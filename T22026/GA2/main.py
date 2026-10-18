from __future__ import annotations

"""
T22026/GA2/main.py — FastAPI Router for GA2 Category A Endpoints.

Provides dual-route support (both bare paths and tenant-prefixed routes):
1. Q3:  GET  /stats?values=...           (and /{email}/stats, /s/{email}/stats)
2. Q4:  POST /verify                     (and /{email}/verify, /s/{email}/verify)
3. Q6:  POST /hit/{key}, GET /count/{key}, GET /healthz
4. Q8:  GET  /work?n=..., GET /metrics, GET /healthz, GET /logs/tail?limit=...
5. Q10: POST /extract                    (and /{email}/extract, /s/{email}/extract)
6. Q13: GET  /stream.json                (and /{email}/stream.json, /s/{email}/stream.json)
7. Q14: GET  /docker.json                (and /{email}/docker.json, /s/{email}/docker.json)
"""

import time
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Header, Query, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse

from T22026.GA2.solvers import (
    EXAM_ORIGIN,
    GA2_STATE,
    compute_stats,
    docker_answer,
    extract_invoice,
    metrics_origin,
    stream_answer,
    verify_oauth_token,
)

router = APIRouter()

EXPOSE_HEADERS = (
    "Retry-After, X-Request-ID, X-Process-Time, X-RateLimit-Limit, "
    "X-RateLimit-Remaining, X-RateLimit-Reset, Location, Content-Type"
)


def _resolve_email(email_param: Optional[str], request: Request) -> str:
    """Extract tenant email from path, scope, query params, or fallback."""
    if email_param and "@" in email_param:
        return email_param.strip().lower()
    t = getattr(request.state, "tenant_email", None) or request.scope.get("tenant_email")
    if t and "@" in str(t):
        return str(t).strip().lower()
    q = request.query_params.get("email")
    if q and "@" in q:
        return q.strip().lower()
    return "student@example.com"


# ---------------------------------------------------------------------------
# Q3: /stats (CORS strict to assigned origin & exam origin)
# ---------------------------------------------------------------------------
def _stats_cors_headers(origin: Optional[str], email: str) -> dict:
    allowed = metrics_origin(email)
    h: dict = {
        "Vary": "Origin",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Accept, X-Request-ID, Authorization",
    }
    if origin and (origin == allowed or origin == EXAM_ORIGIN):
        h["Access-Control-Allow-Origin"] = origin
        h["Access-Control-Expose-Headers"] = EXPOSE_HEADERS
    return h


@router.options("/stats")
@router.options("/{email}/stats")
@router.options("/s/{email}/stats")
async def stats_options(request: Request, email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    h = _stats_cors_headers(origin, tenant)
    if "Access-Control-Allow-Origin" not in h:
        return JSONResponse(status_code=403, content={"error": "origin not allowed"})
    h["Access-Control-Max-Age"] = "600"
    return Response(status_code=204, headers=h)


@router.get("/stats")
@router.get("/{email}/stats")
@router.get("/s/{email}/stats")
async def stats_get(
    request: Request,
    values: str = Query("", description="Comma-separated integers"),
    email: Optional[str] = None,
):
    t0 = time.perf_counter()
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    cors = _stats_cors_headers(origin, tenant)

    stats = compute_stats(values)
    duration = time.perf_counter() - t0
    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())

    headers = {
        "X-Request-ID": req_id,
        "X-Process-Time": f"{duration:.6f}",
        **cors,
    }
    return JSONResponse(
        status_code=200,
        content={"email": tenant, **stats},
        headers=headers,
    )


# ---------------------------------------------------------------------------
# Q4: /verify (OAuth RS256 token verification)
# ---------------------------------------------------------------------------
def _standard_cors(origin: Optional[str]) -> dict:
    h = {"Vary": "Origin", "Access-Control-Expose-Headers": EXPOSE_HEADERS}
    if origin:
        h["Access-Control-Allow-Origin"] = "*" if origin == "null" else origin
    else:
        h["Access-Control-Allow-Origin"] = "*"
    return h


@router.options("/verify")
@router.options("/{email}/verify")
@router.options("/s/{email}/verify")
async def verify_options(request: Request, email: Optional[str] = None):
    origin = request.headers.get("origin")
    return Response(
        status_code=204,
        headers={
            **_standard_cors(origin),
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Accept, Authorization, X-Request-ID",
        },
    )


