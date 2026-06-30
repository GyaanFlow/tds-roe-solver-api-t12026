from __future__ import annotations

"""
shared/tenant.py — Multi-tenant seedrandom engine
Ports David Bau's seedrandom.js v3 (ARC4 based).
Thread-safe ContextVar for request-scoped email.
"""

import math
import threading
from contextvars import ContextVar
from functools import lru_cache

# ---------------------------------------------------------------------------
# Context Variable — request-scoped tenant email
# ---------------------------------------------------------------------------
current_email: ContextVar[str] = ContextVar("current_email", default="student@example.com")


# ---------------------------------------------------------------------------
# David Bau's seedrandom.js v3 Port — exact ARC4 match
# ---------------------------------------------------------------------------
class _ARC4:
    _WIDTH = 256
    _MASK = 255

    def __init__(self, key_bytes: bytes) -> None:
        s = list(range(self._WIDTH))
        j = 0
        key = list(key_bytes) if key_bytes else [0]
        kl = len(key)
        for i in range(self._WIDTH):
            j = (j + s[i] + key[i % kl]) & self._MASK
            s[i], s[j] = s[j], s[i]
        self._s = s
        self._i = 0
        self._j = 0
        self.g(self._WIDTH)  # RC4-drop[256]

    def g(self, count: int) -> int:
        r = 0
        s, mask = self._s, self._MASK
        i, j = self._i, self._j
        for _ in range(count):
            i = (i + 1) & mask
            t = s[i]
            j = (j + t) & mask
            s[i], s[j] = s[j], t
            r = r * self._WIDTH + s[(s[i] + s[j]) & mask]
        self._i = i
        self._j = j
        return r


def _mixkey(seed_str: str) -> bytes:
    key = [0] * 256
    smear = 0
    for j, ch in enumerate(seed_str):
        idx = j & 255
        smear = smear ^ (key[idx] * 19)
        smear = (smear + ord(ch)) & 0xFF_FF_FF_FF
        key[idx] = smear & 255
    return bytes(key)


class _Seedrandom:
    _CHUNKS = 6
    _WIDTH = 256
    _SIGNIFICANCE = 2 ** 52
    _OVERFLOW = _SIGNIFICANCE * 2
    _STARTDENOM = _WIDTH ** _CHUNKS

    def __init__(self, seed: str) -> None:
        key_bytes = _mixkey(seed)
        self._arc4 = _ARC4(key_bytes)

    def random(self) -> float:
        n = self._arc4.g(self._CHUNKS)
        d = self._STARTDENOM
        x = 0
        while n < self._SIGNIFICANCE:
            n = (n + x) * self._WIDTH
            d *= self._WIDTH
            x = self._arc4.g(1)
        while n >= self._OVERFLOW:
            n //= 2
            d //= 2
            x >>= 1
        return (n + x) / d


_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"


def _rand_str(rng: _Seedrandom, n: int) -> str:
    return "".join(_ALPHABET[math.floor(rng.random() * len(_ALPHABET))] for _ in range(n))


# ---------------------------------------------------------------------------
# LRU-cached parameter generators (deterministic per email — safe to cache)
# ---------------------------------------------------------------------------

@lru_cache(maxsize=4096)
def get_q01_allowed_origin(email: str) -> str:
    rng = _Seedrandom(f"q-fastapi-metrics-cors-server#{email.strip().lower()}#")
    return f"https://dash-{_rand_str(rng, 6)}.example.com"


@lru_cache(maxsize=4096)
def get_q02_jwt_parameters(email: str) -> dict:
    rng = _Seedrandom(f"q-oauth-jwks-verify-server#{email.strip().lower()}#")
    aud_suffix = _rand_str(rng, 8)
    sub_suffix = _rand_str(rng, 12)
    return {
        "iss": "https://idp.exam.local",
        "aud": f"tds-{aud_suffix}.apps.exam.local",
        "sub": f"sub-{sub_suffix}",
    }


@lru_cache(maxsize=4096)
def get_q03_config_layers(email: str) -> dict:
    rng = _Seedrandom(f"q-config-precedence-server#{email.strip().lower()}#")
    keys = ["port", "workers", "debug", "log_level", "api_key"]
    levels = ["debug", "info", "warning", "error"]

    def rand_val(k: str):
        if k == "port":          return 8000 + math.floor(rng.random() * 1001)
        if k == "workers":       return 1 + math.floor(rng.random() * 16)
        if k == "debug":         return rng.random() < 0.5
        if k == "log_level":     return levels[math.floor(rng.random() * len(levels))]
        if k == "api_key":       return f"key-{_rand_str(rng, 10)}"

    def make_layer() -> dict:
        return {k: rand_val(k) for k in keys if rng.random() < 0.5}

    file_yaml = make_layer()
    dotenv    = make_layer()
    osenv     = make_layer()

    defaults = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}

    def _coerce(k, v):
        if k in ("port", "workers"): return int(v)
        if k == "debug":             return str(v).lower() in ("1", "true", "yes", "on")
        return str(v)

    merged = dict(defaults)
    for layer in (file_yaml, dotenv, osenv):
        for k, v in layer.items():
            merged[k] = _coerce(k, v)

    # Ensure correct Python types
    merged["port"]    = int(merged["port"])
    merged["workers"] = int(merged["workers"])
    merged["debug"]   = bool(merged["debug"])
    merged["log_level"] = str(merged["log_level"])
    merged["api_key"]   = str(merged["api_key"])

    return {"defaults": defaults, "fileYaml": file_yaml, "dotenv": dotenv, "osenv": osenv, "baseEffective": merged}


@lru_cache(maxsize=4096)
def get_q05_api_key(email: str) -> str:
    rng = _Seedrandom(f"q-deploy-analytics-platform-server#{email.strip().lower()}#")
    return f"ak_{_rand_str(rng, 24)}"


@lru_cache(maxsize=4096)
def get_q09_orders_params(email: str) -> dict:
    rng = _Seedrandom(f"q-api-idempotency-pagination-server#{email.strip().lower()}#")
    return {
        "total":     40 + math.floor(rng.random() * 21),   # 40-60
        "rateLimit": 15 + math.floor(rng.random() * 6),    # 15-20
    }


@lru_cache(maxsize=4096)
def get_q10_middleware_params(email: str) -> dict:
    rng = _Seedrandom(f"q-middleware-ratelimit-cors-server#{email.strip().lower()}#")
    return {
        "allowedOrigin": f"https://app-{_rand_str(rng, 6)}.example.com",
        "bucket": 8 + math.floor(rng.random() * 8),        # 8-15
    }
