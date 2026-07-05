from __future__ import annotations

"""
T22026/GA3/shared/tenant.py — Multi-tenant request contexts and configurations for GA3.
"""

import os
import json
import threading
import tempfile
from pathlib import Path
from contextvars import ContextVar

current_email: ContextVar[str] = ContextVar("current_email", default="student@example.com")
current_token: ContextVar[str | None] = ContextVar("current_token", default=None)

GA3_CONFIG_DEFAULT = Path(tempfile.gettempdir()) / "ga3_tenant_configs.json"
_CONFIG_FILE = Path(os.environ.get("GA3_TENANT_CONFIG_PATH", str(GA3_CONFIG_DEFAULT)))
_lock = threading.Lock()
_MEMORY_CONFIG: dict[str, dict] = {}


def get_tenant_config(email: str) -> dict:
    """Read the tenant's configuration."""
    email_key = email.strip().lower()
    config = {}
    with _lock:
        if email_key in _MEMORY_CONFIG:
            config = dict(_MEMORY_CONFIG.get(email_key, {}))
        elif _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    config = data.get(email_key, {})
                    _MEMORY_CONFIG[email_key] = dict(config)
            except Exception:
                config = {}

    # Precedence:
    # 1. ContextVar token (passed via request header/query)
    c_token = current_token.get()
    if c_token:
        config["aipipe_token"] = c_token

    # 2. Environment variables fallback
    env_token = os.environ.get("AIPIPE_TOKEN") or os.environ.get("AIPIPE_API_KEY")
    if env_token:
        config["aipipe_token"] = env_token
    return config


def set_tenant_config(email: str, config: dict) -> None:
    """Save the tenant's configuration."""
    email_key = email.strip().lower()
    with _lock:
        _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        data = {}
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
