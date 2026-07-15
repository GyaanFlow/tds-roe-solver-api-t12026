# GA4 Live API — Integration Spec

Fixed request/response contract for the **3 GA4 questions that require a live, deployed API URL**
(Q3 grounded-answer, Q4 vector-search + rerank, Q5 GraphRAG). The other 9 GA4 questions are pure
client-side computation and are **not** served here — implement those in your own solver.

This contract is **stable and additive-only**. Code your other solver against it directly.

---

## 1. Conventions (identical to GA2/GA3)

- **Base tenant URL:** `https://<host>/ga4/<url-encoded-email>`
  - e.g. `https://<host>/ga4/23f1000805%40ds.study.iitm.ac.in`
  - The `<host>` is your Render or Hugging Face Space origin. Both behave identically.
- **Method:** every functional endpoint is `POST` with `Content-Type: application/json`.
- **No auth / no token needed.** These 3 questions are pure algorithms — unlike GA3, there is no
  AI Pipe token or per-tenant config required. Any email works immediately and independently.
- **CORS:** open (`Access-Control-Allow-Origin: *`); preflight `OPTIONS` returns `200`.
- **Multi-tenant:** the `<email>` segment isolates callers but does not change behavior — the same
  input yields the same output for every email.

### Discovering routes programmatically
`POST /ga4/onboard` with `{"email": "..."}` returns the ready-to-use route list:

```json
{
  "email": "me@x.com",
  "configured": true,
  "has_token": false,
  "base_url": "https://<host>",
  "solver_url_prefix": "https://<host>/ga4/me%40x.com",
  "ready_routes": [
    "https://<host>/ga4/me%40x.com/grounded-answer",
    "https://<host>/ga4/me%40x.com/vector-search",
    "https://<host>/ga4/me%40x.com/extract-graph",
    "https://<host>/ga4/me%40x.com/graph-query",
    "https://<host>/ga4/me%40x.com/community-summary"
  ],
  "session_id": null
}
```

This response schema is **byte-identical to GA3's** `/onboard`, so existing GA3 integration code
parses it unchanged. `GET /ga4/<email>/status` returns the same shape minus `base_url`/`session_id`.
`GET /ga4/<email>/health` → `{"status":"ok","service":"ga4","timestamp":<float>}`.

### Error contract (all endpoints)
- **400** — malformed input (bad/empty JSON, wrong types, missing required nested keys):
  `{"error": "<human-readable reason>"}`
- **500** — unexpected server error: `{"error": "Internal server error"}` (should not occur for valid input)
- **413-equivalent** — request body over **2 MB** → `400 {"error": "Request body too large (max 2000000 bytes)"}`

---

## 2. Q3 — Grounded Answer API

Answers strictly from the provided chunks, cites source chunk IDs, and refuses when unanswerable.

**Route:** `POST /ga4/<email>/grounded-answer`
(aliases: `/ga4/<email>/q3/grounded-answer`, `/ga4/<email>/q3`)

### Request
```json
{
  "question": "What year was FAISS released?",
  "chunks": [
    {"chunk_id": "C1", "text": "FAISS was developed by Facebook AI Research and open-sourced in 2017."},
    {"chunk_id": "C2", "text": "Qdrant is a vector database written in Rust, released in 2021."}
  ]
}
```
- `question` — string (required; coerced, `null` → `""`).
- `chunks` — array of objects; **each must have `chunk_id`** (and normally `text`). A non-object item
  or a missing `chunk_id` → `400`.

### Response (answerable)
```json
{ "answer": "FAISS was developed by Facebook AI Research and open-sourced in 2017.",
  "citations": ["C1"], "confidence": 0.75, "answerable": true }
```

### Response (unanswerable)
```json
{ "answer": "I don't know", "citations": [], "confidence": 0.1, "answerable": false }
```

| Field | Type | Notes |
|-------|------|-------|
| `answer` | string | Best-matching chunk text, or exactly `"I don't know"` when unanswerable |
| `citations` | string[] | Subset of the provided `chunk_id`s (≤ 3). Empty when unanswerable. Never hallucinated |
| `confidence` | float | `0.5–0.99` when answerable; `≤ 0.3` (currently `0.1`) when not |
| `answerable` | bool | `false` ⇒ answer is `"I don't know"` and citations `[]` |

---

## 3. Q4 — Vector Search + Re-ranking API

Two-stage retrieval: metadata filter → cosine top-k → re-rank via a lookup table.

**Route:** `POST /ga4/<email>/vector-search`
(aliases: `/ga4/<email>/q4/vector-search`, `/ga4/<email>/q4`)

> **Stateless design:** the corpus (`documents`, `embeddings`, `reranker_scores`) is sent **inline
> with every request**, so the endpoint holds no server-side dataset. Post the parsed contents of the
> question's ZIP alongside each query.

### Request
```json
{
  "query_id": "Q001",
  "query_vector": [0.9, 0.1],
  "top_k": 3,
  "rerank_top_n": 2,
  "filter": {
    "department": "finance",
    "year": {"gte": 2023},
    "region": {"in": ["north_america", "europe"]}
  },
  "documents": [
    {"doc_id": "D1", "department": "finance", "year": 2024},
    {"doc_id": "D2", "department": "finance", "year": 2023},
    {"doc_id": "D3", "department": "hr", "year": 2024}
  ],
  "embeddings": {"D1": [1, 0], "D2": [0.9, 0.1], "D3": [1, 0]},
  "reranker_scores": {"Q001": {"D1": 0.5, "D2": 0.9}}
}
```

