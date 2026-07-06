from __future__ import annotations

"""
T22026/GA3/app.py — Unified GA3 sub-application
Mounted at /ga3 by the root hf_space/app.py.
"""

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse

from T22026.GA3.dashboard import DASHBOARD_HTML
from T22026.GA3.main import router as ga3_router
from T22026.GA3.shared.tenant import current_email, current_token, normalize_email

_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Request-ID, Authorization, X-AIPipe-Token",
    "Access-Control-Expose-Headers": "Retry-After, X-Request-ID",
}

app = FastAPI(
    title="IITM TDS 2026-05 GA3 — Multi-Tenant API Hub",
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
    try:
        response = await call_next(request)
        for key, value in _CORS_HEADERS.items():
            response.headers[key] = value
        return response
    finally:
        current_email.reset(token_cv)
        current_token.reset(token_tok)


@app.options("/{full_path:path}", include_in_schema=False)
async def ga3_preflight(full_path: str) -> Response:
    return Response(status_code=200, headers=_CORS_HEADERS)


app.include_router(ga3_router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def ga3_home():
    return HTMLResponse(DASHBOARD_HTML)
