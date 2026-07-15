import json
import logging
import time
from typing import Any, Awaitable, Callable, Dict, List, TypeVar

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from T22026.GA3.shared.tenant import (
    build_ready_routes,
    build_solver_url_prefix,
    current_email,
    get_tenant_config,
    normalize_email,
    set_tenant_config,
)
from T22026.GA3.solvers import (
    solve_context_window_heist,
    solve_cosine_similarity,
    solve_cot_math,
    solve_dynamic_extract,
    solve_embedding_trapdoors,
    solve_invoice_extract,
    solve_korean_audio,
    solve_multimodal_qa,
    solve_proof_of_work,
    solve_semantic_rank,
    solve_spin_up_cli,
    solve_structured_extraction,
    solve_youtube_filter,
    get_q6_debug_info,
    clear_q6_debug_info,
)

logger = logging.getLogger("ga3_router")
router = APIRouter()
T = TypeVar("T")


async def _read_json_body(request: Request) -> Dict[str, Any]:
    """Parse JSON body from a request regardless of Content-Type header."""
    try:
        raw = await request.body()
        if not raw:
            raise ValueError("Empty request body")
        body = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON body: {exc}") from exc
    if not isinstance(body, dict):
        raise ValueError("JSON body must be an object")
    return body


async def _run_solver(handler: Callable[[], Awaitable[T]], label: str) -> T | JSONResponse:
    email = current_email.get()
    start = time.time()
    try:
        result = await handler()
        elapsed = time.time() - start
        logger.info("GA3 %s by %s completed in %.2fs", label, email, elapsed)
        return result
    except (RuntimeError, ValueError) as exc:
        elapsed = time.time() - start
        logger.warning("GA3 %s client error for %s after %.2fs: %s", label, email, elapsed, exc)
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        elapsed = time.time() - start
        logger.exception("GA3 %s failed for %s after %.2fs", label, email, elapsed)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ---------------------------------------------------------------------------
# Q2: Multimodal Image QA
# ---------------------------------------------------------------------------
@router.post("/q2/answer-image")
@router.post("/answer-image")
@router.post("/q2")
async def answer_image(request: Request):
    async def _handle():
        # Accept JSON body, form data, or raw bytes
        body = {}
        raw = await request.body()
        ctype = request.headers.get("content-type", "").lower()
        if raw:
            if "application/json" in ctype or raw[:1] in (b"{", b"["):
                try:
                    body = json.loads(raw)
                except Exception:
                    pass
            elif "multipart/form-data" in ctype or "application/x-www-form-urlencoded" in ctype:
                try:
                    form = await request.form()
                    body = dict(form)
                except Exception:
                    pass
        # Fall back to query params if body is empty
        if not body:
            body = dict(request.query_params)
        image_b64 = body.get("image_base64") or body.get("image") or body.get("img") or ""
        question = body.get("question") or body.get("q") or ""
        if not image_b64:
            raise ValueError("'image_base64' field is required")
        if not question:
            raise ValueError("'question' field is required")
        email = current_email.get()
        logger.info("Q2 multimodal QA for %s, question=%.80s", email, question)
        ans = await solve_multimodal_qa(str(image_b64), str(question))
        return {"answer": str(ans)}
    return await _run_solver(_handle, "Q2")


