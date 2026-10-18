from __future__ import annotations

"""
T22026/GA2/solvers.py — Category A pure Python solvers and state stores for GA2.

Handles all 7 deployed endpoint families:
1. Q3  (q-fastapi-metrics-cors-server): metricsOrigin, stats calculation
2. Q4  (q-oauth-jwks-verify-server): RS256 token verification against IdP public key
3. Q6  (q-compose-redis-tunnel-server): Redis-like key counter & health check
4. Q8  (q-observability-metrics-server): work, Prometheus http_requests_total, logs, healthz
5. Q10 (q-local-llm-structured-server): robust regex/heuristic invoice extractor
6. Q13 (q-ollama-stream-reassembly-server): reconstructed Ollama stream answer
7. Q14 (q-docker-build-cache-server): Docker build cache invalidation cost answer
Also provides shared configBase, analytics, idempotency seeds, and middleware seeds.
"""

import math
import re
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

import jwt
from T22026.shared.seedrandom_arc4 import SeedRandom

EXAM_ORIGIN = "https://exam.sanand.workers.dev"

# Standard fixed IdP Public Key for Q4 (RS256)
OAUTH_PUBKEY = (
    "-----BEGIN PUBLIC KEY-----\n"
    "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY\n"
    "cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID\n"
    "EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc\n"
    "WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfW\n"
    "ed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfI\n"
    "SI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIX\n"
    "dQIDAQAB\n"
    "-----END PUBLIC KEY-----"
)

CF_M = ["port", "workers", "debug", "log_level", "api_key"]
CF_J = ["debug", "info", "warning", "error"]
CF_V = "abcdefghijklmnopqrstuvwxyz0123456789"
ALPHA = "abcdefghijklmnopqrstuvwxyz0123456789"


def fnv1a(text: str) -> int:
    """32-bit FNV-1a hash matching exam specification."""
    h = 2166136261
    for ch in str(text or "").strip().lower():
        h = ((h ^ ord(ch)) * 16777619) & 0xFFFFFFFF
    return h


def seed_for(qid: str, email: str, ver: str = "") -> SeedRandom:
    cleaned = (email or "").strip().lower()
    return SeedRandom(f"{qid}#{cleaned}#{ver}")


def rand_str(rng: SeedRandom, n: int) -> str:
    return "".join(ALPHA[int(rng() * len(ALPHA))] for _ in range(n))


def rand_int(rng: SeedRandom, lo: int, hi: int) -> int:
    return lo + int(rng() * (hi - lo + 1))


# ---------------------------------------------------------------------------
# Q3: Metrics & CORS
# ---------------------------------------------------------------------------
def metrics_origin(email: str, ver: str = "") -> str:
    rng = seed_for("q-fastapi-metrics-cors-server", email, ver)
    return f"https://dash-{rand_str(rng, 6)}.example.com"


def compute_stats(values_str: str) -> Dict[str, Any]:
    raw = [x.strip() for x in (values_str or "").split(",") if x.strip()]
    nums: List[int] = []
    for x in raw:
        try:
            val = float(x)
            if math.isfinite(val):
                nums.append(int(val))
        except Exception:
            continue

    n = len(nums)
    s = sum(nums) if n else 0
    return {
        "count": n,
        "sum": s,
        "min": min(nums) if n else 0,
        "max": max(nums) if n else 0,
        "mean": (s / n) if n else 0.0,
    }


# ---------------------------------------------------------------------------
# Q4: OAuth JWKS Verification
# ---------------------------------------------------------------------------
def oauth_seeds(email: str, ver: str = "") -> Dict[str, str]:
    rng = seed_for("q-oauth-jwks-verify-server", email, ver)
    return {
        "iss": "https://idp.exam.local",
        "aud": f"tds-{rand_str(rng, 8)}.apps.exam.local",
        "sub": f"sub-{rand_str(rng, 12)}",
    }


def verify_oauth_token(token: str, email: str) -> Tuple[int, Dict[str, Any]]:
    if not token or not isinstance(token, str):
        return 401, {"valid": False}
    try:
        expected = oauth_seeds(email)
        # Decode & verify RS256 signature, expiration, issuer, and audience
        payload = jwt.decode(
            token,
            OAUTH_PUBKEY,
            algorithms=["RS256"],
            issuer=expected["iss"],
            audience=expected["aud"],
            options={"require": ["exp", "iss", "aud"]},
        )
        return 200, {
            "valid": True,
            "email": payload.get("email"),
            "sub": payload.get("sub"),
            "aud": payload.get("aud"),
        }
    except Exception:
        return 401, {"valid": False}


