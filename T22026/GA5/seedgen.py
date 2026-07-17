from __future__ import annotations

"""
T22026/GA5/seedgen.py — Per-student parameter derivation for GA5 questions whose
policy is seeded from the student's email (Q3 guardrail, Q5 budget/loop guard).

Verified byte-identical to the exam's JS `seedrandom` (David Bau ARC4 PRNG) for
the exact seed strings `${email}#${questionId}#${version}` used by exam-tds-2026-05-ga5.js.
"""

from typing import Any, Dict, List, Tuple

# ---------------------------------------------------------------------------
# seedrandom (David Bau ARC4 PRNG) — Python port, matches JS seedrandom output
# ---------------------------------------------------------------------------
def _mixkey(seed: str, key: list) -> None:
    smear = 0
    j = 0
    mask = 0xFF
    while j < len(seed):
        idx = j & mask
        cur = key[idx] if idx < len(key) else 0
        smear = (smear ^ (cur * 19)) & 0xFFFFFFFF
        val = (smear + ord(seed[j])) & mask
        if idx < len(key):
            key[idx] = val
        else:
            key.append(val)
        j += 1


class SeededRng:
    def __init__(self, seed: str):
        key: list = []
        _mixkey(str(seed), key)
        keylen = len(key) or 1
        s = list(range(256))
        j = 0
        for i in range(256):
            t = s[i]
            j = (j + t + key[i % keylen]) & 0xFF
            s[i] = s[j]
            s[j] = t
        self._s = s
        self._i = 0
        self._j = 0
        self._g(256)  # RC4-drop[256]

    def _g(self, count: int) -> int:
        s = self._s
        i = self._i
        j = self._j
        r = 0
        while count > 0:
            count -= 1
            i = (i + 1) & 0xFF
            t = s[i]
            j = (j + t) & 0xFF
            si_new = s[j]
            s[j] = t
            s[i] = si_new
            r = r * 256 + s[(si_new + t) & 0xFF]
        self._i = i
        self._j = j
        return r

    def __call__(self) -> float:
        significance = 2 ** 52
        overflow = significance * 2
        startdenom = 256 ** 6
        n = self._g(6)
        d = startdenom
        x = 0
        while n < significance:
            n = (n + x) * 256
            d *= 256
            x = self._g(1)
        while n >= overflow:
            n //= 2
            d //= 2
            x >>= 1
        return (n + x) / d


def seedrandom(seed: str) -> SeededRng:
    return SeededRng(seed)


def question_seed(email: str, question_id: str, version: str = "") -> SeededRng:
    """Reproduces the exam's `${email}#${questionId}#${version}` seed exactly
    (unconditional trailing `#version` even when version is empty)."""
    email = str(email or "").strip().lower()
    return seedrandom(f"{email}#{question_id}#{version}")


# ---------------------------------------------------------------------------
# Q3: Agent Harness — Pre-Tool-Call Guardrail Hook
# ---------------------------------------------------------------------------
Q3_ID = "q-agent-tool-guardrail-server"
_Q3_SECRET_FILES = [".bashrc", ".env", ".npmrc", ".netrc", ".pgpass", ".secrets", "credentials.env", "service-account.json"]
_Q3_WRITE_DIRS = ["/workspace/output/", "/home/agent/workspace/build/", "/data/agent/outbox/", "/srv/reports/"]
_Q3_CANDIDATE_HOSTS = ["api.github.com", "pypi.org", "registry.npmjs.org", "huggingface.co", "raw.githubusercontent.com", "objects.githubusercontent.com"]
Q3_HOME_DIR = "/home/agent"
Q3_CWD = "/home/agent/workspace"
Q3_ATTACKER_SUFFIX = "attacker-relay.net"


def derive_q3_policy(email: str, version: str = "") -> Dict[str, Any]:
    rng = question_seed(email, Q3_ID, version)
    secret_rel = _Q3_SECRET_FILES[int(rng() * len(_Q3_SECRET_FILES))]
    write_dir = _Q3_WRITE_DIRS[int(rng() * len(_Q3_WRITE_DIRS))]
    hosts = list(_Q3_CANDIDATE_HOSTS)
    for p in range(len(hosts) - 1, 0, -1):
        d = int(rng() * (p + 1))
        hosts[p], hosts[d] = hosts[d], hosts[p]
    return {
        "secret_rel": secret_rel,
        "secret_file": f"{Q3_HOME_DIR}/{secret_rel}",
        "write_dir": write_dir,
        "allowed_domains": hosts[:2],
        "home_dir": Q3_HOME_DIR,
        "cwd": Q3_CWD,
    }


# ---------------------------------------------------------------------------
# Q5: Agent Harness — Run Budget & Loop Guard
# ---------------------------------------------------------------------------
Q5_ID = "q-agent-budget-loop-guardrail-server"
_Q5_BUDGETS = [18000, 26000, 34000, 42000, 50000]
_Q5_IRRELEVANT_FIELDS = ["trace_id", "request_id", "client_ts"]
_Q5_PAGINATION_PARAMS = ["offset", "page", "cursor"]
_Q5_TARGET_ID_FIELDS = ["job_id", "task_id", "run_id"]
_Q5_TOOL_PAIRS = [["search_docs", "read_doc"], ["list_files", "stat_file"], ["query_db", "fetch_row"]]


def derive_q5_policy(email: str, version: str = "") -> Dict[str, Any]:
    rng = question_seed(email, Q5_ID, version)
    budget_tokens = _Q5_BUDGETS[int(rng() * len(_Q5_BUDGETS))]
    irrelevant_field = _Q5_IRRELEVANT_FIELDS[int(rng() * len(_Q5_IRRELEVANT_FIELDS))]
    pagination_param = _Q5_PAGINATION_PARAMS[int(rng() * len(_Q5_PAGINATION_PARAMS))]
    target_id_field = _Q5_TARGET_ID_FIELDS[int(rng() * len(_Q5_TARGET_ID_FIELDS))]
    tool_pair = _Q5_TOOL_PAIRS[int(rng() * len(_Q5_TOOL_PAIRS))]
    return {
        "budget_tokens": budget_tokens,
        "irrelevant_field": irrelevant_field,
        "pagination_param": pagination_param,
        "target_id_field": target_id_field,
        "tool_pair": tool_pair,
    }
