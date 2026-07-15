from __future__ import annotations

"""
T22026/GA4/shared/tenant.py — Multi-tenant request contexts and configurations for GA4.
"""

import json
import os
import secrets
import tempfile
import threading
import time
from contextvars import ContextVar
from pathlib import Path
from urllib.parse import quote

current_email: ContextVar[str] = ContextVar("current_email", default="student@example.com")
current_token: ContextVar[str | None] = ContextVar("current_token", default=None)

GA4_CONFIG_DEFAULT = Path(tempfile.gettempdir()) / "ga4_tenant_configs.json"
_CONFIG_FILE = Path(os.environ.get("GA4_TENANT_CONFIG_PATH", str(GA4_CONFIG_DEFAULT)))
_lock = threading.Lock()
_MEMORY_CONFIG: dict[str, dict] = {}

_session_lock = threading.Lock()
GA4_SESSIONS: dict[str, dict] = {}


def create_ga4_session(email: str, token: str) -> str:
    session_id = "sess_" + secrets.token_hex(8)
    now = time.time()
    with _session_lock:
        GA4_SESSIONS[session_id] = {
            "email": normalize_email(email),
            "token": token,
            "expires_at": now + 10800,  # 3 hour lifetime (covers full exam session)
        }
    return session_id


def get_ga4_session_token(session_id: str) -> str | None:
    now = time.time()
    with _session_lock:
        expired = [k for k, v in GA4_SESSIONS.items() if v["expires_at"] < now]
        for k in expired:
            GA4_SESSIONS.pop(k, None)

        sess = GA4_SESSIONS.get(session_id)
        if sess:
            sess["expires_at"] = now + 10800
            return sess["token"]
    return None


GA4_API_ROUTE_SUFFIXES = (
    "/grounded-answer",
    "/vector-search",
    "/extract-graph",
    "/graph-query",
    "/community-summary",
)


def normalize_email(email: str) -> str:
    return email.strip().lower()


def build_solver_url_prefix(base_url: str, email: str) -> str:
    base = base_url.rstrip("/")
    return f"{base}/ga4/{quote(normalize_email(email), safe='')}"


def build_ready_routes(base_url: str, email: str) -> list[str]:
    prefix = build_solver_url_prefix(base_url, email)
    return [f"{prefix}{suffix}" for suffix in GA4_API_ROUTE_SUFFIXES]


def get_stored_token(email: str) -> str | None:
    """Return the user's personal AIPipe token from stored config (ignoring JWT override)."""
    email_key = normalize_email(email)
    with _lock:
        if email_key in _MEMORY_CONFIG:
            return _MEMORY_CONFIG[email_key].get("aipipe_token")
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                token = data.get(email_key, {}).get("aipipe_token")
                _MEMORY_CONFIG[email_key] = dict(data.get(email_key, {}))
                return token
            except Exception:
                pass
    return None


def get_tenant_config(email: str) -> dict:
    """Read the tenant's configuration."""
    email_key = normalize_email(email)
    config: dict = {}
    with _lock:
        if email_key in _MEMORY_CONFIG:
            config = dict(_MEMORY_CONFIG.get(email_key, {}))
        elif _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    config = dict(data.get(email_key, {}))
                    _MEMORY_CONFIG[email_key] = dict(config)
            except Exception:
                config = {}

    c_token = current_token.get()
    if c_token:
        config["aipipe_token"] = c_token
    elif not config.get("aipipe_token"):
        env_token = os.environ.get("AIPIPE_TOKEN") or os.environ.get("AIPIPE_API_KEY")
        if env_token:
            config["aipipe_token"] = env_token
    return config


def set_tenant_config(email: str, config: dict) -> None:
    """Save the tenant's configuration."""
    email_key = normalize_email(email)
    with _lock:
        _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        data: dict = {}
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        if email_key not in data:
            data[email_key] = {}
        data[email_key].update(config)
        _MEMORY_CONFIG[email_key] = dict(data[email_key])

        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
