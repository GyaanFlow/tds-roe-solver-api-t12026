import json
import logging
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
)

logger = logging.getLogger("ga3_router")
router = APIRouter()
T = TypeVar("T")


async def _read_json_body(request: Request) -> Dict[str, Any]:
    try:
        body = await request.json()
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON body: {exc}") from exc
    if not isinstance(body, dict):
        raise ValueError("JSON body must be an object")
    return body


async def _run_solver(handler: Callable[[], Awaitable[T]], label: str) -> T | JSONResponse:
    try:
        return await handler()
    except (RuntimeError, ValueError) as exc:
        logger.warning("%s client error: %s", label, exc)
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception as exc:
        logger.exception("%s failed", label)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


# --- Q2: Multimodal Image QA ---
class MultimodalRequest(BaseModel):
    image_base64: str
    question: str


@router.post("/q2/answer-image")
@router.post("/answer-image")
@router.post("/q2")
async def answer_image(req: MultimodalRequest):
    email = current_email.get()
    logger.info("Q2 multimodal QA for %s", email)

    async def _handle():
        ans = await solve_multimodal_qa(req.image_base64, req.question)
        return {"answer": str(ans)}

    return await _run_solver(_handle, "Q2")


# --- Q3 & Q7: Unified Extraction Endpoint ---
@router.post("/q3/extract")
@router.post("/extract")
@router.post("/q3")
@router.post("/q7/extract")
@router.post("/q7")
async def extract(request: Request):
    email = current_email.get()
    async def _handle():
        body = await _read_json_body(request)
        if "invoice_text" in body:
            logger.info("Q3 fixed extract for %s", email)
            return await solve_invoice_extract(body["invoice_text"])
        else:
            logger.info("Q7 structured extraction for %s", email)
            return await solve_structured_extraction(body)
    return await _run_solver(_handle, "Q3/Q7")


# --- Q4: Dynamic Schema Structured Extraction ---
class DynamicExtractRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    text: str
    schema_def: Dict[str, Any] = Field(alias="schema")


@router.post("/q4/dynamic-extract")
@router.post("/dynamic-extract")
@router.post("/q4")
async def dynamic_extract(req: DynamicExtractRequest):
    email = current_email.get()
    logger.info("Q4 dynamic extract for %s", email)

    async def _handle():
        return await solve_dynamic_extract(req.text, req.schema_def)

    return await _run_solver(_handle, "Q4")


# --- Q6: Korean Audio Dataset API ---
@router.post("/q6/answer-audio")
@router.post("/answer-audio")
@router.post("/q6")
async def korean_audio(request: Request):
    import base64
    email = current_email.get()

    async def _handle():
        raw = await request.body()
        ctype = request.headers.get("content-type", "")
        body = {}
        if "application/json" in ctype or raw[:1] in (b"{", b"["):
            try:
                body = json.loads(raw)
            except Exception:
                pass
        else:
            audio_bytes = b""
            try:
                form = await request.form()
                for k, v in form.items():
                    data = await v.read() if hasattr(v, "read") else None
                    if data:
                        audio_bytes = data
            except Exception:
                pass
            if not audio_bytes and raw:
                audio_bytes = raw
            if audio_bytes:
                body = {"audio_base64": base64.b64encode(audio_bytes).decode()}
        
        logger.info("Q6 korean audio for %s body keys=%s", email, list(body.keys()))
        return await solve_korean_audio(body)

    return await _run_solver(_handle, "Q6")


# --- Q8: Semantic Search Passage Ranking ---
@router.post("/q8/rank")
@router.post("/rank")
@router.post("/q8")
async def semantic_rank(request: Request):
    email = current_email.get()

    async def _handle():
        body = await _read_json_body(request)
        logger.info("Q8 semantic rank for %s", email)
        return await solve_semantic_rank(body)

    return await _run_solver(_handle, "Q8")


# --- Q9: Word-Problem Solver ---
@router.post("/q9/solve")
@router.post("/solve")
@router.post("/q9")
async def cot_math(request: Request):
    email = current_email.get()

    async def _handle():
        body = await _read_json_body(request)
        logger.info("Q9 cot math for %s", email)
        return await solve_cot_math(body)

    return await _run_solver(_handle, "Q9")


# --- Config & Solver Routes for Dashboard ---


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
    return {"status": "ok", "service": "ga3"}


@router.post("/config")
async def save_config(req: ConfigSaveRequest):
    email = current_email.get()
    if req.aipipe_token is not None:
        set_tenant_config(email, {"aipipe_token": req.aipipe_token})
    tenant_cfg = get_tenant_config(email)
    return {
        "status": "ok",
        "message": f"Configuration saved for {email}",
        "has_token": bool(tenant_cfg.get("aipipe_token")),
    }


@router.get("/status", response_model=TenantStatusResponse)
async def tenant_status(request: Request):
    email = normalize_email(current_email.get())
    base = str(request.base_url).rstrip("/")
    tenant_cfg = get_tenant_config(email)
    return TenantStatusResponse(
        email=email,
        configured=True,
        has_token=bool(tenant_cfg.get("aipipe_token")),
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
        # Still set tenant config as fallback / local backup
        set_tenant_config(email, {"aipipe_token": req.aipipe_token})
        
    base = str(request.base_url).rstrip("/")
    tenant_cfg = get_tenant_config(email)
    return OnboardResponse(
        email=email,
        configured=True,
        has_token=bool(tenant_cfg.get("aipipe_token")),
        base_url=base,
        solver_url_prefix=build_solver_url_prefix(base, email),
        ready_routes=build_ready_routes(base, email),
        session_id=session_id
    )


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
