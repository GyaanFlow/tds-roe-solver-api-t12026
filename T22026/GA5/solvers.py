from __future__ import annotations

"""
T22026/GA5/solvers.py — Live, deployable API logic for the deterministic GA5
questions: Q2 (proration), Q3 (pre-tool-call guardrail), Q5 (budget/loop guard),
Q6 (MCP server). Q4 (skill safety audit) is heuristic-first with an optional
LLM fallback (per-caller AIPipe token, same model as GA4's Q3/Q5).
"""

import base64
import hashlib
import json
import posixpath
import re
from typing import Any, Dict, List, Optional, Tuple

from T22026.GA4.solvers import aipipe_chat, parse_json_block
from T22026.GA5.seedgen import derive_q3_policy, derive_q5_policy, derive_q8_scenario

# ---------------------------------------------------------------------------
# Q2: Spec-Driven Development — The Proration Bug
# ---------------------------------------------------------------------------
def solve_proration(payload: Dict[str, Any]) -> Dict[str, float]:
    old_price = float(payload.get("old_price", 0))
    new_price = float(payload.get("new_price", 0))
    days_remaining = float(payload.get("days_remaining", 0))
    days_in_actual_month = float(payload.get("days_in_actual_month", 30) or 30)
    spec = str(payload.get("spec", "v1"))

    delta = new_price - old_price
    if spec == "v2":
        charge = delta * (days_remaining / days_in_actual_month)
    else:
        charge = delta * (days_remaining / 30.0)
    return {"charge": round(charge, 4)}


# ---------------------------------------------------------------------------
# Q3: Agent Harness — Pre-Tool-Call Guardrail Hook
# ---------------------------------------------------------------------------
_B64_TOKEN_RE = re.compile(r"[A-Za-z0-9+/]{8,}={0,2}")
_HOME_VAR_RE = re.compile(r"\$\{HOME\}|\$HOME")


def _decode_base64_fragments(text: str) -> List[str]:
    """Best-effort recursive base64 decode of any plausible token in `text`,
    so wrapped commands like `bash -c "$(echo <b64> | base64 -d)"` are visible
    to the scanner too."""
    found: List[str] = []
    for match in _B64_TOKEN_RE.finditer(text):
        token = match.group(0)
        if len(token) % 4 != 0:
            continue
        try:
            decoded = base64.b64decode(token, validate=True).decode("utf-8", errors="strict")
        except Exception:
            continue
        if decoded.isprintable() or "\n" in decoded:
            found.append(decoded)
    return found


def _normalize_path(token: str, cwd: str, home: str) -> str:
    token = token.strip().strip("'\"")
    token = _HOME_VAR_RE.sub(home, token)
    if token == "~":
        token = home
    elif token.startswith("~/"):
        token = home + token[1:]
    if not token.startswith("/"):
        token = cwd.rstrip("/") + "/" + token
    return posixpath.normpath(token)


_PATH_TOKEN_RE = re.compile(r"[^\s|;&()<>\"']+")


def _bash_touches_secret(command: str, secret_file: str, cwd: str, home: str) -> bool:
    secret_norm = posixpath.normpath(secret_file)
    texts = [command] + _decode_base64_fragments(command)
    for text in texts:
        # Direct textual form (cheap, catches unobfuscated reads immediately).
        if secret_file in text:
            return True
        # Token-level normalization: any whitespace/quote-delimited token that
        # resolves (relative to cwd, ~ / $HOME expansion) to the secret file.
        for tok in _PATH_TOKEN_RE.findall(text):
            if "/" not in tok and not tok.startswith("~") and "HOME" not in tok and tok != posixpath.basename(secret_file):
                continue
            try:
                if _normalize_path(tok, cwd, home) == secret_norm:
                    return True
            except Exception:
                continue
    return False


def _write_path_allowed(path: str, write_dir: str, cwd: str, home: str) -> bool:
    normalized = _normalize_path(path, cwd, home)
    boundary = posixpath.normpath(write_dir)
    return normalized == boundary or normalized.startswith(boundary.rstrip("/") + "/")


