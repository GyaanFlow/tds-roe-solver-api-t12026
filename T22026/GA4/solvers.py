from __future__ import annotations

"""
T22026/GA4/solvers.py — Live, deployable API logic for the GA4 questions that are
graded by calling a deployed endpoint (rather than by submitting a precomputed
JSON blob): Q3 grounded-answer, Q4 vector-search + rerank, Q5 GraphRAG.
"""

import hashlib
import json
import logging
import math
import os
import re
import weakref
from collections import OrderedDict, defaultdict, deque
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger("ga4_solvers")

TOKEN_RE = re.compile(r"\b[a-z0-9]+\b")
SENTENCE_SPLIT_RE = re.compile(r"[.!?]\s+")

# ---------------------------------------------------------------------------
# AIPipe LLM client (Q3 grounded QA + Q5 GraphRAG). Q4 needs no LLM.
# ---------------------------------------------------------------------------
AIPIPE_BASE = os.getenv("AIPIPE_BASE_URL", "https://aipipe.org/openai/v1")

# Bounded LRU-ish response cache. This dict is process-global and shared by
# every tenant on the hub, so an unbounded version grows for as long as the
# instance lives -- on Render's 512 MB free plan that ends in an OOM restart
# mid-exam, which looks to students exactly like "the API is down".
_LLM_CACHE: "OrderedDict[str, str]" = OrderedDict()
_LLM_CACHE_MAX = int(os.getenv("LLM_CACHE_MAX", "2000"))


def _cache_put(key: str, value: str) -> None:
    _LLM_CACHE[key] = value
    _LLM_CACHE.move_to_end(key)
    while len(_LLM_CACHE) > _LLM_CACHE_MAX:
        _LLM_CACHE.popitem(last=False)


# Weak-keyed on the loop OBJECT, deliberately not on id(loop): CPython reuses
# the address of a destroyed loop, so an int key silently collides and hands
# back a client belonging to a dead loop. A weak key is the object's own
# identity, and the entry disappears when the loop is collected.
_HTTP_CLIENTS: "weakref.WeakKeyDictionary[Any, Any]" = weakref.WeakKeyDictionary()
_HTTP_CLIENT_NOLOOP = None

# The pool is shared by EVERY tenant on the hub, so it must be sized against
# AGGREGATE demand, not one request's. A single Q9 propose runs at
# Semaphore(32), Q10 at 16, plus Q11 -- so even two or three concurrent
# students exceeded the original 64 and the rest got PoolTimeout and silently
# degraded to safe fallbacks (i.e. lost marks). Sockets are cheap here; the
# expensive thing was the TLS handshake, and keepalive reuse still avoids that.
_MAX_CONNECTIONS = int(os.getenv("HTTP_MAX_CONNECTIONS", "300"))
_MAX_KEEPALIVE = int(os.getenv("HTTP_MAX_KEEPALIVE", "120"))
# Waiting for a free slot must NOT be charged against the caller's read budget.
# httpx.Timeout(8.0) sets connect/read/write/POOL all to 8s, so a queued call
# burned the whole per-call budget waiting and then failed instead of waiting
# briefly and succeeding. Pool wait is now its own, more generous dial.
_POOL_WAIT = float(os.getenv("HTTP_POOL_WAIT", "20"))


def _get_http_client():
    """One pooled httpx client PER EVENT LOOP, created lazily.

    Connection limits are generous enough for a 64-dossier Q9 batch but
    capped so a burst of concurrent students cannot exhaust the instance's
    sockets.

    Keyed per loop, not a bare module global: a pooled client owns keepalive
    connections bound to the loop that created them, so handing one to a
    different loop can fail on a reused connection. Under uvicorn there is a
    single loop for the process lifetime and this is a no-op, but tests and
    any asyncio.run() caller create a fresh loop each time -- and
    `client.is_closed` stays False for a client whose loop is long dead, so it
    cannot be used to detect this."""
    global _HTTP_CLIENT_NOLOOP
    import asyncio

    import httpx

    def _new():
        return httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            limits=httpx.Limits(
                max_connections=_MAX_CONNECTIONS,
                max_keepalive_connections=_MAX_KEEPALIVE,
                keepalive_expiry=60.0,
            ),
        )

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # No running loop (sync caller). Keep a single spare rather than
        # allocating one per call.
        if _HTTP_CLIENT_NOLOOP is None or _HTTP_CLIENT_NOLOOP.is_closed:
            _HTTP_CLIENT_NOLOOP = _new()
        return _HTTP_CLIENT_NOLOOP

    client = _HTTP_CLIENTS.get(loop)
    if client is None or client.is_closed:
        client = _new()
        _HTTP_CLIENTS[loop] = client
    return client


