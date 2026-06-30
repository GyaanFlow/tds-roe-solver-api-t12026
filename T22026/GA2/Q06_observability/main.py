from __future__ import annotations

"""
Q06: Production Observability
GET /work?n=K           → {email, done: K}  (increments counter)
GET /metrics            → Prometheus text
GET /healthz            → {status, uptime_s}
GET /logs/tail?limit=N  → [{level, ts, path, request_id}, ...]

Thread-safe counter via threading.Lock.
Circular log buffer (deque) so memory stays bounded.
"""

import time
import uuid
import threading
from collections import deque
from datetime import datetime, timezone
from fastapi import APIRouter, Query, Request
from fastapi.responses import PlainTextResponse
from T22026.GA2.shared.tenant import current_email

router = APIRouter(tags=["Q06 Observability"])

_START_TIME  = time.perf_counter()
_MAX_LOGS    = 2000
_log_buffer  = deque(maxlen=_MAX_LOGS)
_counter     = 0
_counter_lock = threading.Lock()


def record_request(path: str, req_id: str, status_code: int) -> None:
    global _counter
    with _counter_lock:
        _counter += 1
    level = "ERROR" if status_code >= 500 else "WARNING" if status_code >= 400 else "INFO"
    _log_buffer.append({
        "level":      level,
        "ts":         datetime.now(timezone.utc).isoformat(),
        "path":       path,
        "request_id": req_id,
    })


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/work")
async def get_work(request: Request, n: int = Query(..., ge=0, le=10_000)):
    email  = current_email.get()
    req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    path   = request.url.path
    record_request(path, req_id, 200)
    return {"email": email, "done": n}


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics():
    with _counter_lock:
        cnt = _counter
    return (
        "# HELP http_requests_total Total HTTP requests handled.\n"
        "# TYPE http_requests_total counter\n"
        f"http_requests_total {cnt}\n"
    )


@router.get("/healthz")
async def get_healthz():
    uptime = time.perf_counter() - _START_TIME
    return {"status": "ok", "uptime_s": round(uptime, 4)}


@router.get("/logs/tail")
async def get_logs_tail(limit: int = Query(default=50, ge=1, le=1000)):
    logs = list(_log_buffer)
    return logs[-limit:]