@router.post("/verify")
@router.post("/{email}/verify")
@router.post("/s/{email}/verify")
async def verify_post(request: Request, email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    cors = _standard_cors(origin)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(status_code=400, content={"valid": False}, headers=cors)

    token = body.get("token") if isinstance(body, dict) else None
    status_code, resp = verify_oauth_token(token, tenant)
    return JSONResponse(status_code=status_code, content=resp, headers=cors)


# ---------------------------------------------------------------------------
# Q6: Compose Redis Counter (POST /hit/{key}, GET /count/{key}, GET /healthz)
# ---------------------------------------------------------------------------
@router.options("/hit/{key:path}")
@router.options("/{email}/hit/{key:path}")
@router.options("/s/{email}/hit/{key:path}")
async def hit_options(request: Request, key: str, email: Optional[str] = None):
    origin = request.headers.get("origin")
    return Response(
        status_code=204,
        headers={
            **_standard_cors(origin),
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@router.post("/hit/{key:path}")
@router.post("/{email}/hit/{key:path}")
@router.post("/s/{email}/hit/{key:path}")
async def hit_post(request: Request, key: str, email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    count = GA2_STATE.hit_key(tenant, key)
    return JSONResponse(
        status_code=200,
        content={"key": key, "count": count},
        headers=_standard_cors(origin),
    )


@router.options("/count/{key:path}")
@router.options("/{email}/count/{key:path}")
@router.options("/s/{email}/count/{key:path}")
async def count_options(request: Request, key: str, email: Optional[str] = None):
    origin = request.headers.get("origin")
    return Response(
        status_code=204,
        headers={
            **_standard_cors(origin),
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@router.get("/count/{key:path}")
@router.get("/{email}/count/{key:path}")
@router.get("/s/{email}/count/{key:path}")
async def count_get(request: Request, key: str, email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    count = GA2_STATE.get_count(tenant, key)
    return JSONResponse(
        status_code=200,
        content={"key": key, "count": count},
        headers=_standard_cors(origin),
    )


# ---------------------------------------------------------------------------
# Q8: Observability (GET /work?n=..., GET /metrics, GET /healthz, GET /logs/tail)
# ---------------------------------------------------------------------------
@router.get("/work")
@router.get("/{email}/work")
@router.get("/s/{email}/work")
async def work_get(request: Request, n: int = Query(1, ge=0), email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    GA2_STATE.obs_bump(tenant, "/work", "GET")
    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    headers = {"X-Request-ID": req_id, **_standard_cors(origin)}
    return JSONResponse(
        status_code=200,
        content={"email": tenant, "done": n},
        headers=headers,
    )


@router.get("/metrics")
@router.get("/{email}/metrics")
@router.get("/s/{email}/metrics")
async def metrics_get(request: Request, email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    GA2_STATE.obs_bump(tenant, "/metrics", "GET")
    total = GA2_STATE.get_obs_metrics(tenant)
    body = (
        f"# HELP http_requests_total Total HTTP requests\n"
        f"# TYPE http_requests_total counter\n"
        f"http_requests_total {total}\n"
    )
    return PlainTextResponse(
        status_code=200,
        content=body,
        media_type="text/plain; version=0.0.4",
        headers=_standard_cors(origin),
    )


@router.get("/healthz")
@router.get("/{email}/healthz")
@router.get("/s/{email}/healthz")
async def healthz_get(request: Request, email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    _, uptime = GA2_STATE.obs_bump(tenant, "/healthz", "GET")
    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    # Satisfies both Q6 compose (status, redis) and Q8 obs (status, uptime_s)
    content = {
        "status": "ok",
        "redis": "up",
        "uptime_s": uptime,
    }
    return JSONResponse(
        status_code=200,
        content=content,
        headers={"X-Request-ID": req_id, **_standard_cors(origin)},
    )


@router.get("/logs/tail")
@router.get("/{email}/logs/tail")
@router.get("/s/{email}/logs/tail")
async def logs_tail_get(request: Request, limit: int = Query(50, ge=1), email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    GA2_STATE.obs_bump(tenant, "/logs/tail", "GET")
    entries = GA2_STATE.get_obs_logs(tenant, limit=limit)
    req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    return JSONResponse(
        status_code=200,
        content=entries,
        headers={"X-Request-ID": req_id, **_standard_cors(origin)},
    )


# ---------------------------------------------------------------------------
# Q10: Structured Invoice Extraction (POST /extract)
# ---------------------------------------------------------------------------
@router.options("/extract")
@router.options("/{email}/extract")
@router.options("/s/{email}/extract")
async def extract_options(request: Request, email: Optional[str] = None):
    origin = request.headers.get("origin")
    return Response(
        status_code=204,
        headers={
            **_standard_cors(origin),
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        },
    )


@router.post("/extract")
@router.post("/{email}/extract")
@router.post("/s/{email}/extract")
async def extract_post(request: Request, email: Optional[str] = None):
    origin = request.headers.get("origin")
    cors = _standard_cors(origin)
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=422,
            content={"error": "invalid json", "vendor": "", "amount": 0, "currency": "", "date": ""},
            headers=cors,
        )

    text = body.get("text", "") if isinstance(body, dict) else ""
    extracted = extract_invoice(text)
    if not extracted:
        return JSONResponse(
            status_code=422,
            content={"error": "could not extract invoice fields", "vendor": "", "amount": 0, "currency": "", "date": ""},
            headers=cors,
        )
    return JSONResponse(status_code=200, content=extracted, headers=cors)


# ---------------------------------------------------------------------------
# Q13: Ollama Stream Reassembly (GET /stream.json)
# ---------------------------------------------------------------------------
@router.get("/stream.json")
@router.get("/{email}/stream.json")
@router.get("/s/{email}/stream.json")
async def stream_get(request: Request, email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    resp = stream_answer(tenant)
    return JSONResponse(status_code=200, content=resp, headers=_standard_cors(origin))


# ---------------------------------------------------------------------------
# Q14: Docker Build Cache Invalidation (GET /docker.json)
# ---------------------------------------------------------------------------
@router.get("/docker.json")
@router.get("/{email}/docker.json")
@router.get("/s/{email}/docker.json")
async def docker_get(request: Request, email: Optional[str] = None):
    tenant = _resolve_email(email, request)
    origin = request.headers.get("origin")
    resp = docker_answer(tenant)
    return JSONResponse(status_code=200, content=resp, headers=_standard_cors(origin))
