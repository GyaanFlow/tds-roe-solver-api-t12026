import json
import logging
import time
from typing import Any, Awaitable, Callable, Dict, List, TypeVar

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from T22026.GA4.shared.tenant import (
    build_ready_routes,
    build_solver_url_prefix,
    current_email,
    get_tenant_config,
    normalize_email,
    set_tenant_config,
)
from T22026.GA4.solvers import (
    community_summary,
    extract_graph,
    graph_query,
    grounded_answer,
    vector_search_rerank,
)

logger = logging.getLogger("ga4_router")
router = APIRouter()
T = TypeVar("T")


MAX_BODY_BYTES = 2_000_000  # 2 MB — generous for exam-sized payloads, guards against abuse


async def _read_json_body(request: Request) -> Dict[str, Any]:
    """Parse JSON body from a request regardless of Content-Type header."""
    try:
        raw = await request.body()
        if not raw:
            raise ValueError("Empty request body")
        if len(raw) > MAX_BODY_BYTES:
            raise ValueError(f"Request body too large (max {MAX_BODY_BYTES} bytes)")
        body = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON body: {exc}") from exc
    if not isinstance(body, dict):
        raise ValueError("JSON body must be an object")
    return body


def _as_dict(value: Any, field: str) -> Dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"'{field}' must be a JSON object")
    return value


def _as_list(value: Any, field: str) -> List[Any]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"'{field}' must be a JSON array")
    return value


def _as_str(value: Any) -> str:
    return "" if value is None else str(value)


async def _run_solver(handler: Callable[[], Awaitable[T]], label: str) -> T | JSONResponse:
    email = current_email.get()
    start = time.time()
    try:
        result = await handler()
        elapsed = time.time() - start
        logger.info("GA4 %s by %s completed in %.2fs", label, email, elapsed)
        return result
    except (RuntimeError, ValueError, KeyError) as exc:
        elapsed = time.time() - start
        logger.warning("GA4 %s client error for %s after %.2fs: %s", label, email, elapsed, exc)
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception:
        elapsed = time.time() - start
        logger.exception("GA4 %s failed for %s after %.2fs", label, email, elapsed)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ---------------------------------------------------------------------------
# Q3: live Grounded Answer API — submit this hub's own URL as the answer.
# ---------------------------------------------------------------------------
@router.post("/grounded-answer")
@router.post("/q3/grounded-answer")
@router.post("/q3")
async def grounded_answer_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        question = _as_str(body.get("question"))
        chunks = _as_list(body.get("chunks"), "chunks")
        for c in chunks:
            if not isinstance(c, dict) or "chunk_id" not in c:
                raise ValueError("each item in 'chunks' must be an object with a 'chunk_id'")
        return grounded_answer(question, chunks)
    return await _run_solver(_handle, "Q3")


# ---------------------------------------------------------------------------
# Q4: live Vector Search + Re-ranking API.
# The grader posts documents/embeddings/reranker_scores inline with each
# query so the endpoint is stateless across requests.
# ---------------------------------------------------------------------------
@router.post("/vector-search")
@router.post("/q4/vector-search")
@router.post("/q4")
async def vector_search_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        documents = _as_list(body.get("documents"), "documents")
        embeddings = _as_dict(body.get("embeddings"), "embeddings")
        reranker_scores = _as_dict(body.get("reranker_scores"), "reranker_scores")
        if not documents or not embeddings:
            raise ValueError("'documents' and 'embeddings' are required")
        for d in documents:
            if not isinstance(d, dict) or "doc_id" not in d:
                raise ValueError("each item in 'documents' must be an object with a 'doc_id'")
        query_vector = body.get("query_vector")
        if not isinstance(query_vector, list):
            raise ValueError("'query_vector' must be a numeric array")
        return vector_search_rerank(body, documents, embeddings, reranker_scores)
    return await _run_solver(_handle, "Q4")