class TokenExpiredError(RuntimeError):
    """Raised when AIPipe responds with 401 or 403, indicating the token is
    expired or invalid. Callers should surface this directly to the user with
    a message to embed a fresh token in the URL."""


def resolve_aipipe_token(request_token: Optional[str] = None, tenant_token: Optional[str] = None) -> Optional[str]:
    """Precedence: explicit request token > stored tenant token > env fallback."""
    return (
        request_token
        or tenant_token
        or os.environ.get("AIPIPE_TOKEN")
        or os.environ.get("AIPIPE_API_KEY")
        or None
    )


def _cache_key(*parts: Any) -> str:
    return hashlib.sha256("||".join(map(str, parts)).encode()).hexdigest()


async def aipipe_chat(
    messages: List[dict],
    token: str,
    model: str = "gpt-4o-mini",
    max_tokens: int = 1000,
    force_json: bool = True,
    timeout: float = 30.0,
    retries: int = 3,
) -> str:
    """Call AIPipe's OpenAI-compatible chat endpoint. Cached + retried."""
    import asyncio

    import httpx

    key = _cache_key("chat", model, force_json, json.dumps(messages, sort_keys=True, default=str))
    if key in _LLM_CACHE:
        return _LLM_CACHE[key]

    body: Dict[str, Any] = {"model": model, "messages": messages, "temperature": 0, "max_tokens": max_tokens}
    if force_json:
        body["response_format"] = {"type": "json_object"}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    last_err = None
    # DEFENSIVE: `retries` is the ATTEMPT COUNT for this loop, so retries=0 would
    # mean range(0) -> the body never runs -> NO HTTP REQUEST IS EVER SENT and we
    # fall straight through to the "failed after 0 retries" raise below. That bug
    # has been introduced twice in this codebase (both times it looked exactly
    # like an exhausted API quota, because every caller silently degraded to its
    # heuristic fallback while the token was perfectly healthy). Clamp to at
    # least one real attempt so a caller passing retries=0 meaning "don't retry"
    # still gets the single call it obviously intended.
    attempts = max(1, int(retries or 0))
    # Reuse ONE pooled client for the whole process instead of opening a new
    # AsyncClient (= new TCP + TLS handshake) per call. A single Q9 propose
    # makes 64 of these and a Q10 send makes 12; multiplied by every student
    # hitting the shared hub at once, the TLS handshakes alone saturate the
    # 0.1-CPU Render instance and exhaust ephemeral sockets -- which surfaced
    # as `network error: ` with an EMPTY message (httpx ConnectError) and as
    # unrelated requests dying with ClientDisconnect while the loop was busy.
    client = _get_http_client()
    for attempt in range(attempts):
        try:
            r = await client.post(
                f"{AIPIPE_BASE}/chat/completions",
                headers=headers,
                json=body,
                # Per-phase, NOT a single scalar: httpx.Timeout(8.0) would set
                # the pool-acquire wait to 8s too, so a call queued behind a
                # busy pool failed rather than waiting its turn. read/write
                # keep the caller's tight budget; pool gets its own.
                timeout=httpx.Timeout(
                    connect=min(timeout, 10.0),
                    read=timeout,
                    write=timeout,
                    pool=_POOL_WAIT,
                ),
            )
        except httpx.RequestError as exc:
            # repr, not str: httpx ConnectError/PoolTimeout often stringify to
            # "" and the log line then reads "network error: " with no cause.
            last_err = f"network error: {exc!r}"
            await asyncio.sleep(1.0 * (attempt + 1))
            continue
        # 401/403 → token is expired or invalid; retrying won't help.
        if r.status_code in (401, 403):
            raise TokenExpiredError(
                "AIPipe token is expired or invalid (HTTP " + str(r.status_code) + "). "
                "Embed a fresh token in the URL path: /ga5/<email>/<NEW_TOKEN>/... "
                "You can get a new token from https://aipipe.org"
            )
        if r.status_code in (429, 500, 502, 503, 504):
            last_err = f"HTTP {r.status_code}: {r.text[:160]}"
            await asyncio.sleep(1.2 * (attempt + 1))
            continue
        r.raise_for_status()
        out = r.json()["choices"][0]["message"]["content"]
        _cache_put(key, out)
        return out
    raise RuntimeError(f"AIPipe chat failed after {attempts} attempt(s): {last_err}")