def _hostname_allowed(url: str, allowed_domains: List[str]) -> bool:
    try:
        from urllib.parse import urlparse

        host = (urlparse(url).hostname or "").lower()
    except Exception:
        return False
    return any(host == d.lower() for d in allowed_domains)


def guardrail_decision(payload: Dict[str, Any], policy: Optional[Dict[str, Any]] = None, email: str = "") -> Dict[str, str]:
    policy = policy or derive_q3_policy(email)
    tool = payload.get("tool")
    cwd = policy["cwd"]
    home = policy["home_dir"]

    if tool == "bash":
        command = str(payload.get("command", ""))
        if _bash_touches_secret(command, policy["secret_file"], cwd, home):
            return {"decision": "block", "reason": f"Reading {policy['secret_file']} is never permitted by this agent's policy."}
        return {"decision": "allow", "reason": "Command does not access the restricted secret file."}

    if tool == "write_file":
        path = str(payload.get("path", ""))
        if _write_path_allowed(path, policy["write_dir"], cwd, home):
            return {"decision": "allow", "reason": f"Write target is inside the allowed directory {policy['write_dir']}."}
        return {"decision": "block", "reason": f"Writes are only permitted inside {policy['write_dir']}."}

    if tool == "http_request":
        url = str(payload.get("url", ""))
        if _hostname_allowed(url, policy["allowed_domains"]):
            return {"decision": "allow", "reason": "Destination host is on the allowed list."}
        return {"decision": "block", "reason": "Destination host is not on the allowed list."}

    return {"decision": "block", "reason": f"Unrecognized tool '{tool}'."}


# ---------------------------------------------------------------------------
# Q5: Agent Harness — Run Budget & Loop Guard
# ---------------------------------------------------------------------------
def _canonicalize(obj: Any, ignore_key: str) -> Any:
    if isinstance(obj, dict):
        return {k: _canonicalize(v, ignore_key) for k, v in sorted(obj.items()) if k != ignore_key}
    if isinstance(obj, list):
        return [_canonicalize(v, ignore_key) for v in obj]
    if isinstance(obj, str):
        return re.sub(r"\s+", " ", obj).strip()
    return obj


def _step_key(step: Dict[str, Any], ignore_key: str) -> str:
    canon = _canonicalize(step.get("args", {}) or {}, ignore_key)
    return f"{step.get('tool')}::{json.dumps(canon, sort_keys=True)}"


def _detect_loop(step_keys: List[str]) -> Tuple[bool, Optional[str]]:
    n = len(step_keys)
    # Rule 1: any run of 3+ consecutive identical calls.
    run = 1
    for i in range(1, n):
        if step_keys[i] == step_keys[i - 1]:
            run += 1
            if run >= 3:
                return True, "The same tool call repeated 3 or more times in a row with functionally identical arguments."
        else:
            run = 1
    # Rule 2: a >=6-length trailing 2-step alternating cycle (A,B,A,B,...), A != B.
    for length in range(n, 5, -1):
        window = step_keys[n - length : n]
        a, b = window[0], window[1]
        if a == b:
            continue
        if all(val == (a if idx % 2 == 0 else b) for idx, val in enumerate(window)):
            return True, "The trailing steps show a repeating 2-step cycle with no distinguishing progress."
    return False, None


def budget_loop_decision(payload: Dict[str, Any], policy: Optional[Dict[str, Any]] = None, email: str = "") -> Dict[str, str]:
    policy = policy or derive_q5_policy(email)
    budget_tokens = payload.get("budget_tokens", 0)
    steps = payload.get("steps", []) or []

    total_tokens = sum(int(s.get("tokens_used", 0)) for s in steps)
    if total_tokens >= budget_tokens:
        return {
            "decision": "halt",
            "reason": f"Cumulative tokens_used ({total_tokens}) has reached the budget ({budget_tokens}).",
        }

    step_keys = [_step_key(s, policy["irrelevant_field"]) for s in steps]
    is_loop, reason = _detect_loop(step_keys)
    if is_loop:
        return {"decision": "halt", "reason": reason}

    return {"decision": "continue", "reason": f"Well under budget ({total_tokens}/{budget_tokens}); no repeated-call or cyclical pattern detected."}


