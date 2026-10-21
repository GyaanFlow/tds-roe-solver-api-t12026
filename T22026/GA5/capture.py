"""Private request/response recorder for the GA5 agent routes (mailroom, A2A, incidents).

Purpose: debug grader failures against the grader's REAL requests instead of guesses.

* Keyed by sha256(email + URL token): only someone holding the full tenant URL can read it.
* Redacts incident ``sensitive`` values and stores Authorization only as a short hash.
* Lives in the temp dir (ephemeral on free hosts), bounded by entry count and bytes.
* Disabled with GA5_CAPTURE=0.
"""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path
from tempfile import gettempdir
from typing import Any, Dict, List, Optional

_ROOT = Path(gettempdir()) / "ga5_capture"
_LOCK = threading.Lock()
MAX_ENTRIES = 160
MAX_BODY_BYTES = 1_500_000
CAPTURE_MARKERS = ("/mailroom", "/q9", "message:send", "/tasks", "/v2/incidents")


def enabled() -> bool:
    return os.environ.get("GA5_CAPTURE", "1") != "0"


def wants(path: str) -> bool:
    return enabled() and any(marker in path for marker in CAPTURE_MARKERS)


def _key(email: str, token: Optional[str]) -> str:
    return hashlib.sha256(f"{(email or '').lower()}::{token or ''}".encode()).hexdigest()[:32]


def _short_hash(value: Optional[str]) -> Optional[str]:
    return hashlib.sha256(value.encode()).hexdigest()[:12] if value else None


def _redact(obj: Any, secrets: List[str]) -> Any:
    if isinstance(obj, dict):
        return {k: ("[REDACTED]" if k == "sensitive" else _redact(v, secrets)) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_redact(v, secrets) for v in obj]
    if isinstance(obj, str) and secrets:
        for s in secrets:
            if s and s in obj:
                obj = obj.replace(s, "[REDACTED]")
    return obj


def _parse(raw: bytes) -> Any:
    if len(raw) > MAX_BODY_BYTES:
        return {"_truncated_bytes": len(raw), "_head": raw[:4000].decode("utf-8", "replace")}
    try:
        return json.loads(raw.decode("utf-8")) if raw else None
    except Exception:
        return {"_raw": raw[:4000].decode("utf-8", "replace")}


def record(email: str, token: Optional[str], method: str, path: str, headers: Dict[str, str],
           request_body: bytes, status: int, response_body: bytes, elapsed: float) -> None:
    try:
        req = _parse(request_body)
        secrets: List[str] = []
        if isinstance(req, dict) and isinstance(req.get("sensitive"), dict):
            secrets = [v for v in req["sensitive"].values() if isinstance(v, str) and len(v) >= 4]
        if token:
            secrets.append(token)
        auth = headers.get("authorization") or ""
        entry = {
            "ts": round(time.time(), 3), "elapsed": round(elapsed, 3), "method": method,
            "path": path.replace(token, "<token>") if token else path, "status": status,
            "headers": {k: v for k, v in headers.items()
                        if k in ("a2a-version", "content-type", "accept", "traceparent", "tracestate", "user-agent")},
            "authHash": _short_hash(auth[7:].strip()) if auth.lower().startswith("bearer ") else (auth and "non-bearer"),
            "request": _redact(req, secrets),
            "response": _redact(_parse(response_body), secrets),
        }
        line = json.dumps(entry, ensure_ascii=False)
        path_ = _ROOT / f"{_key(email, token)}.jsonl"
        with _LOCK:
            _ROOT.mkdir(parents=True, exist_ok=True)
            lines = path_.read_text(encoding="utf-8").splitlines() if path_.exists() else []
            lines.append(line)
            lines = lines[-MAX_ENTRIES:]
            while len(lines) > 1 and sum(len(x) for x in lines) > 40_000_000:
                lines.pop(0)
            tmp = path_.with_suffix(".tmp")
            tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
            tmp.replace(path_)
    except Exception:  # recording must never affect a real response
        pass


def read(email: str, token: Optional[str], contains: str = "", limit: int = 40, offset: int = 0) -> List[Dict[str, Any]]:
    path_ = _ROOT / f"{_key(email, token)}.jsonl"
    if not path_.exists():
        return []
    with _LOCK:
        lines = path_.read_text(encoding="utf-8").splitlines()
    rows = [json.loads(x) for x in lines if x.strip()]
    if contains:
        rows = [r for r in rows if contains in r.get("path", "")]
    rows = rows[::-1]  # newest first
    return rows[offset:offset + max(1, min(limit, 160))]


def clear(email: str, token: Optional[str]) -> None:
    path_ = _ROOT / f"{_key(email, token)}.jsonl"
    with _LOCK:
        if path_.exists():
            path_.unlink()