# ---------------------------------------------------------------------------
# Q5: live GraphRAG pipeline (3 sub-endpoints).
# ---------------------------------------------------------------------------
MAX_EXTRACT_TEXT_CHARS = 20_000


@router.post("/extract-graph")
@router.post("/q5/extract-graph")
async def extract_graph_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        text = _as_str(body.get("text"))
        if len(text) > MAX_EXTRACT_TEXT_CHARS:
            raise ValueError(f"'text' too long (max {MAX_EXTRACT_TEXT_CHARS} chars)")
        return extract_graph(text)
    return await _run_solver(_handle, "Q5/extract-graph")


@router.post("/graph-query")
@router.post("/q5/graph-query")
async def graph_query_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        question = _as_str(body.get("question"))
        graph = _as_dict(body.get("graph"), "graph")
        graph["entities"] = _as_list(graph.get("entities"), "graph.entities")
        graph["relationships"] = _as_list(graph.get("relationships"), "graph.relationships")
        return graph_query(question, graph)
    return await _run_solver(_handle, "Q5/graph-query")


@router.post("/community-summary")
@router.post("/q5/community-summary")
async def community_summary_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        community_id = _as_str(body.get("community_id"))
        entities = _as_list(body.get("entities"), "entities")
        relationships = _as_list(body.get("relationships"), "relationships")
        for r in relationships:
            if not isinstance(r, dict) or not {"source", "target", "relation"} <= r.keys():
                raise ValueError("each item in 'relationships' must have 'source', 'target', 'relation'")
        return community_summary(community_id, entities, relationships)
    return await _run_solver(_handle, "Q5/community-summary")


# ---------------------------------------------------------------------------
# Config & Tenant Management (mirrors GA3)
# ---------------------------------------------------------------------------
class OnboardRequest(BaseModel):
    email: str
    aipipe_token: str | None = None


class OnboardResponse(BaseModel):
    email: str
    configured: bool
    has_token: bool
    base_url: str
    solver_url_prefix: str
    ready_routes: List[str]
    session_id: str | None = None


class ConfigSaveRequest(BaseModel):
    aipipe_token: str | None = None


class TenantStatusResponse(BaseModel):
    email: str
    configured: bool
    has_token: bool
    solver_url_prefix: str
    ready_routes: List[str]


@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "ga4", "timestamp": time.time()}


@router.post("/config")
async def save_config(req: ConfigSaveRequest):
    email = current_email.get()
    if req.aipipe_token is not None:
        set_tenant_config(email, {"aipipe_token": req.aipipe_token})
    cfg = get_tenant_config(email)
    return {"status": "ok", "message": f"Configuration saved for {email}", "has_token": bool(cfg.get("aipipe_token"))}


@router.get("/status", response_model=TenantStatusResponse)
async def tenant_status(request: Request):
    email = normalize_email(current_email.get())
    base = str(request.base_url).rstrip("/")
    cfg = get_tenant_config(email)
    return TenantStatusResponse(
        email=email,
        configured=True,
        has_token=bool(cfg.get("aipipe_token")),
        solver_url_prefix=build_solver_url_prefix(base, email),
        ready_routes=build_ready_routes(base, email),
    )


@router.post("/onboard", response_model=OnboardResponse)
async def onboard(req: OnboardRequest, request: Request):
    email = normalize_email(req.email)
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    session_id = None
    if req.aipipe_token:
        from T22026.GA4.shared.tenant import create_ga4_session
        session_id = create_ga4_session(email, req.aipipe_token)
        set_tenant_config(email, {"aipipe_token": req.aipipe_token})
    base = str(request.base_url).rstrip("/")
    cfg = get_tenant_config(email)
    return OnboardResponse(
        email=email,
        configured=True,
        has_token=bool(cfg.get("aipipe_token")),
        base_url=base,
        solver_url_prefix=build_solver_url_prefix(base, email),
        ready_routes=build_ready_routes(base, email),
        session_id=session_id,
    )