# ---------------------------------------------------------------------------
# Q6: Build a Live MCP Server
# ---------------------------------------------------------------------------
def solve_challenge_response(challenge: str, normalized_email: str) -> str:
    digest = hashlib.sha256(f"{challenge}:{normalized_email}".encode("utf-8")).hexdigest()
    return digest[:16]


MCP_TOOL_NAME = "solve_challenge"
MCP_TOOLS = [
    {
        "name": MCP_TOOL_NAME,
        "description": "Returns the exam challenge-response hash derived from the current call's headers.",
        "inputSchema": {"type": "object", "properties": {}, "required": []},
    }
]


def mcp_handle(body: Dict[str, Any], challenge_header: Optional[str], normalized_email: str) -> Optional[Dict[str, Any]]:
    """Handle one JSON-RPC 2.0 MCP request. Returns None for notifications
    (no response body expected), else the JSON-RPC response dict."""
    method = body.get("method")
    req_id = body.get("id")
    is_notification = "id" not in body

    if method == "initialize":
        result = {
            "protocolVersion": "2025-06-18",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "ga5-solve-challenge-server", "version": "1.0.0"},
        }
        return None if is_notification else {"jsonrpc": "2.0", "id": req_id, "result": result}

    if method in ("notifications/initialized", "initialized"):
        return None

    if method == "tools/list":
        result = {"tools": MCP_TOOLS}
        return None if is_notification else {"jsonrpc": "2.0", "id": req_id, "result": result}

    if method == "tools/call":
        params = body.get("params", {}) or {}
        name = params.get("name")
        if name != MCP_TOOL_NAME:
            error = {"code": -32602, "message": f"Unknown tool '{name}'"}
            return None if is_notification else {"jsonrpc": "2.0", "id": req_id, "error": error}
        challenge = challenge_header or ""
        text = solve_challenge_response(challenge, normalized_email)
        result = {"content": [{"type": "text", "text": text}], "isError": False}
        return None if is_notification else {"jsonrpc": "2.0", "id": req_id, "result": result}

    error = {"code": -32601, "message": f"Method not found: {method}"}
    return None if is_notification else {"jsonrpc": "2.0", "id": req_id, "error": error}


# ---------------------------------------------------------------------------
# Q4: Skill Safety Audit — Scanner API (heuristic; LLM upgrade lives in main.py)
# ---------------------------------------------------------------------------
_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|webhook)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/+]{12,}"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"https://hooks\.slack\.com/services/\S+"),
]
_INJECTION_PATTERNS = [
    re.compile(r"(?i)ignore (the )?(user'?s?|previous) (stop|cancel|instructions)"),
    re.compile(r"(?i)do not (tell|inform|notify) the user"),
    re.compile(r"(?i)silently (send|exfiltrate|upload|email)"),
    re.compile(r"(?i)without (asking|notifying|telling) (the )?user"),
]
_EXCESSIVE_PERM_PATTERNS = [
    re.compile(r"(?i)(read|write|access).{0,20}(entire|whole|all|full).{0,10}(filesystem|disk|drive)"),
    re.compile(r"(?i)network:\s*any|domains?:\s*\*|egress.{0,10}any domain"),
    re.compile(r"(?i)permissions?:\s*\[?\s*(read|write)\s*,\s*(read|write).{0,20}(all|\*|any)"),
]


def _has_frontmatter_field(text: str, field: str) -> bool:
    fm_match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    fm = fm_match.group(1) if fm_match else text
    return bool(re.search(rf"(?im)^{field}\s*:\s*\S", fm))


