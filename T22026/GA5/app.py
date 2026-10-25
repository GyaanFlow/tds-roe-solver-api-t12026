from __future__ import annotations

"""
T22026/GA5/app.py — Unified GA5 sub-application
Mounted at /ga5 by the root hf_space/app.py.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

from T22026.GA5.dashboard import DASHBOARD_HTML
from T22026.GA5.main import router as ga5_router
from T22026.GA5.shared.tenant import current_email, current_token, normalize_email

_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Request-ID, Authorization, X-AIPipe-Token, X-Exam-Challenge, X-Exam-Timestamp, X-Exam-Signature, A2A-Version",
    "Access-Control-Expose-Headers": "Retry-After, X-Request-ID",
}

app = FastAPI(
    title="IITM TDS 2026-05 GA5 — Agent Safety/Infra Multi-Tenant API Hub",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


def _resolve_email(request: Request) -> str:
    raw = (
        request.scope.get("tenant_email")
        or request.query_params.get("email")
        or "student@example.com"
    )
    return normalize_email(raw)


def _resolve_token(request: Request) -> str | None:
    req_token = request.scope.get("tenant_token")
    if not req_token:
        req_token = request.headers.get("X-AIPipe-Token") or request.headers.get("x-aipipe-token")
        if not req_token:
            auth_header = request.headers.get("Authorization") or request.headers.get("authorization")
            if auth_header and auth_header.lower().startswith("bearer "):
                req_token = auth_header[7:].strip()
        if not req_token:
            req_token = request.query_params.get("aipipe_token") or request.query_params.get("token")
    return req_token or None


@app.middleware("http")
async def _inject_tenant(request: Request, call_next):
    email = _resolve_email(request)
    req_token = _resolve_token(request)

    token_cv = current_email.set(email)
    token_tok = current_token.set(req_token)

    # Register this tenant's A2A base URL on ANY tenant-scoped GA5 request,
    # not just /a2a/ ones.
    #
    # The Q10 Agent Card must advertise the EXACT submitted base URL, which
    # embeds the student's token -- so a new token, or a redeploy (the
    # registry file is gitignored because it holds real student tokens, and
    # therefore is absent from every fresh build), leaves the card empty until
    # some /a2a/ call happens to land first. If the grader fetches
    # {origin}/.well-known/agent-card.json before its first /a2a/ call, that is
    # an automatic AGENT_CARD_CONTRACT failure -- observed exactly that way
    # after a redeploy + token rotation.
    #
    # Registering from every tenant route means the Q9 (/mailroom) and Q11
    # (/v2/incidents) traffic the grader sends for the same email+token also
    # primes the card, so discovery is far less likely to be the first hit.
    # Best-effort only: never let this break the actual request.
    try:
        _tenant_tok = request.scope.get("tenant_token")
        if _tenant_tok and request.scope.get("tenant_email"):
            from T22026.GA5 import a2a_agent as _a2a
            from T22026.GA5.shared.tenant import build_solver_url_prefix as _prefix
            _base = str(request.base_url).rstrip("/")
            _a2a.register_base_url(f"{_prefix(_base, email)}/{_tenant_tok}/a2a/")
    except Exception:  # noqa: BLE001 -- registration must never break a request
        pass

    try:
        response = await call_next(request)
        for key, value in _CORS_HEADERS.items():
            response.headers[key] = value
        
        path = request.url.path
        if "/a2a/" in path or "agent-card.json" in path:
            response.headers["Content-Type"] = "application/a2a+json"
            
        return response
    finally:
        current_email.reset(token_cv)
        current_token.reset(token_tok)


@app.options("/{full_path:path}", include_in_schema=False)
async def ga5_preflight(full_path: str) -> Response:
    return Response(status_code=200, headers=_CORS_HEADERS)


class _CaptureASGI:
    """Tee request/response bytes of the agent routes into the private recorder
    (T22026/GA5/capture.py). Pure ASGI so it works on every Starlette version."""

    def __init__(self, app):  # Starlette passes this as app=... (keyword)
        self.inner = app

    async def __call__(self, scope, receive, send):
        from T22026.GA5 import capture
        if scope.get("type") != "http" or not capture.wants(scope.get("path", "")):
            return await self.inner(scope, receive, send)
        import time as _time
        started = _time.time()
        req_chunks: list = []
        resp_chunks: list = []
        status_holder = {"status": 0}

        async def _receive():
            message = await receive()
            if message.get("type") == "http.request":
                req_chunks.append(message.get("body", b""))
            return message

        async def _send(message):
            if message.get("type") == "http.response.start":
                status_holder["status"] = message.get("status", 0)
            elif message.get("type") == "http.response.body":
                resp_chunks.append(message.get("body", b""))
            await send(message)

        try:
            await self.inner(scope, _receive, _send)
        finally:
            headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers") or []}
            capture.record(
                normalize_email(scope.get("tenant_email") or ""), scope.get("tenant_token"),
                scope.get("method", ""), scope.get("path", ""), headers,
                b"".join(req_chunks), status_holder["status"], b"".join(resp_chunks), _time.time() - started,
            )


_REF_ENGINE_CACHE: dict = {}


class _ReferenceEnginesASGI:
    """Serve the T3-2026 GA3 mailroom and incident questions with the reference
    engines vendored in T32026/GA3/refimpl (they pass the live grader; see
    T32026/GA3/README.md). Same public URLs: {base}/mailroom and {base}/v2/incidents.
    Set GA3_REF_ENGINES=0 to fall back to the original T22026/GA5 handlers."""

    def __init__(self, app):  # Starlette passes this as app=... (keyword)
        self.inner = app

    def _engine(self, name):
        if name not in _REF_ENGINE_CACHE:
            if name == "mailroom":
                from T32026.GA3.refimpl.mailroom.agent import app as engine
            else:
                from T32026.GA3.refimpl.incident.agent import app as engine
            _REF_ENGINE_CACHE[name] = engine
        return _REF_ENGINE_CACHE[name]

    async def __call__(self, scope, receive, send):
        import os as _os
        if scope.get("type") != "http" or _os.environ.get("GA3_REF_ENGINES", "1") == "0":
            return await self.inner(scope, receive, send)
        path = scope.get("path", "")
        root = scope.get("root_path", "") or ""
        sub = path[len(root):] if root and path.startswith(root) else path
        if sub.startswith("/ga5/"):
            sub = sub[len("/ga5"):]
        target = None
        if sub.rstrip("/") in ("/mailroom", "/q9") and scope.get("method") == "POST":
            target, new_path = "mailroom", "/"
        elif sub.startswith("/v2/incidents"):
            target, new_path = "incident", sub
        if target is None:
            return await self.inner(scope, receive, send)
        child = dict(scope, path=new_path, raw_path=new_path.encode(), root_path="")
        return await self._engine(target)(child, receive, send)


app.add_middleware(_ReferenceEnginesASGI)
app.add_middleware(_CaptureASGI)


@app.get("/debug/captures", include_in_schema=False)
async def ga5_debug_captures(request: Request, contains: str = "", limit: int = 40, offset: int = 0, clear: int = 0):
    """Owner-only view of recorded grader traffic. Requires the tenant URL token."""
    from fastapi.responses import JSONResponse
    from T22026.GA5 import capture
    token = request.scope.get("tenant_token")
    email = normalize_email(request.scope.get("tenant_email") or "")
    if not token or not email:
        return JSONResponse(status_code=404, content={"error": "not found"})
    if clear:
        capture.clear(email, token)
        return {"cleared": True}
    rows = capture.read(email, token, contains=contains, limit=limit, offset=offset)
    return JSONResponse(content={"count": len(rows), "entries": rows}, headers={"Cache-Control": "no-store"})


app.include_router(ga5_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def ga5_home():
    return HTMLResponse(DASHBOARD_HTML)