def parse_json_block(s: str) -> dict:
    """Robustly parse a JSON object out of an LLM response (handles code fences)."""
    s = (s or "").strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-z]*\n?|\n?```$", "", s).strip()
    try:
        return json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, re.DOTALL)
        return json.loads(m.group(0)) if m else {}


# ---------------------------------------------------------------------------
# Generic helpers
# ---------------------------------------------------------------------------
def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(str(text or "").lower())


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def sentences_of(text: str, min_len: int = 0) -> List[str]:
    parts = [p.strip() for p in SENTENCE_SPLIT_RE.split(str(text or "")) if p.strip()]
    if min_len:
        parts = [p for p in parts if len(p) > min_len]
    return parts


# ---------------------------------------------------------------------------
# Q3: Anti-Hallucination Grounded Answer API (live endpoint logic)
# ---------------------------------------------------------------------------
def grounded_answer(question: str, chunks: List[Dict[str, str]]) -> Dict[str, Any]:
    q_tokens = set(tokenize(question))
    q_tokens -= {"what", "when", "where", "which", "who", "how", "does", "is", "are", "the", "a", "an", "of", "in"}

    best_chunk = None
    best_overlap = 0.0
    scored: List[tuple] = []
    for c in chunks:
        c_tokens = set(tokenize(c.get("text", "")))
        if not q_tokens:
            overlap = 0.0
        else:
            overlap = len(q_tokens & c_tokens) / len(q_tokens)
        scored.append((c, overlap))
        if overlap > best_overlap:
            best_overlap = overlap
            best_chunk = c

    if best_chunk is None or best_overlap < 0.2:
        return {"answer": "I don't know", "citations": [], "confidence": 0.1, "answerable": False}

    supporting = [c for c, ov in scored if ov >= max(0.2, best_overlap * 0.6)]
    citations = [c["chunk_id"] for c in supporting][:3]
    answer_text = best_chunk.get("text", "").strip()
    confidence = round(min(0.99, 0.5 + best_overlap * 0.5), 2)
    return {"answer": answer_text, "citations": citations, "confidence": confidence, "answerable": True}


# ---------------------------------------------------------------------------
# Q4: Two-stage Vector Search + Re-ranking (live endpoint logic)
# ---------------------------------------------------------------------------
def _matches_filter(doc: Dict[str, Any], filt: Dict[str, Any]) -> bool:
    for field, condition in (filt or {}).items():
        value = doc.get(field)
        if isinstance(condition, dict):
            if "gte" in condition and not (value is not None and value >= condition["gte"]):
                return False
            if "lte" in condition and not (value is not None and value <= condition["lte"]):
                return False
            if "in" in condition and value not in condition["in"]:
                return False
        else:
            if value != condition:
                return False
    return True


def vector_search_rerank(
    payload: Dict[str, Any],
    documents: List[Dict[str, Any]],
    embeddings: Dict[str, List[float]],
    reranker_scores: Dict[str, Dict[str, float]],
) -> Dict[str, List[str]]:
    filt = payload.get("filter", {})
    top_k = int(payload.get("top_k", 10))
    rerank_top_n = int(payload.get("rerank_top_n", 3))
    query_vector = payload.get("query_vector", [])
    query_id = payload.get("query_id")

    filtered = [d for d in documents if _matches_filter(d, filt)]
    scored = [(d["doc_id"], cosine(query_vector, embeddings.get(d["doc_id"], []))) for d in filtered]
    scored.sort(key=lambda p: (-p[1], p[0]))
    stage1 = [doc_id for doc_id, _ in scored[:top_k]]

    lookup = reranker_scores.get(query_id, {}) if query_id else {}
    # Missing rerank score sinks the doc to the bottom (matches reference -999.0).
    reranked = sorted(stage1, key=lambda doc_id: (-lookup.get(doc_id, -999.0), doc_id))
    return {"matches": reranked[:rerank_top_n]}


# ---------------------------------------------------------------------------
# Q5: GraphRAG Pipeline (live endpoint logic) — Extract / Query / Summarize
# ---------------------------------------------------------------------------
# Proper-noun phrases: runs of capitalized words, no sentence-final periods.
_PROPER_NOUN_RE = re.compile(r"\b[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*\b")

# (regex over a single sentence, relation label). Group 1 = subject, group 2 = object,
# both restricted to proper-noun phrases so matches never bleed across punctuation.
_NP = r"([A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*)*)"
_REL_PATTERNS = [
    (re.compile(_NP + r"\s+was\s+(?:created|founded|developed)\s+by\s+" + _NP), "CREATED_BY"),
    (re.compile(_NP + r"\s+(?:created|founded|developed)\s+" + _NP), "CREATED"),
    (re.compile(_NP + r"\s+(?:integrates|integrated)\s+(?:with|into)\s+" + _NP), "INTEGRATED_INTO"),
    (re.compile(_NP + r"\s+hired\s+" + _NP), "HIRED"),
    (re.compile(_NP + r"\s+(?:wrote|authored)\s+" + _NP), "AUTHORED"),
]


def _guess_entity_type(name: str) -> str:
    lowered = name.lower()
    if any(kw in lowered for kw in ("inc", "corp", "labs", "research", "ai", "systems", "technologies")):
        return "Organization"
    return "Entity"


def extract_graph(text: str) -> Dict[str, Any]:
    entities: Dict[str, str] = {}
    relationships: List[Dict[str, str]] = []

    for sentence in sentences_of(text):
        for name in _PROPER_NOUN_RE.findall(sentence):
            name = name.strip()
            if len(name) < 2 or name in entities:
                continue
            entities[name] = _guess_entity_type(name)

        for pattern, relation in _REL_PATTERNS:
            for match in pattern.finditer(sentence):
                a, b = match.group(1).strip(), match.group(2).strip()
                if a == b:
                    continue
                if relation == "CREATED_BY":
                    source, target = b, a
                else:
                    source, target = a, b
                relationships.append({"source": source, "target": target, "relation": relation})
                entities.setdefault(source, _guess_entity_type(source))
                entities.setdefault(target, _guess_entity_type(target))

    return {
        "entities": [{"name": n, "type": t} for n, t in entities.items()],
        "relationships": relationships,
    }


def graph_query(question: str, graph: Dict[str, Any]) -> Dict[str, Any]:
    """Best-effort multi-hop BFS. The graph edges are directed, but natural-language
    questions ("who created X", "what integrates with Y") don't reliably signal
    direction, so we walk the graph as undirected and return the farthest node
    reached from whichever mentioned entity is named the earliest/most specifically
    in the question text."""
    relationships = graph.get("relationships", [])
    adjacency: Dict[str, List[str]] = defaultdict(list)
    for rel in relationships:
        adjacency[rel["source"]].append(rel["target"])
        adjacency[rel["target"]].append(rel["source"])

    all_entities = {e["name"] for e in graph.get("entities", [])} | set(adjacency.keys())
    q_tokens = set(tokenize(question))

    # Prefer the longest entity name whose tokens are a full subset of the
    # question tokens (longer names are more specific / less ambiguous).
    start = None
    for name in sorted(all_entities, key=len, reverse=True):
        name_tokens = set(tokenize(name))
        if name_tokens and name_tokens.issubset(q_tokens):
            start = name
            break
    if start is None:
        for name in all_entities:
            if set(tokenize(name)) & q_tokens:
                start = name
                break

    if start is None:
        return {"answer": "unknown", "reasoning_path": [], "hops": 0}

    visited = {start}
    queue = deque([(start, [start])])
    best_path: List[str] = [start]
    while queue:
        node, path = queue.popleft()
        for nxt in adjacency.get(node, []):
            if nxt in visited:
                continue
            visited.add(nxt)
            new_path = path + [nxt]
            best_path = new_path
            queue.append((nxt, new_path))

    answer = best_path[-1] if len(best_path) > 1 else "unknown"
    hops = max(len(best_path) - 1, 0)
    return {"answer": answer, "reasoning_path": best_path, "hops": hops}


def community_summary(community_id: str, entities: List[str], relationships: List[Dict[str, str]]) -> Dict[str, str]:
    if not entities:
        return {"community_id": community_id, "summary": "No entities found in this community."}
    rel_sentences = [
        f"{r['source']} {r['relation'].replace('_', ' ').lower()} {r['target']}" for r in relationships
    ]
    body = "; ".join(rel_sentences) if rel_sentences else f"a group of related entities: {', '.join(entities)}"
    summary = f"This community centers around {entities[0]}. It involves {body}."
    return {"community_id": community_id, "summary": summary}


# ===========================================================================
# LLM-backed implementations (preferred when an AIPipe token is available).
# These match the exam grader's expectations far better than the regex/heuristic
# versions above, which remain as offline fallbacks when no token is configured.
# ===========================================================================
async def grounded_answer_llm(question: str, chunks: List[Dict[str, str]], token: str) -> Dict[str, Any]:
    prompt = (
        "You are a highly reliable Grounded QA API for medical and legal compliance.\n"
        "Answer the user's question strictly using ONLY the provided context chunks.\n"
        "1. If the question CANNOT be answered from the chunks, return:\n"
        '   answerable: false, answer: "I don\'t know" (exact match), citations: [], confidence: 0.1\n'
        "2. If it CAN be answered, return:\n"
        "   answerable: true, answer: <grounded answer>, citations: [<ONLY the chunk_ids you used>],\n"
        "   confidence: <float 0.8-1.0>\n"
        "NEVER use outside knowledge. Return strictly JSON with exactly these 4 keys.\n\n"
        f"QUESTION:\n{question}\n\nCHUNKS:\n{json.dumps(chunks, indent=2)}"
    )
    out = parse_json_block(await aipipe_chat([{"role": "user", "content": prompt}], token, model="gpt-4o-mini", max_tokens=1000))
    if not out.get("answerable", False) or float(out.get("confidence", 1.0)) <= 0.3:
        return {"answer": "I don't know", "citations": [], "confidence": 0.1, "answerable": False}
    valid_ids = {c.get("chunk_id") for c in chunks if isinstance(c, dict)}
    cites = [c for c in out.get("citations", []) if c in valid_ids]
    return {
        "answer": out.get("answer", "I don't know"),
        "citations": cites,
        "confidence": float(out.get("confidence", 0.9)),
        "answerable": True,
    }


async def extract_graph_llm(text: str, token: str) -> Dict[str, Any]:
    prompt = (
        "You are an expert GraphRAG Entity and Relationship extractor.\n"
        "Extract entities and relationships from the provided text according to these EXACT rules:\n"
        "Allowed Entity Types: Person, Organization, Product, Framework\n"
        "Allowed Relationship Types: FOUNDED, DEVELOPED, INTEGRATED_INTO, HIRED, AUTHORED\n\n"
        "Return strictly JSON in this format:\n"
        '{"entities": [{"name": "Entity Name", "type": "AllowedType"}], '
        '"relationships": [{"source": "Entity1", "target": "Entity2", "relation": "ALLOWED_RELATION"}]}\n\n'
        f"TEXT:\n{text}"
    )
    out = parse_json_block(await aipipe_chat([{"role": "user", "content": prompt}], token, model="gpt-4o", max_tokens=1500))
    return {"entities": out.get("entities", []), "relationships": out.get("relationships", [])}


async def graph_query_llm(question: str, graph: Dict[str, Any], token: str) -> Dict[str, Any]:
    prompt = (
        "You are a GraphRAG multi-hop reasoning agent.\n"
        "Given the knowledge graph (entities and relationships), answer the natural language question.\n"
        "Determine the logical path through the graph to find the answer.\n"
        "Return strictly JSON in this format:\n"
        '{"answer": "Brief factual answer", "reasoning_path": ["Entity1", "Entity2", "Entity3"], "hops": 2}\n\n'
        f"QUESTION:\n{question}\n\nGRAPH:\n{json.dumps(graph, indent=2)}"
    )
    out = parse_json_block(await aipipe_chat([{"role": "user", "content": prompt}], token, model="gpt-4o", max_tokens=1500))
    path = out.get("reasoning_path", []) or []
    return {"answer": out.get("answer", ""), "reasoning_path": path, "hops": len(path) - 1 if path else 0}


async def community_summary_llm(community_id: str, entities: List[Any], relationships: List[dict], token: str) -> Dict[str, str]:
    prompt = (
        "You are a GraphRAG community summarizer. Summarize the following community of entities and relationships.\n"
        "The summary should be a concise paragraph explaining how these entities are connected and their overall theme.\n"
        "Return strictly JSON in this format:\n"
        f'{{"community_id": "{community_id}", "summary": "Your summary here."}}\n\n'
        f"ENTITIES:\n{json.dumps(entities, indent=2)}\n\nRELATIONSHIPS:\n{json.dumps(relationships, indent=2)}"
    )
    out = parse_json_block(await aipipe_chat([{"role": "user", "content": prompt}], token, model="gpt-4o", max_tokens=1500))
    return {"community_id": community_id, "summary": out.get("summary", "")}


# ---------------------------------------------------------------------------
# Q4: in-memory dataset variant. The grader posts only the query; the corpus is
# generated per-email (see q4data.py). Inline documents/embeddings (if supplied,
# e.g. from the dashboard tester) take precedence over the generated corpus.
# ---------------------------------------------------------------------------
def vector_search_from_dataset(payload: Dict[str, Any], email: str) -> Dict[str, List[str]]:
    from T22026.GA4.q4data import get_q4_dataset

    documents, embeddings, reranker_scores = get_q4_dataset(email)
    return vector_search_rerank(payload, documents, embeddings, reranker_scores)