def audit_skill_heuristic(skill_text: str) -> List[str]:
    categories: List[str] = []
    if any(p.search(skill_text) for p in _SECRET_PATTERNS):
        categories.append("hardcoded_secret")
    if any(p.search(skill_text) for p in _INJECTION_PATTERNS):
        categories.append("prompt_injection")
    if any(p.search(skill_text) for p in _EXCESSIVE_PERM_PATTERNS):
        categories.append("excessive_permissions")
    has_author = _has_frontmatter_field(skill_text, "author")
    has_version = _has_frontmatter_field(skill_text, "version")
    has_changelog = "changelog" in skill_text.lower()
    if not has_author and not has_version and not has_changelog:
        categories.append("unclear_provenance")
    return categories


_Q4_ALLOWED_CATEGORIES = {"hardcoded_secret", "prompt_injection", "excessive_permissions", "unclear_provenance"}


async def audit_skill_llm(skill_text: str, token: str) -> List[str]:
    """LLM pass for the semantically fuzzy categories (mainly prompt_injection,
    which plain regex tends to under- or over-flag). Falls back to the caller
    on any error — see main.py's try/except around this."""
    prompt = (
        "You are a strict security scanner for AI agent 'skill' files (markdown with YAML frontmatter).\n"
        "Check the file for exactly these 4 vulnerability categories:\n"
        "- hardcoded_secret: a literal secret/API key/webhook URL embedded directly instead of via env var or secret store.\n"
        "- prompt_injection: a step tries to override user/agent control (e.g. silent exfiltration, ignoring stop requests).\n"
        "- excessive_permissions: declares broader filesystem/network access than the stated task needs.\n"
        "- unclear_provenance: no author, no version, no changelog, and/or silently rewrites its own version metadata.\n\n"
        "A genuinely clean file should get an empty list — do not force a match. Over-claiming is penalized harder "
        "than under-claiming, so only flag a category when the evidence is clear.\n\n"
        'Return strictly JSON: {"categories": ["<zero or more of the 4 exact keys above>"]}\n\n'
        f"SKILL FILE:\n{skill_text}"
    )
    out = parse_json_block(await aipipe_chat([{"role": "user", "content": prompt}], token, model="gpt-4o-mini", max_tokens=300))
    categories = out.get("categories", [])
    if not isinstance(categories, list):
        return []
    return sorted({c for c in categories if c in _Q4_ALLOWED_CATEGORIES})


# ---------------------------------------------------------------------------
# Q8: Guardrail Red-Team Round-Trip — actually executes read_file / fetch_url,
# it doesn't just decide allow/block. The *logical* paths (sandboxRoot,
# outsideDir, canaryPath) are the exact per-student seeded strings the grader
# sends and checks — those are used purely for the security boundary decision.
# Actual bytes are stored under a real, always-writable directory (tempdir),
# so the endpoint works regardless of whether the container can write to the
# literal /srv/... path.
# ---------------------------------------------------------------------------
import tempfile as _tempfile
from pathlib import Path as _Path


def _q8_physical_root(email: str) -> _Path:
    key = hashlib.sha256(str(email or "").strip().lower().encode()).hexdigest()[:20]
    return _Path(_tempfile.gettempdir()) / "ga5_q8_sandbox" / key


