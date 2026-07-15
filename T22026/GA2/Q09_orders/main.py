from __future__ import annotations

"""
Q09: Orders API with Idempotency and Cursor Pagination
POST /orders (Idempotency-Key, X-Client-Id)
GET  /orders?limit=N&cursor=K (X-Client-Id)

- Per-tenant total orders from seedrandom
- Rate limit: N requests / 10s per X-Client-Id
- Idempotency: same key always returns same order id (201 first, 200 after)
- Cursor pagination over [1, total_t]
- Thread-safe with per-client locks
"""

import time
import uuid
import threading
from fastapi import APIRouter, Header, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, List, Optional
from T22026.GA2.shared.tenant import current_email, get_q09_orders_params

router = APIRouter(tags=["Q09 Orders"])

# ---------------------------------------------------------------------------
# Global stores (safe for single process; cleared per-restart)
# ---------------------------------------------------------------------------
_store_lock       = threading.Lock()
_idempotency: Dict[str, str]          = {}   # key -> order_id
_rate_windows: Dict[str, List[float]] = {}   # client_id -> [timestamps]
_IDEMPOTENCY_MAX = 10_000
_RATE_WINDOW_MAX = 1_000


def _cors(origin: str | None) -> dict:
    return {
        "Access-Control-Allow-Origin":  origin or "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, X-Client-Id, Idempotency-Key",
        "Access-Control-Expose-Headers": "Retry-After, X-Request-ID",
    }


def _evict_stale():
    now = time.monotonic()
    stale_clients = [c for c, ts in _rate_windows.items() if all(now - t >= 10.0 for t in ts)]
    for c in stale_clients:
        del _rate_windows[c]
    if len(_idempotency) > _IDEMPOTENCY_MAX:
        keys = sorted(_idempotency.keys())[:_IDEMPOTENCY_MAX // 2]
        for k in keys:
            del _idempotency[k]
    if len(_rate_windows) > _RATE_WINDOW_MAX:
        clients = sorted(_rate_windows.keys())[:_RATE_WINDOW_MAX // 2]
        for c in clients:
            del _rate_windows[c]


def _check_rate(client_id: str, limit: int) -> bool:
    now = time.monotonic()
    with _store_lock:
        _evict_stale()
        ts = _rate_windows.get(client_id, [])
        ts = [t for t in ts if now - t < 10.0]
        if len(ts) >= limit:
            _rate_windows[client_id] = ts
            return False
        ts.append(now)
        _rate_windows[client_id] = ts
    return True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.options("/orders")
async def options_orders(request: Request):
    return Response(status_code=200, headers=_cors(request.headers.get("Origin")))


@router.post("/orders")
async def create_order(
    request: Request,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    x_client_id:     Optional[str] = Header(None, alias="X-Client-Id"),
):
    email     = current_email.get()
    params    = get_q09_orders_params(email)
    limit     = params["rateLimit"]
    client_id = x_client_id or "anon"
    origin    = request.headers.get("Origin")

    if not _check_rate(client_id, limit):
        hdrs = {**_cors(origin), "Retry-After": "10"}
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"}, headers=hdrs)

    if idempotency_key:
        with _store_lock:
            if idempotency_key in _idempotency:
                oid = _idempotency[idempotency_key]
                return JSONResponse(status_code=200, content={"id": oid}, headers=_cors(origin))
            oid = str(uuid.uuid4())
            _idempotency[idempotency_key] = oid
        return JSONResponse(status_code=201, content={"id": oid}, headers=_cors(origin))

    return JSONResponse(status_code=201, content={"id": str(uuid.uuid4())}, headers=_cors(origin))


@router.get("/orders")
async def list_orders(
    request: Request,
    limit:       int           = Query(default=10, ge=1, le=100),
    cursor:      Optional[str] = Query(None),
    x_client_id: Optional[str] = Header(None, alias="X-Client-Id"),
):
    email     = current_email.get()
    params    = get_q09_orders_params(email)
    total_t   = params["total"]
    limit_r   = params["rateLimit"]
    client_id = x_client_id or "anon"
    origin    = request.headers.get("Origin")

    if not _check_rate(client_id, limit_r):
        hdrs = {**_cors(origin), "Retry-After": "10"}
        return JSONResponse(status_code=429, content={"detail": "Too Many Requests"}, headers=hdrs)

    start_id = 1
    if cursor:
        try:
            start_id = int(cursor)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid cursor")

    items = []
    idx = start_id
    while idx <= total_t and len(items) < limit:
        items.append({"id": idx, "amount": 100})
        idx += 1

    next_cursor = str(idx) if idx <= total_t else None
    return JSONResponse(content={"items": items, "next_cursor": next_cursor}, headers=_cors(origin))
