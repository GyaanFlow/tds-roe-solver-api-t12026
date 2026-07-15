from __future__ import annotations

"""
T22026/GA4/solvers.py — Live, deployable API logic for the GA4 questions that are
graded by calling a deployed endpoint (rather than by submitting a precomputed
JSON blob): Q3 grounded-answer, Q4 vector-search + rerank, Q5 GraphRAG.
"""

import math
import re
from collections import defaultdict, deque
from typing import Any, Dict, List, Sequence

TOKEN_RE = re.compile(r"\b[a-z0-9]+\b")
SENTENCE_SPLIT_RE = re.compile(r"[.!?]\s+")


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
    reranked = sorted(stage1, key=lambda doc_id: (-lookup.get(doc_id, 0.0), doc_id))
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
