from __future__ import annotations

"""
Q01: CORS-Aware Metrics API
GET /stats?values=1,2,3,...
- Strict per-origin CORS (no wildcards)
- X-Request-ID and X-Process-Time middleware headers on every response
"""

import time
import uuid
from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import JSONResponse
from T22026.GA2.shared.tenant import current_email, get_q01_allowed_origin

router = APIRouter(tags=["Q01 Metrics"])

# ---------------------------------------------------------------------------
# CORS helpers
# ---------------------------------------------------------------------------

EXAM_ORIGINS = {"https://exam.sanand.workers.dev", "https://sanand0.github.io"}

def _cors_headers(origin: str | None, allowed: str) -> dict:
    h: dict = {
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Request-ID",
    }
    if origin and (origin == allowed or origin in EXAM_ORIGINS):
        h["Access-Control-Allow-Origin"] = origin if origin in EXAM_ORIGINS else allowed
    return h


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.options("/stats")
async def stats_preflight(request: Request):
    email   = current_email.get()
    allowed = get_q01_allowed_origin(email)
    origin  = request.headers.get("Origin")
    return Response(status_code=200, headers=_cors_headers(origin, allowed))


@router.get("/stats")
async def get_stats(request: Request, values: str = Query(..., description="Comma-separated integers")):
    t0      = time.perf_counter()
    email   = current_email.get()
    allowed = get_q01_allowed_origin(email)
    origin  = request.headers.get("Origin")
    req_id  = request.headers.get("X-Request-ID") or str(uuid.uuid4())

    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip()]
        if not nums:
            raise ValueError("empty")
    except ValueError:
        process_time = time.perf_counter() - t0
        return JSONResponse(
            status_code=400,
            content={"detail": "values must be comma-separated integers"},
            headers={"X-Request-ID": req_id, "X-Process-Time": f"{process_time:.6f}"}
        )

    n    = len(nums)
    s    = sum(nums)
    mean = s / n

    process_time = time.perf_counter() - t0
    headers = {
        "X-Request-ID":   req_id,
        "X-Process-Time": f"{process_time:.6f}",
        **_cors_headers(origin, allowed),
    }
    return JSONResponse(
        content={"email": email, "count": n, "sum": s, "min": min(nums), "max": max(nums), "mean": round(mean, 6)},
        headers=headers,
    )
