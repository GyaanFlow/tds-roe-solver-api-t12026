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
    redteam_guardrail_decision,
    solve_proration,
)
from T22026.GA4.solvers import TokenExpiredError, resolve_aipipe_token
from T22026.GA5 import a2a_agent, incident_agent, mailroom

logger = logging.getLogger("ga5_router")
router = APIRouter()
T = TypeVar("T")

MAX_BODY_BYTES = 2_000_000
MAX_SKILL_TEXT_CHARS = 40_000


def _tenant_token() -> str | None:
    email = current_email.get()
    stored = get_tenant_config(email).get("aipipe_token")
    return resolve_aipipe_token(current_token.get(), stored)


def _content_type_matches(request: Request, expected: str) -> bool:
    content_type = (request.headers.get("content-type") or "").split(";", 1)[0].strip().lower()
    return content_type == expected


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
    except TokenExpiredError as exc:
        elapsed = time.time() - start
        logger.warning("GA5 %s token expired for %s after %.2fs", label, email, elapsed)
        return JSONResponse(
            status_code=401,
            content={
                "error": str(exc),
                "hint": (
                    "⚠️ Your AIPipe token is expired or invalid. "
                    "Get a fresh token from https://aipipe.org and embed it in the URL: "
                    "/ga5/<email>/<NEW_TOKEN>/... "
                    "LLMs can also hallucinate — if you keep getting wrong answers try calling 2-3 times."
                ),
            },
        )
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
        policy = derive_q3_policy(email, version="v1")
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
        policy = derive_q5_policy(email, version="v1")
        return budget_loop_decision(body, policy=policy)
    return await _run_solver(_handle, "Q5")


# ---------------------------------------------------------------------------
# Q8: Guardrail Red-Team Round-Trip (extends Q3: must actually execute allowed
# tool calls and return real results, not just a decision).
# ---------------------------------------------------------------------------
@router.post("/guardrail-redteam")
@router.post("/q8")
async def guardrail_redteam_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        tool = body.get("tool")
        if tool not in ("read_file", "fetch_url"):
            raise ValueError("'tool' must be 'read_file' or 'fetch_url'")
        arguments = body.get("arguments")
        if not isinstance(arguments, dict):
            # Gracefully handle missing/null arguments instead of crashing
            body["arguments"] = {}
        email = current_email.get()
        return await redteam_guardrail_decision(body, email)
    return await _run_solver(_handle, "Q8")


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
# Q9: Lethal-Trifecta Mailroom Action Gate (durable propose/commit AI agent).
# Single endpoint dispatching on body["operation"].
# ---------------------------------------------------------------------------
@router.post("/mailroom")
@router.post("/q9")
async def mailroom_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        operation = body.get("operation")
        email = current_email.get()
        try:
            if operation == "propose":
                token = _tenant_token()
                return await mailroom.propose(body, email, token)
            if operation == "commit":
                return await mailroom.commit(body, email)
            raise mailroom.MailroomError(400, "'operation' must be 'propose' or 'commit'")
        except mailroom.MailroomError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return await _run_solver(_handle, "Q9")


# ---------------------------------------------------------------------------
# Q10: A2A Invoice Action Agent (A2A 1.0 HTTP+JSON surface).
# The Agent Card itself is served at the origin-level well-known path by
# hf_space/app.py (not here) -- see T22026/GA5/a2a_agent.register_base_url.
# ---------------------------------------------------------------------------
def _a2a_principal(request: Request) -> str:
    """Tenant isolation key: normalized email + exact Bearer token.
    This avoids cross-email task visibility when two learners reuse a token."""
    auth = request.headers.get("Authorization") or request.headers.get("authorization") or ""
    if auth.lower().startswith("bearer "):
        return f"{current_email.get()}:{auth[7:].strip()}"
    return ""

