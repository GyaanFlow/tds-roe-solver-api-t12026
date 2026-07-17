import json
import logging
import time
from typing import Any, Awaitable, Callable, Dict, List, TypeVar

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from T22026.GA5.shared.tenant import (
    build_ready_routes,
    build_solver_url_prefix,
    current_email,
    current_token,
    get_tenant_config,
    normalize_email,
    set_tenant_config,
)
from T22026.GA5.seedgen import derive_q3_policy, derive_q5_policy
from T22026.GA5.solvers import (
    audit_skill_heuristic,
    audit_skill_llm,
    budget_loop_decision,
    guardrail_decision,
    mcp_handle,
    solve_proration,
)
from T22026.GA4.solvers import resolve_aipipe_token

logger = logging.getLogger("ga5_router")
router = APIRouter()
T = TypeVar("T")

MAX_BODY_BYTES = 2_000_000
MAX_SKILL_TEXT_CHARS = 40_000


def _tenant_token() -> str | None:
    email = current_email.get()
    stored = get_tenant_config(email).get("aipipe_token")
    return resolve_aipipe_token(current_token.get(), stored)


async def _read_json_body(request: Request) -> Dict[str, Any]:
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


async def _run_solver(handler: Callable[[], Awaitable[T]], label: str) -> T | JSONResponse:
    email = current_email.get()
    start = time.time()
    try:
        result = await handler()
        elapsed = time.time() - start
        logger.info("GA5 %s by %s completed in %.2fs", label, email, elapsed)
        return result
    except HTTPException as exc:
        elapsed = time.time() - start
        logger.warning("GA5 %s HTTP error for %s after %.2fs: %s", label, email, elapsed, exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})
    except (RuntimeError, ValueError, KeyError) as exc:
        elapsed = time.time() - start
        logger.warning("GA5 %s client error for %s after %.2fs: %s", label, email, elapsed, exc)
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception:
        elapsed = time.time() - start
        logger.exception("GA5 %s failed for %s after %.2fs", label, email, elapsed)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})


# ---------------------------------------------------------------------------
# Q2: Spec-Driven Development — The Proration Bug (no token, no seed needed)
# ---------------------------------------------------------------------------
@router.post("/proration")
@router.post("/q2")
async def proration_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        for field in ("old_price", "new_price", "days_remaining", "days_in_actual_month"):
            if not isinstance(body.get(field), (int, float)):
                raise ValueError(f"'{field}' must be a number")
        if body.get("spec") not in ("v1", "v2"):
            raise ValueError("'spec' must be 'v1' or 'v2'")
        return solve_proration(body)
    return await _run_solver(_handle, "Q2")


# ---------------------------------------------------------------------------
# Q3: Agent Harness — Pre-Tool-Call Guardrail Hook
# ---------------------------------------------------------------------------
@router.post("/guardrail")
@router.post("/q3")
async def guardrail_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        tool = body.get("tool")
        if tool not in ("bash", "write_file", "http_request"):
            raise ValueError("'tool' must be one of 'bash', 'write_file', 'http_request'")
        email = current_email.get()
        policy = derive_q3_policy(email)
        return guardrail_decision(body, policy=policy)
    return await _run_solver(_handle, "Q3")


# ---------------------------------------------------------------------------
# Q4: Skill Safety Audit — Scanner API
# ---------------------------------------------------------------------------
@router.post("/skill-scan")
@router.post("/q4")
async def skill_scan_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        skill_text = body.get("skill")
        if not isinstance(skill_text, str) or not skill_text.strip():
            raise ValueError("'skill' must be a non-empty string")
        if len(skill_text) > MAX_SKILL_TEXT_CHARS:
            raise ValueError(f"'skill' too long (max {MAX_SKILL_TEXT_CHARS} chars)")

        categories = audit_skill_heuristic(skill_text)
        token = _tenant_token()
        if token:
            try:
                categories = await audit_skill_llm(skill_text, token)
            except Exception as exc:  # noqa: BLE001 — fall back, never hard-fail grading
                logger.warning("Q4 LLM failed, using heuristic result: %s", exc)
        return {"categories": categories}
    return await _run_solver(_handle, "Q4")


# ---------------------------------------------------------------------------
# Q5: Agent Harness — Run Budget & Loop Guard
# ---------------------------------------------------------------------------
@router.post("/budget-guard")
@router.post("/q5")
async def budget_guard_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        if not isinstance(body.get("budget_tokens"), (int, float)):
            raise ValueError("'budget_tokens' must be a number")
        steps = body.get("steps")
        if not isinstance(steps, list):
            raise ValueError("'steps' must be a list")
        for s in steps:
            if not isinstance(s, dict) or "tool" not in s:
                raise ValueError("each item in 'steps' must be an object with a 'tool'")
        email = current_email.get()
        policy = derive_q5_policy(email)
        return budget_loop_decision(body, policy=policy)
    return await _run_solver(_handle, "Q5")


# ---------------------------------------------------------------------------
# Q6: Build a Live MCP Server (JSON-RPC 2.0 over HTTP POST)
# ---------------------------------------------------------------------------
@router.post("/mcp")
async def mcp_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        challenge = request.headers.get("X-Exam-Challenge") or request.headers.get("x-exam-challenge")
        email = normalize_email(current_email.get())
        response = mcp_handle(body, challenge, email)
        if response is None:
            return Response(status_code=202)
        return response
    return await _run_solver(_handle, "Q6")


# ---------------------------------------------------------------------------
# Config & Tenant Management (mirrors GA4/GA3)
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
    return {"status": "ok", "service": "ga5", "timestamp": time.time()}


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
        from T22026.GA5.shared.tenant import create_ga5_session
        session_id = create_ga5_session(email, req.aipipe_token)
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