# ---------------------------------------------------------------------------
# Q3 & Q7: Invoice Extraction (shared /extract route)
# ---------------------------------------------------------------------------
@router.post("/q3/extract")
@router.post("/extract")
@router.post("/q3")
@router.post("/q7/extract")
@router.post("/q7")
async def extract(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        if "invoice_text" in body:
            logger.info("Q3 fixed extract for %s", current_email.get())
            return await solve_invoice_extract(body["invoice_text"])
        else:
            logger.info("Q7 structured extraction for %s", current_email.get())
            return await solve_structured_extraction(body)
    return await _run_solver(_handle, "Q3/Q7")


# ---------------------------------------------------------------------------
# Q4: Dynamic Schema Extraction
# -- Uses raw body parsing to avoid Pydantic alias issues with "schema" key
# ---------------------------------------------------------------------------
@router.post("/q4/dynamic-extract")
@router.post("/dynamic-extract")
@router.post("/q4")
async def dynamic_extract(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        text = body.get("text", "")
        schema = body.get("schema", body.get("schema_def", {}))
        if not isinstance(schema, dict) or not schema:
            raise ValueError("'schema' must be a non-empty JSON object")
        logger.info("Q4 dynamic extract for %s, keys=%s", current_email.get(), list(schema.keys()))
        return await solve_dynamic_extract(text, schema)
    return await _run_solver(_handle, "Q4")


# ---------------------------------------------------------------------------
# Q6: Korean Audio Dataset API
# ---------------------------------------------------------------------------
@router.post("/q6/answer-audio")
@router.post("/answer-audio")
@router.post("/q6")
async def korean_audio(request: Request):
    import base64 as _b64
    async def _handle():
        raw = await request.body()
        ctype = request.headers.get("content-type", "").lower()
        body = {}
        # JSON body: detect by content-type OR by raw byte sniff (handles charset variants)
        is_json = "application/json" in ctype or raw[:1] in (b"{", b"[")
        if is_json:
            try:
                body = json.loads(raw)
            except Exception:
                body = {}
        if not body.get("audio_base64"):
            # Try multipart/form-data
            audio_bytes = b""
            if "multipart/form-data" in ctype or "application/x-www-form-urlencoded" in ctype:
                try:
                    form = await request.form()
                    for _k, v in form.items():
                        data = await v.read() if hasattr(v, "read") else None
                        if data and len(data) > 100:
                            audio_bytes = data
                            break
                except Exception:
                    pass
            # Last resort: raw binary body
            if not audio_bytes and raw and not is_json:
                audio_bytes = raw
            if audio_bytes:
                body = {"audio_base64": _b64.b64encode(audio_bytes).decode()}
        email = current_email.get()
        logger.info("Q6 korean audio for %s body_keys=%s", email, list(body.keys()))
        return await solve_korean_audio(body)
    return await _run_solver(_handle, "Q6")


@router.get("/q6/debug")
async def q6_debug():
    return get_q6_debug_info()


@router.get("/q6/transcripts")
async def q6_transcripts():
    info = get_q6_debug_info()
    return {"transcript": info.get("transcript", ""), "source": info.get("transcript_source", "")}


@router.get("/q6/last-audio")
async def q6_last_audio():
    from fastapi.responses import Response
    info = get_q6_debug_info()
    return Response(content=info.get("raw_body", b""), media_type="application/octet-stream")


@router.get("/q6/clear-debug")
async def q6_clear_debug():
    clear_q6_debug_info()
    return {"status": "cleared"}


# ---------------------------------------------------------------------------
# Q8: Semantic Search Passage Ranking
# ---------------------------------------------------------------------------
@router.post("/q8/rank")
@router.post("/rank")
@router.post("/q8")
async def semantic_rank(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        return await solve_semantic_rank(body)
    return await _run_solver(_handle, "Q8")


# ---------------------------------------------------------------------------
# Q9: Word-Problem Solver
# ---------------------------------------------------------------------------
@router.post("/q9/solve")
@router.post("/solve")
@router.post("/q9")
async def cot_math(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        return await solve_cot_math(body)
    return await _run_solver(_handle, "Q9")


# ---------------------------------------------------------------------------
# Config & Tenant Management
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
    return {"status": "ok", "service": "ga3", "timestamp": time.time()}


@router.get("/cache-stats")
async def cache_stats():
    from T22026.GA3.solvers import _LLM_CACHE_HITS, _LLM_CACHE_MISSES, _LLM_CACHE
    return {
        "hits": _LLM_CACHE_HITS,
        "misses": _LLM_CACHE_MISSES,
        "size": len(_LLM_CACHE),
    }


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
        from T22026.GA3.shared.tenant import create_ga3_session
        session_id = create_ga3_session(email, req.aipipe_token)
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


# ---------------------------------------------------------------------------
# Solver Routes (Bucket A endpoints)
# ---------------------------------------------------------------------------
@router.post("/solve/q1")
async def solve_q1(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        return await solve_youtube_filter(body)
    return await _run_solver(_handle, "Q1")


@router.post("/solve/q5")
async def solve_q5(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        return await solve_cosine_similarity(body)
    return await _run_solver(_handle, "Q5")


@router.post("/solve/q10")
async def solve_q10(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        return await solve_proof_of_work(body)
    return await _run_solver(_handle, "Q10")


@router.post("/solve/q11")
async def solve_q11(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        return await solve_context_window_heist(body)
    return await _run_solver(_handle, "Q11")


@router.post("/solve/q12")
async def solve_q12(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        return await solve_spin_up_cli(body)
    return await _run_solver(_handle, "Q12")


@router.post("/solve/q13")
async def solve_q13(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        return await solve_embedding_trapdoors(body)
    return await _run_solver(_handle, "Q13")