| Field | Type | Notes |
|-------|------|-------|
| `query_id` | string | Key into `reranker_scores` |
| `query_vector` | number[] | **Required**, must be an array |
| `top_k` | int | Stage-1 candidates kept after cosine (default 10) |
| `rerank_top_n` | int | Final results returned after re-rank (default 3) |
| `filter` | object | Optional. Supports exact match, `{"gte":n}`, `{"lte":n}`, `{"in":[...]}` |
| `documents` | object[] | **Required**, each needs `doc_id` |
| `embeddings` | object | **Required**, `doc_id → number[]` |
| `reranker_scores` | object | `query_id → {doc_id → score}` (optional; missing → score 0) |

**Filter operators:** exact (`{"department":"finance"}`), `gte`, `lte`, `in`. Tie-break in both stages
is by **lexicographically smaller `doc_id`**.

### Response
```json
{ "matches": ["D2", "D1"] }
```
- `matches` — up to `rerank_top_n` `doc_id`s, in final re-ranked order.

---

## 4. Q5 — GraphRAG Pipeline (3 sub-endpoints)

The grader calls three separate endpoints under the same base URL.

### 4a. `POST /ga4/<email>/extract-graph`  (alias `/q5/extract-graph`)
Extract entities and relationships from raw text (regex-based, sentence-scoped, no LLM).

**Request**
```json
{ "chunk_id": "C001", "text": "LangChain was created by Harrison Chase. LangChain integrates with OpenAI." }
```
- `text` — string (required). Capped at **20,000 chars** → over that returns `400`.

**Response**
```json
{
  "entities": [
    {"name": "LangChain", "type": "Organization"},
    {"name": "Harrison Chase", "type": "Entity"},
    {"name": "OpenAI", "type": "Organization"}
  ],
  "relationships": [
    {"source": "Harrison Chase", "target": "LangChain", "relation": "CREATED_BY"},
    {"source": "LangChain", "target": "OpenAI", "relation": "INTEGRATED_INTO"}
  ]
}
```
- `entities[].type` ∈ `{"Organization","Entity"}` (heuristic).
- `relationships[].relation` ∈ `{CREATED, CREATED_BY, INTEGRATED_INTO, HIRED, AUTHORED}`.

### 4b. `POST /ga4/<email>/graph-query`  (alias `/q5/graph-query`)
Multi-hop reasoning over a supplied graph.

**Request**
```json
{
  "question": "Who created the framework that integrates with OpenAI?",
  "graph": {
    "entities": [ ... ],
    "relationships": [ {"source": "...", "target": "...", "relation": "..."} ]
  }
}
```
- `graph` — object; `entities`/`relationships` default to `[]` if omitted (never `null`-crashes).

**Response**
```json
{ "answer": "Harrison Chase", "reasoning_path": ["OpenAI", "LangChain", "Harrison Chase"], "hops": 2 }
```
- `answer` — string (`"unknown"` if no path found).
- `reasoning_path` — ordered node names traversed.
- `hops` — `len(reasoning_path) - 1`.

> Note: traversal is **undirected BFS** (edge direction in NL questions is ambiguous), returning the
> farthest node from the most-specific entity named in the question. Verify against the grader's
> expected direction for edge cases.

### 4c. `POST /ga4/<email>/community-summary`  (alias `/q5/community-summary`)
Summarize a connected sub-community.

**Request**
```json
{
  "community_id": "COM_001",
  "entities": ["LangChain", "Harrison Chase"],
  "relationships": [ {"source": "Harrison Chase", "target": "LangChain", "relation": "CREATED_BY"} ]
}
```
- Each `relationships` item must have `source`, `target`, `relation` → else `400`.

**Response**
```json
{ "community_id": "COM_001",
  "summary": "This community centers around LangChain. It involves Harrison Chase created by LangChain; ..." }
```

---

## 5. Quick client snippet

```python
import requests
from urllib.parse import quote

HOST = "https://<your-host>"
EMAIL = "you@example.com"
base = f"{HOST}/ga4/{quote(EMAIL, safe='')}"

# Q3
r = requests.post(f"{base}/grounded-answer", json={
    "question": "What year was FAISS released?",
    "chunks": [{"chunk_id": "C1", "text": "FAISS was open-sourced in 2017."}],
}, timeout=10)
print(r.json())   # {"answer": "...", "citations": ["C1"], "confidence": 0.75, "answerable": true}
```

For the exam itself, submit the **tenant URL** for each question as the answer
(e.g. `https://<host>/ga4/<email>/grounded-answer`) — the grader calls it directly.

---

## 6. Stability guarantee

- All routes, request fields, and response fields above are **fixed**. Future changes will be
  additive (new optional fields / new routes), never renames or removals.
- GA4 shares GA2/GA3's `/onboard`, `/status`, `/config`, `/health` schema, so a single integration
  layer handles all three hubs. Point your existing GA3 client code at `/ga4/...` unchanged.