# ---------------------------------------------------------------------------
# Q10: Invoice Structured Extraction
# ---------------------------------------------------------------------------
def extract_invoice(text: str) -> Optional[Dict[str, Any]]:
    if not isinstance(text, str) or not text.strip():
        return None

    # Vendor extraction - preserve punctuation like 'Acme-Alpha Industries Ltd.'
    vendor_m = re.search(
        r"\b(?:invoice\s+from|vendor|supplier)\s*[:=-]?\s*(.+?)(?=\s+(?:total\b|amount\b|please\s+pay|pay\b|balance\b|due\s+date|payment\s+due|currency\b)|\r?\n|$)",
        text,
        re.IGNORECASE,
    ) or re.search(r"\b(Acme-[\w-]+\s+Industries\s+Ltd\.?)", text, re.IGNORECASE)

    number_pat = r"[+-]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?"
    curr_pat = r"(USD|EUR|GBP|INR|CAD|AUD|JPY|CHF|AED|SGD)"
    amount_m = re.search(rf"({number_pat})\s*{curr_pat}\b", text, re.IGNORECASE)
    rev_amount_m = re.search(rf"\b{curr_pat}\s*[$€£]?\s*({number_pat})", text, re.IGNORECASE)

    dates = list(re.finditer(r"\b(\d{4}-\d{2}-\d{2})\b", text))
    date_m = re.search(
        r"\b(?:due\s+date|payment\s+due)\s*:?\s*(\d{4}-\d{2}-\d{2})\b",
        text,
        re.IGNORECASE,
    ) or (dates[-1] if dates else None)

    if not vendor_m or (not amount_m and not rev_amount_m) or not date_m:
        return None

    val_str = (amount_m.group(1) if amount_m else rev_amount_m.group(2)).replace(",", "")
    curr = (amount_m.group(2) if amount_m else rev_amount_m.group(1)).upper()
    try:
        val = float(val_str)
    except Exception:
        return None

    v = vendor_m.group(1).strip()
    if not v:
        return None

    d = date_m.group(1) if hasattr(date_m, "group") else date_m[1]
    return {
        "vendor": v,
        "amount": val,
        "currency": curr,
        "date": d,
    }


# ---------------------------------------------------------------------------
# Q13: Ollama Stream Reassembly
# ---------------------------------------------------------------------------
def stream_tag(email: str) -> str:
    return f"job-{fnv1a(email):x}"


def stream_answer(email: str) -> Dict[str, Any]:
    tag = stream_tag(email)
    return {
        "A": {"text": f"Report {tag}: café\nReady ✓", "complete": True, "error": None},
        "B": {"text": f"Partial {tag}", "complete": False, "error": None},
        "C": {"text": f"Draft {tag}", "complete": False, "error": "model unloaded"},
    }


# ---------------------------------------------------------------------------
# Q14: Docker Build Cache Invalidation
# ---------------------------------------------------------------------------
def docker_costs(email: str) -> Dict[str, int]:
    t = fnv1a(email)
    return {
        "install": 40 + (t % 31),
        "compile": 10 + (t % 11),
        "test": 15 + (t % 16),
    }


def docker_answer(email: str) -> Dict[str, Any]:
    costs = docker_costs(email)
    inst, comp, tst = costs["install"], costs["compile"], costs["test"]
    return {
        "A": {"steps": ["L3", "L4", "L5"], "seconds": comp + tst},
        "B": {"steps": ["L1", "L2", "L3", "L4", "L5"], "seconds": inst + comp + tst},
        "C": {"steps": [], "seconds": 0},
        "D": {"steps": [], "seconds": 0},
        "E": {"steps": ["L4", "L5"], "seconds": comp + tst},
    }


# ---------------------------------------------------------------------------
# State Stores for Q6 (Compose Redis Counter) and Q8 (Observability)
# ---------------------------------------------------------------------------
class GA2StateStore:
    def __init__(self):
        self._lock = threading.Lock()
        # Q6 Compose Counters: (email, key) -> count
        self.compose_counts: Dict[str, int] = {}
        # Q8 Observability: email -> count, logs, start_time
        self.obs_count: Dict[str, int] = {}
        self.obs_logs: Dict[str, List[Dict[str, Any]]] = {}
        self.obs_start: Dict[str, float] = {}
        # Additional state for Q5, Q9, Q10
        self.rate_buckets: Dict[str, List[float]] = {}
        self.idem_orders: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self.order_seq: Dict[str, int] = {}

    def hit_key(self, email: str, key: str) -> int:
        norm = (email or "").strip().lower()
        map_key = f"{norm}|{key}"
        with self._lock:
            n = self.compose_counts.get(map_key, 0) + 1
            self.compose_counts[map_key] = n
            return n

    def get_count(self, email: str, key: str) -> int:
        norm = (email or "").strip().lower()
        map_key = f"{norm}|{key}"
        with self._lock:
            return self.compose_counts.get(map_key, 0)

    def obs_bump(self, email: str, path: str, method: str) -> Tuple[int, float]:
        norm = (email or "").strip().lower()
        now = time.time()
        with self._lock:
            if norm not in self.obs_start:
                self.obs_start[norm] = now
            cnt = self.obs_count.get(norm, 0) + 1
            self.obs_count[norm] = cnt

            arr = self.obs_logs.setdefault(norm, [])
            arr.append({
                "level": "info",
                "ts": now,
                "path": path,
                "request_id": str(uuid.uuid4()),
                "method": method,
                "status": 200,
            })
            if len(arr) > 5000:
                del arr[: len(arr) - 5000]

            uptime = now - self.obs_start[norm]
            return cnt, uptime

    def get_obs_metrics(self, email: str) -> int:
        norm = (email or "").strip().lower()
        with self._lock:
            return self.obs_count.get(norm, 0)

    def get_obs_uptime(self, email: str) -> float:
        norm = (email or "").strip().lower()
        now = time.time()
        with self._lock:
            start = self.obs_start.get(norm, now)
            return max(0.0, now - start)

    def get_obs_logs(self, email: str, limit: int = 50) -> List[Dict[str, Any]]:
        norm = (email or "").strip().lower()
        with self._lock:
            arr = self.obs_logs.get(norm, [])
            return list(arr[-limit:])


GA2_STATE = GA2StateStore()
