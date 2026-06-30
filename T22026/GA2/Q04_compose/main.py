from __future__ import annotations

"""
Q04: Docker Compose + Redis Counter
POST /hit/{key}     → INCR → {key, count}
GET  /count/{key}   → GET  → {key, count}
GET  /healthz       → PING → {status, redis}

Redis client is lazily initialised once on first use.
If Redis is unavailable (e.g. local dev without compose), falls back
gracefully with an in-process dict so the service doesn't crash.
"""

import os
import threading
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Q04 Redis"])

# ---------------------------------------------------------------------------
# Redis client — lazy, thread-safe singleton
# ---------------------------------------------------------------------------
_redis_lock = threading.Lock()
_redis_client = None
_fallback: dict[str, int] = {}   # in-process fallback for local dev


def _get_redis():
    global _redis_client
    if _redis_client is not None:
        return _redis_client
    with _redis_lock:
        if _redis_client is not None:
            return _redis_client
        try:
            import redis
            host = os.getenv("REDIS_HOST", "redis")
            port = int(os.getenv("REDIS_PORT", "6379"))
            r = redis.Redis(host=host, port=port, db=0, socket_timeout=2, socket_connect_timeout=2, decode_responses=True)
            r.ping()         # validate connection
            _redis_client = r
        except Exception:
            _redis_client = None   # mark as unavailable
    return _redis_client


def _incr(key: str) -> int:
    r = _get_redis()
    if r:
        return r.incr(f"hit:{key}")
    _fallback[key] = _fallback.get(key, 0) + 1
    return _fallback[key]


def _get(key: str) -> int:
    r = _get_redis()
    if r:
        val = r.get(f"hit:{key}")
        return int(val) if val is not None else 0
    return _fallback.get(key, 0)


def _ping() -> bool:
    r = _get_redis()
    if r:
        try:
            r.ping()
            return True
        except Exception:
            return False
    return False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/hit/{key}")
async def hit_key(key: str):
    count = _incr(key)
    return {"key": key, "count": count}


@router.get("/count/{key}")
async def count_key(key: str):
    count = _get(key)
    return {"key": key, "count": count}


@router.get("/healthz")
async def healthz():
    redis_up = _ping()
    if redis_up:
        return {"status": "ok", "redis": "up"}
    return JSONResponse(
        status_code=503,
        content={"status": "degraded", "redis": "down"},
    )