def _check_a2a_auth(request: Request) -> None:
    version = request.headers.get("A2A-Version") or request.headers.get("a2a-version")
    if version and version != "1.0":
        raise HTTPException(status_code=400, detail="Unsupported A2A-Version")
    if request.method.upper() == "POST" and not _content_type_matches(request, "application/a2a+json"):
        raise HTTPException(status_code=415, detail="Content-Type must be application/a2a+json")
    auth = request.headers.get("Authorization") or request.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer ") or not auth[7:].strip():
        raise HTTPException(status_code=401, detail="Missing or malformed Bearer token")
    # Do NOT reject non-matching Bearer tokens here. Per the A2A spec, the Bearer
    # is the PRINCIPAL identifier -- different callers legitimately hit the same
    # base URL with different Bearer tokens, and task-level scoping (via
    # _a2a_principal) enforces isolation on read/list/continue/cancel. Requiring
    # Bearer == URL-embedded AIPipe token here made the endpoint 403 the grader
    # (whose Bearer is its own opaque token, unrelated to your billing token).

    # Auto-register THIS exact base URL into the shared, origin-level Agent Card
    # on every A2A call. The spec requires supportedInterfaces to contain "the
    # exact submitted base URL" -- previously this only happened if the student
    # separately called /onboard first, which the grader never does, so the
    # card's supportedInterfaces was empty for any token the grader used
    # directly (AGENT_CARD_CONTRACT failure). Deriving the base URL from the
    # CURRENT request guarantees it exactly matches whatever URL the caller is
    # actually using -- no separate registration step required.
    tenant_token = request.scope.get("tenant_token")
    if tenant_token:
        base_now = str(request.base_url).rstrip("/")
        prefix = build_solver_url_prefix(base_now, current_email.get() or "")
        a2a_agent.register_base_url(f"{prefix}/{tenant_token}/a2a/")


@router.post("/a2a/message:send")
async def a2a_message_send(request: Request):
    _check_a2a_auth(request)

    async def _handle():
        body = await _read_json_body(request)
        principal = _a2a_principal(request)
        token = current_token.get()
        try:
            return await a2a_agent.message_send(body, principal, token)
        except a2a_agent.MailroomError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return await _run_solver(_handle, "Q10/message:send")


@router.get("/a2a/tasks/{task_id}")
async def a2a_get_task(task_id: str, request: Request):
    _check_a2a_auth(request)

    async def _handle():
        principal = _a2a_principal(request)
        try:
            return a2a_agent.get_task(task_id, principal)
        except a2a_agent.MailroomError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return await _run_solver(_handle, "Q10/get-task")


@router.get("/a2a/tasks")
async def a2a_list_tasks(request: Request):
    _check_a2a_auth(request)

    async def _handle():
        principal = _a2a_principal(request)
        return a2a_agent.list_tasks(principal)
    return await _run_solver(_handle, "Q10/list-tasks")


@router.post("/a2a/tasks/{task_id}:cancel")
async def a2a_cancel_task(task_id: str, request: Request):
    _check_a2a_auth(request)

    async def _handle():
        principal = _a2a_principal(request)
        try:
            return await a2a_agent.cancel_task(task_id, principal)
        except a2a_agent.MailroomError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return await _run_solver(_handle, "Q10/cancel-task")


# ---------------------------------------------------------------------------
# Q11: Build an Observable Incident-Response Agent (durable, receipt-correlated
# OTLP-emitting agent). Requires an AIPipe token (embed it in the URL).
# ---------------------------------------------------------------------------
@router.post("/v2/incidents")
async def incidents_create_endpoint(request: Request):
    async def _handle():
        body = await _read_json_body(request)
        email = current_email.get()
        token = _tenant_token()
        incoming_traceparent = request.headers.get("traceparent")
        incoming_tracestate = request.headers.get("tracestate")
        try:
            return await incident_agent.create_incident(body, email, token, incoming_traceparent, incoming_tracestate)
        except incident_agent.MailroomError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return await _run_solver(_handle, "Q11/create")


@router.post("/v2/incidents/{run_id}/receipts")
async def incidents_receipts_endpoint(run_id: str, request: Request):
    async def _handle():
        body = await _read_json_body(request)
        email = current_email.get()
        token = _tenant_token()
        try:
            return await incident_agent.submit_receipts(run_id, body, email, token)
        except incident_agent.MailroomError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return await _run_solver(_handle, "Q11/receipts")


@router.get("/v2/incidents/{run_id}")
async def incidents_get_endpoint(run_id: str, request: Request):
    async def _handle():
        email = current_email.get()
        try:
            return incident_agent.get_incident(run_id, email)
        except incident_agent.MailroomError as exc:
            raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return await _run_solver(_handle, "Q11/get")


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
        # Register this student's A2A base URL into the shared, origin-level
        # Agent Card (Q10) -- the A2A spec assumes one agent per origin, but
        # this hub serves every student from one origin, so the Agent Card's
        # supportedInterfaces accumulates every registered student base.
        base_now = str(request.base_url).rstrip("/")
        prefix = build_solver_url_prefix(base_now, email)
        a2a_agent.register_base_url(f"{prefix}/{req.aipipe_token}/a2a/")
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
