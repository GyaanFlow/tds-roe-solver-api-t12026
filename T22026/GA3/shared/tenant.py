from __future__ import annotations

"""
T22026/GA3/shared/tenant.py — Multi-tenant request contexts and configurations for GA3.
"""

import os
import json
import threading
from pathlib import Path
from contextvars import ContextVar

current_email: ContextVar[str] = ContextVar("current_email", default="student@example.com")
current_token: ContextVar[str | None] = ContextVar("current_token", default=None)

_CONFIG_FILE = Path(__file__).resolve().parents[3] / "work" / "ga3_tenant_configs.json"
_lock = threading.Lock()

def get_tenant_config(email: str) -> dict:
    """Read the tenant's configuration."""
    email_key = email.strip().lower()
    config = {}
    with _lock:
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    config = data.get(email_key, {})
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
        # Create directories if they do not exist
        _CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        data = {}
        if _CONFIG_FILE.exists():
            try:
                with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}
                
        # Merge config
        if email_key not in data:
            data[email_key] = {}
        data[email_key].update(config)
        
        with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
