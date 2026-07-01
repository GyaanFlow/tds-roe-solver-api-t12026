from __future__ import annotations

"""
shared/tenant.py — Multi-tenant parameter engine
Uses Node.js bridge to run the REAL seedrandom@3.0.5 library,
ensuring exact bit-for-bit match with the exam grader.

Thread-safe ContextVar for request-scoped email.
"""

import json
import os
import subprocess
import sys
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path

# ---------------------------------------------------------------------------
# Context Variable — request-scoped tenant email
# ---------------------------------------------------------------------------
current_email: ContextVar[str] = ContextVar("current_email", default="student@example.com")

# ---------------------------------------------------------------------------
# Node.js bridge — calls seed_bridge.js with seedrandom@3.0.5
# ---------------------------------------------------------------------------
_BRIDGE_SCRIPT = str(Path(__file__).resolve().parent / "seed_bridge.js")

# Find node executable — try common locations
def _find_node() -> str:
    """Find the Node.js executable."""
    # Check if node is on PATH
    for cmd in ("node", "node.exe"):
        try:
            subprocess.run([cmd, "--version"], capture_output=True, timeout=5, check=True)
            return cmd
        except (FileNotFoundError, subprocess.SubprocessError):
            continue
    # Common install locations
    for p in ("/usr/bin/node", "/usr/local/bin/node", "C:\\Program Files\\nodejs\\node.exe"):
        if os.path.isfile(p):
            return p
    return "node"  # fallback

_NODE = _find_node()


@lru_cache(maxsize=4096)
def _get_all_params(email: str) -> dict:
    """Call seed_bridge.js and return all seeded parameters for this email."""
    try:
        result = subprocess.run(
            [_NODE, _BRIDGE_SCRIPT, email.strip().lower()],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(_BRIDGE_SCRIPT),
        )
        if result.returncode != 0:
            raise RuntimeError(f"seed_bridge.js failed: {result.stderr}")
        return json.loads(result.stdout)
    except Exception as e:
        # If Node.js is unavailable, raise a clear error
        raise RuntimeError(
            f"Cannot compute seeded parameters — Node.js bridge failed: {e}. "
            f"Ensure Node.js and seedrandom are installed."
        ) from e


# ---------------------------------------------------------------------------
# Public API — each function extracts from the cached bridge result
# ---------------------------------------------------------------------------

@lru_cache(maxsize=4096)
def get_q01_allowed_origin(email: str) -> str:
    return _get_all_params(email)["q01"]["allowedOrigin"]


@lru_cache(maxsize=4096)
def get_q02_jwt_parameters(email: str) -> dict:
    return _get_all_params(email)["q02"]


@lru_cache(maxsize=4096)
def get_q03_config_layers(email: str) -> dict:
    return _get_all_params(email)["q03"]


@lru_cache(maxsize=4096)
def get_q05_api_key(email: str) -> str:
    return _get_all_params(email)["q05"]["apiKey"]


@lru_cache(maxsize=4096)
def get_q09_orders_params(email: str) -> dict:
    return _get_all_params(email)["q09"]


@lru_cache(maxsize=4096)
def get_q10_middleware_params(email: str) -> dict:
    return _get_all_params(email)["q10"]