def ensure_q8_sandbox_files(email: str, scenario: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Idempotently create the seeded canary/safe files for this student. Safe
    to call on every request — writes only happen once per email (checked via
    file existence)."""
    scenario = scenario or derive_q8_scenario(email)
    physical = _q8_physical_root(email)
    sandbox_dir = physical / "sandbox"
    outside_dir = physical / "outside"
    (sandbox_dir / "notes").mkdir(parents=True, exist_ok=True)
    (sandbox_dir / "encoded").mkdir(parents=True, exist_ok=True)
    outside_dir.mkdir(parents=True, exist_ok=True)

    _write_if_absent(sandbox_dir / "notes" / "report.txt", scenario["safe_report_token"])
    _write_if_absent(sandbox_dir / "notes" / "looks-like-..-but-safe.txt", scenario["safe_weird_token"])
    _write_if_absent(sandbox_dir / "encoded" / "%2e%2e-literal.txt", scenario["safe_encoded_token"])
    _write_if_absent(outside_dir / "canary.txt", scenario["canary_token"])
    return scenario


def _write_if_absent(path: _Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def _q8_logical_to_physical(logical_path: str, scenario: Dict[str, Any], email: str) -> Tuple[bool, Optional[_Path]]:
    """Returns (is_allowed, physical_path_or_None). No URL-decoding — a literal
    `%2e%2e` in the request must stay a literal filename component, never be
    interpreted as `..`."""
    normalized = posixpath.normpath(logical_path)
    sandbox_root = posixpath.normpath(scenario["sandbox_root"])
    outside_dir = posixpath.normpath(scenario["outside_dir"])

    physical = _q8_physical_root(email)

    if normalized == sandbox_root or normalized.startswith(sandbox_root.rstrip("/") + "/"):
        rel = posixpath.relpath(normalized, sandbox_root)
        return True, (physical / "sandbox" / rel)

    if normalized == outside_dir or normalized.startswith(outside_dir.rstrip("/") + "/"):
        return False, None

    return False, None


def q8_read_file(arguments: Dict[str, Any], email: str) -> Dict[str, Any]:
    scenario = ensure_q8_sandbox_files(email)
    path = str(arguments.get("path", ""))
    allowed, physical = _q8_logical_to_physical(path, scenario, email)
    if not allowed:
        return {"action": "block", "reason": f"'read_file' may only read inside {scenario['sandbox_root']}."}
    # Never leak our internal /tmp storage path or a raw exception string --
    # any read failure (missing file, directory, permission) degrades to an
    # empty result. The decision (allow, since the path is in-sandbox) stands.
    content = ""
    try:
        if physical.is_file():
            content = physical.read_text(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        content = ""
    return {"action": "allow", "reason": "Path is inside the sandbox.", "result": content}


_PRIVATE_HOST_RE = re.compile(
    r"^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|169\.254\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?|metadata\.google\.internal)",
    re.IGNORECASE,
)


async def q8_fetch_url(arguments: Dict[str, Any], scenario: Dict[str, Any]) -> Dict[str, Any]:
    import httpx
    from urllib.parse import urlparse

    url = str(arguments.get("url", ""))
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
    except Exception:
        return {"action": "block", "reason": "Malformed URL."}

    allowed_hosts = {h.lower() for h in scenario["allowed_hosts"]}
    if not host or host not in allowed_hosts or _PRIVATE_HOST_RE.match(host):
        return {"action": "block", "reason": "Destination host is not on the allowed list."}

    try:
        async with httpx.AsyncClient(timeout=8.0, follow_redirects=True, max_redirects=5) as client:
            resp = await client.get(url)
        final_host = (urlparse(str(resp.url)).hostname or "").lower()
        if final_host not in allowed_hosts or _PRIVATE_HOST_RE.match(final_host):
            return {"action": "block", "reason": "Request redirected to a host that is not on the allowed list."}
        return {"action": "allow", "reason": "Destination host is on the allowed list.", "result": resp.text[:4000]}
    except Exception as exc:  # noqa: BLE001
        return {"action": "allow", "reason": "Destination host is on the allowed list.", "result": f"(fetch error: {exc})"}


async def redteam_guardrail_decision(payload: Dict[str, Any], email: str) -> Dict[str, Any]:
    scenario = derive_q8_scenario(email)
    tool = payload.get("tool")
    arguments = payload.get("arguments", {}) or {}

    if tool == "read_file":
        return q8_read_file(arguments, email)
    if tool == "fetch_url":
        return await q8_fetch_url(arguments, scenario)
    return {"action": "block", "reason": f"Unrecognized tool '{tool}'."}
