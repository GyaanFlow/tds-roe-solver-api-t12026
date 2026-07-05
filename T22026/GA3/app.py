from __future__ import annotations

"""
T22026/GA3/app.py — Unified GA3 sub-application
Mounted at /ga3 by the root hf_space/app.py.
"""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from T22026.GA3.shared.tenant import current_email
from T22026.GA3.main import router as ga3_router
from T22026.GA3.dashboard import DASHBOARD_HTML

app = FastAPI(
    title="IITM TDS 2026-05 GA3 — Multi-Tenant API Hub",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

@app.middleware("http")
async def _inject_tenant(request: Request, call_next):
    email = (
        request.scope.get("tenant_email")
        or request.query_params.get("email")
        or "student@example.com"
    )
    token = current_email.set(email)
    try:
        response = await call_next(request)
        # Expose CORS headers for grader worker client
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Request-ID, Authorization"
        response.headers["Access-Control-Expose-Headers"] = "Retry-After, X-Request-ID"
        return response
    finally:
        current_email.reset(token)

app.include_router(ga3_router)

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def ga3_home():
    return HTMLResponse(DASHBOARD_HTML)
