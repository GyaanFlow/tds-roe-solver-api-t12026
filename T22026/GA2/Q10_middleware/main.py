from __future__ import annotations

"""
Q10: Composable Middleware Stack — /ping endpoint
Middleware layers (applied in order, outermost first):
  1. CORS guard: allow only the tenant-specific origin (or exam origins)
  2. X-Request-Id injector: generate + propagate
  3. Rate limiter: N requests / 10s sliding window per X-Client-Id
  4. Handler: {"email": "…", "request_id": "<id>"}

Thread-safe sliding window rate limiter.
"""


import time
import uuid
import threading
from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from T22026.GA2.shared.tenant import current_email, get_q10_middleware_params

router = APIRouter(tags=["Q10 Middleware"])

_store_lock  = threading.Lock()
_windows: Dict[str, List[float]] = {}
_WINDOW_MAX = 1_000

EXAM_ORIGINS = {"https://exam.sanand.workers.dev", "https://sanand0.github.io"}


def _evict_stale():
    now = time.monotonic()
    stale = [c for c, ts in _windows.items() if all(now - t >= 10.0 for t in ts)]
    for c in stale:
        del _windows[c]
    if len(_windows) > _WINDOW_MAX:
        clients = sorted(_windows.keys())[:_WINDOW_MAX // 2]
        for c in clients:
            del _windows[c]


def _check_rate(client_id: str, bucket: int) -> bool:
    now = time.monotonic()
    with _store_lock:
        _evict_stale()
        ts = _windows.get(client_id, [])
        ts = [t for t in ts if now - t < 10.0]
        if len(ts) >= bucket:
            _windows[client_id] = ts
            return False
        ts.append(now)
        _windows[client_id] = ts
    return True


def _cors_headers(origin: str | None, allowed: str) -> dict:
    """Build CORS headers only if origin matches."""
    h: dict = {}
    if origin and (origin == allowed or origin in EXAM_ORIGINS):
        h["Access-Control-Allow-Origin"] = origin
        h["Access-Control-Expose-Headers"] = "X-Request-ID, Retry-After"
    return h


@router.options("/ping")
async def options_ping(request: Request):
    email   = current_email.get()
    params  = get_q10_middleware_params(email)
    origin  = request.headers.get("Origin")
    allowed = params["allowedOrigin"]

    if origin and (origin == allowed or origin in EXAM_ORIGINS):
        return Response(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin":  origin,
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, X-Client-Id, X-Request-ID",
                "Access-Control-Expose-Headers": "X-Request-ID, Retry-After",
            },
        )
    return Response(status_code=403)


@router.get("/ping")
async def ping(
    request:     Request,
    x_client_id:  Optional[str] = Header(None, alias="X-Client-Id"),
    x_request_id: Optional[str] = Header(None, alias="X-Request-ID"),
):
    email   = current_email.get()
    params  = get_q10_middleware_params(email)
    allowed = params["allowedOrigin"]
    bucket  = params["bucket"]
    origin  = request.headers.get("Origin")

    # 1. CORS gate — only block if an Origin IS present and doesn't match
    if origin and (origin not in EXAM_ORIGINS and origin != allowed):
        return JSONResponse(status_code=403, content={"detail": "CORS forbidden"})

    # 2. Request ID — reuse inbound or generate fresh
    req_id  = x_request_id or str(uuid.uuid4())

    # 3. Rate limit
    client  = x_client_id or "anon"
    if not _check_rate(client, bucket):
        hdrs = {
            "X-Request-ID": req_id,
            "Retry-After":  "10",
            **_cors_headers(origin, allowed),
        }
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"}, headers=hdrs)

    # 4. Build response — ALWAYS include X-Request-ID in response header
    hdrs: dict = {
        "X-Request-ID": req_id,
        **_cors_headers(origin, allowed),
    }

    return JSONResponse(
        content={"email": email, "request_id": req_id},
        headers=hdrs,
    )
