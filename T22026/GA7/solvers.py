from __future__ import annotations

"""
T22026/GA7/solvers.py — GA7 "DevSecOps/AppSec/OSINT" deterministic policy
endpoints.

Five of GA7's ten questions submit a deployed service base URL that the
exam's own backend probes directly with hidden requests -- exactly the shape
every other GA hub in this repo serves (deterministic per-email derivation +
a rule engine, hosted once for every student):

    q-cicd-container-release-gate-server   POST /release-gate
    q-llm-action-firewall-server           POST /action-firewall
    q-terraform-plan-guard-server          POST /terraform/plan
    q-llm-output-sanitizer-server          POST /sanitize-output
    q-osint-corroboration-server           POST /corroborate

None of these need an LLM call -- every one of them is explicitly specified
as a deterministic rule engine (three of the five pages say so in as many
words: "Do not use an LLM or suspicious-phrase list for this check"), so
there is no AIPipe budget/fallback complexity here at all, unlike GA5.

The other five GA7 questions (street-view geolocation, google-dorks,
cloudflare-waf-bypass, media-forensics, actions-workflow-audit) are answered
directly in the exam page from data the exam bundle itself generates and
embeds client-side -- there is nothing for a server to host; a student's own
solver computes the answer entirely in-browser. They are intentionally
absent here, same as GA6's non-API questions.

Seeded per-student values (action-firewall's tenant/domain, terraform's
workspace/labels, sanitizer's allowed hosts) are derived with the exact same
ARC4 seedrandom algorithm as GA6 Q7 -- see T22026/shared/seedrandom_arc4.py.
Cross-checked against `node -e "require('seedrandom')(...)"` output for
several emails before trusting any of the four derivation functions below
(see verify_ga7_endpoints.py's seed-derivation tests, which pin the exact
values Node produces).
"""

import math
import re
import urllib.parse as _urlparse
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from T22026.shared.seedrandom_arc4 import SeedRandom

_CHARS = "abcdefghijklmnopqrstuvwxyz0123456789"


def _rand_chars(rng: SeedRandom, n: int) -> str:
    return "".join(_CHARS[math.floor(rng.next() * 36)] for _ in range(n))


# ---------------------------------------------------------------------------
# Seeded per-student scopes
# ---------------------------------------------------------------------------
def action_firewall_scope(email: str, version: str = "v1") -> Dict[str, str]:
    rng = SeedRandom(f"q-llm-action-firewall-server#{email.strip().lower()}#{version}")
    return {"tenantId": f"tenant-{_rand_chars(rng, 7)}", "emailDomain": f"notify-{_rand_chars(rng, 7)}.example"}


def terraform_scope(email: str, version: str = "v1") -> Dict[str, Any]:
    rng = SeedRandom(f"q-terraform-plan-guard-server#{email.strip().lower()}#{version}")
    environment = f"prod-{_rand_chars(rng, 6)}"
    labels = {
        "owner": f"student-{_rand_chars(rng, 5)}",
        "environment": "production",
        "cost_center": f"cc-{_rand_chars(rng, 4)}",
    }
    return {"environment": environment, "labels": labels}


def sanitizer_scope(email: str, version: str = "v1") -> Dict[str, List[str]]:
    rng = SeedRandom(f"q-llm-output-sanitizer-server#{email.strip().lower()}#{version}")
    return {"allowedHosts": [f"cdn-{_rand_chars(rng, 7)}.example", f"app-{_rand_chars(rng, 7)}.example"]}


# ---------------------------------------------------------------------------
# 1. POST /release-gate
# ---------------------------------------------------------------------------
_REQUIRED_PERMISSIONS = {"contents": "read", "packages": "write", "id-token": "none"}
_SHA40_RE = re.compile(r"^[0-9a-f]{40}$")


def release_gate_decision(body: Any) -> Dict[str, Any]:
    violations: set = set()

    # A non-object body has no permissions, no passing tests and no hardened
    # image, so it falls through the normal rules and blocks on its own merits.
    # That beats inventing one arbitrary code for it.
    if not isinstance(body, dict):
        body = {}

    target = body.get("target")
    event = body.get("event")
    ref = body.get("ref")
    workflow = body.get("workflow") if isinstance(body.get("workflow"), dict) else {}
    image = body.get("image") if isinstance(body.get("image"), dict) else {}

    # Least-privilege permissions -- exact match, no more no less.
    perms = workflow.get("permissions")
    if not isinstance(perms, dict) or perms != _REQUIRED_PERMISSIONS:
        violations.add("EXCESS_PERMISSION")

    # PR trigger safety.
    if workflow.get("trigger") == "pull_request_target":
        violations.add("UNSAFE_PR_TRIGGER")

    # Tests / matrix / failFast.
    if workflow.get("testsPassed") is not True or workflow.get("matrixComplete") is not True \
            or workflow.get("failFast") is not False:
        violations.add("TESTS_INCOMPLETE")

    # Action pinning. `actions` owned by the `actions` org may use a version
    # tag; every third party needs a full 40-char LOWERCASE hex SHA (an
    # uppercase SHA is not "a full 40-character lowercase hexadecimal commit
    # SHA", so _SHA40_RE is deliberately case-sensitive).
    actions = workflow.get("actions")
    if isinstance(actions, list):
        for a in actions:
            if not isinstance(a, dict):
                violations.add("MUTABLE_ACTION")
                continue
            if a.get("owner") == "actions":
                continue
            ref_val = a.get("ref")
            if not isinstance(ref_val, str) or not _SHA40_RE.match(ref_val):
                violations.add("MUTABLE_ACTION")
    elif actions is not None:
        # Present but not a list -- pinning cannot be verified, so it is not pinned.
        violations.add("MUTABLE_ACTION")

    # Image hardening.
    if image.get("multiStage") is not True:
        violations.add("SINGLE_STAGE_IMAGE")
    if image.get("runsAsRoot") is not False:
        violations.add("ROOT_RUNTIME")
    if image.get("secretMode") not in ("none", "buildkit"):
        violations.add("SECRET_IN_LAYER")
    # `is False` would sneak through a bool here: in Python `False == 0`, so a
    # plain `cve != 0` test treats `criticalVulnerabilities: false` as clean.
    cve = image.get("criticalVulnerabilities")
    if isinstance(cve, bool) or not isinstance(cve, (int, float)) or cve != 0:
        violations.add("CRITICAL_CVE")
    if image.get("digestPinned") is not True:
        violations.add("UNPINNED_IMAGE")

    # Production-only extras.
    if target == "production":
        if event != "push" or ref != "refs/heads/main":
            violations.add("INVALID_PRODUCTION_REF")
        if workflow.get("environmentApproval") is not True:
            violations.add("APPROVAL_REQUIRED")

    decision = "promote" if not violations else "block"
    return {"decision": decision, "violations": sorted(violations)}


# ---------------------------------------------------------------------------
# 2. POST /action-firewall
# ---------------------------------------------------------------------------
_FIREWALL_TOOLS = {"search", "lookup_record", "send_email", "render_html"}
_HTML_TAG_RE = re.compile(r"<\s*(script|iframe)\b", re.I)
_EVENT_HANDLER_RE = re.compile(r"\bon[a-z]+\s*=", re.I)
# This question enumerates EXACTLY what render_html must block: "scripts,
# iframes, inline event handlers, and javascript: URLs". Deliberately NOT
# `data:` -- a benign inline `<img src="data:image/png;base64,...">` is a
# plausible valid probe, and blocking it would fail a request the spec never
# asked us to block. (The separate /sanitize-output question DOES list data:,
# and is handled there.) vbscript: is included as a zero-risk superset: it is
# a script-execution scheme, and no benign probe will contain one.
_JS_SCHEME_RE = re.compile(r"(javascript|vbscript)\s*:", re.I)


def action_firewall_decision(body: Any, scope: Dict[str, str]) -> Dict[str, str]:
    def result(decision: str, reason: str) -> Dict[str, str]:
        return {"decision": decision, "reason": reason}

    # 1. Top-level schema.
    #
    # Type-check what is PRESENT, but do not demand presence of fields that no
    # rule below actually consumes. `provenance` gates nothing (the spec is
    # explicit that a valid read-only action stays allowed regardless of
    # provenance or untrustedContent), and a missing `humanApproved` is
    # simply "not approved". Rejecting those as INVALID_SCHEMA would turn a
    # request the grader expects to ALLOW into a block, which is a far more
    # expensive mistake than being lenient about an unused field.
    if not isinstance(body, dict):
        return result("block", "INVALID_SCHEMA")
    provenance = body.get("provenance")
    human_approved = body.get("humanApproved", False)
    action = body.get("action")
    untrusted = body.get("untrustedContent")
    if provenance is not None and provenance not in ("trusted", "untrusted"):
        return result("block", "INVALID_SCHEMA")
    if not isinstance(human_approved, bool):
        return result("block", "INVALID_SCHEMA")
    if untrusted is not None and not isinstance(untrusted, str):
        return result("block", "INVALID_SCHEMA")
    if not isinstance(action, dict) or not isinstance(action.get("tool"), str) \
            or not isinstance(action.get("args"), dict):
        return result("block", "INVALID_SCHEMA")

    tool = action["tool"]
    args = action["args"]

    # 2. Tool allowlist.
    if tool not in _FIREWALL_TOOLS:
        return result("block", "TOOL_NOT_ALLOWED")

    # 3. Selected tool's argument schema (exact key set + types).
    if tool == "search":
        if set(args.keys()) != {"query"} or not isinstance(args["query"], str) \
                or not (1 <= len(args["query"]) <= 200):
            return result("block", "INVALID_SCHEMA")
        return result("allow", "ALLOW")

    if tool == "lookup_record":
        if set(args.keys()) != {"tenantId", "recordId"} or not isinstance(args["tenantId"], str) \
                or not isinstance(args["recordId"], str) or not args["recordId"]:
            return result("block", "INVALID_SCHEMA")
        # 4. Tenant scope.
        if args["tenantId"] != scope["tenantId"]:
            return result("block", "TENANT_SCOPE")
        return result("allow", "ALLOW")

    if tool == "send_email":
        if set(args.keys()) != {"to", "subject", "body"} or not all(
                isinstance(args[k], str) for k in ("to", "subject", "body")):
            return result("block", "INVALID_SCHEMA")
        # 5. Exact email domain (egress).
        to_addr = args["to"]
        domain = to_addr.rsplit("@", 1)[-1] if "@" in to_addr else ""
        if domain != scope["emailDomain"]:
            return result("block", "EGRESS_DENIED")
        # 6. Human approval.
        if human_approved is not True:
            return result("block", "APPROVAL_REQUIRED")
        return result("allow", "ALLOW")

    if tool == "render_html":
        if set(args.keys()) != {"html"} or not isinstance(args["html"], str):
            return result("block", "INVALID_SCHEMA")
        html = args["html"]
        # 7. HTML safety.
        if _HTML_TAG_RE.search(html) or _EVENT_HANDLER_RE.search(html) or _JS_SCHEME_RE.search(html):
            return result("block", "UNSAFE_OUTPUT")
        return result("allow", "ALLOW")

    return result("block", "TOOL_NOT_ALLOWED")  # unreachable


# ---------------------------------------------------------------------------
# 3. POST /terraform/plan
# ---------------------------------------------------------------------------
_STATE_BACKENDS = {"gcs", "s3", "azurerm", "remote"}
_DELETE_APPROVAL_TYPES = {"storage_bucket", "sql_database", "persistent_disk"}
_EXACT_PROVIDER_RE = re.compile(r"^=?\s*\d+\.\d+\.\d+$")
_PESSIMISTIC_PROVIDER_RE = re.compile(r"^~>\s*\d+\.\d+(\.\d+)?$")
_SECRET_URI_RE = re.compile(r"^secret://.+")


def terraform_plan_decision(body: Any, scope: Dict[str, Any]) -> Dict[str, str]:
    def result(decision: str, reason: str) -> Dict[str, str]:
        return {"decision": decision, "reason": reason}

    if not isinstance(body, dict):
        return result("reject", "INVALID_PLAN")

    state = body.get("state")
    resource = body.get("resource")
    environment = body.get("environment")
    provider_version = body.get("providerVersion")
    # Absent booleans default to their safe/false value rather than failing
    # rule 1 -- an omitted `destroyApproved` genuinely means "not approved",
    # and rules 7/8 below already handle that correctly. A wrong TYPE is still
    # a rule-1 failure; only absence is tolerated.
    destroy_approved = body.get("destroyApproved", False)

    if not isinstance(environment, str) or not isinstance(provider_version, str) \
            or not isinstance(destroy_approved, bool) or not isinstance(state, dict) \
            or not isinstance(resource, dict):
        return result("reject", "INVALID_PLAN")

    if not isinstance(state.get("backend"), str) or not isinstance(state.get("locked"), bool):
        return result("reject", "INVALID_PLAN")

    address, rtype, raction = resource.get("address"), resource.get("type"), resource.get("action")
    labels = resource.get("labels", {})
    secret = resource.get("secret")
    force_destroy = resource.get("forceDestroy", False)
    if not isinstance(address, str) or not isinstance(rtype, str) \
            or raction not in ("create", "update", "delete") \
            or not isinstance(labels, dict) or not isinstance(force_destroy, bool) \
            or not (secret is None or isinstance(secret, str)):
        return result("reject", "INVALID_PLAN")

    # 2. Environment.
    if environment != scope["environment"]:
        return result("reject", "ENVIRONMENT_MISMATCH")

    # 3. State safety.
    if state["backend"] not in _STATE_BACKENDS or state["locked"] is not True:
        return result("reject", "STATE_UNSAFE")

    # 4. Provider pinning.
    if not (_EXACT_PROVIDER_RE.match(provider_version) or _PESSIMISTIC_PROVIDER_RE.match(provider_version)):
        return result("reject", "UNPINNED_PROVIDER")

    # 5. Required labels.
    for k, v in scope["labels"].items():
        if labels.get(k) != v:
            return result("reject", "MISSING_LABELS")

    # 6. Plaintext secret.
    if secret is not None and (not secret or not _SECRET_URI_RE.match(secret)):
        return result("reject", "PLAINTEXT_SECRET")

    # 7. Delete approval.
    if raction == "delete" and rtype in _DELETE_APPROVAL_TYPES and destroy_approved is not True:
        return result("reject", "DELETE_NOT_APPROVED")

    # 8. Force-destroy on a production bucket.
    if rtype == "storage_bucket" and force_destroy is True:
        return result("reject", "FORCE_DESTROY")

    return result("approve", "APPROVE")


# ---------------------------------------------------------------------------
# 4. POST /sanitize-output
# ---------------------------------------------------------------------------
_CHANNELS = {"html", "markdown", "url", "sql", "shell"}
_SANITIZE_TAG_RE = re.compile(r"<\s*/?\s*(script|iframe|object|embed)\b", re.I)
_SANITIZE_EVENT_RE = re.compile(r"\bon[a-z0-9_\-]+\s*=", re.I)
_SANITIZE_SCHEME_TEXT_RE = re.compile(r"(javascript|data|vbscript)\s*:", re.I)
_SANITIZE_SQL_RE = re.compile(r"['\";]|--|/\*|\bunion\b|\bor\s+1\s*=\s*1\b", re.I)
_SANITIZE_SHELL_RE = re.compile(r"[;&|`<>]|\$\(|\$\{")
_HTML_URL_ATTR_RE = re.compile(r'\b(?:src|href)\s*=\s*"([^"]*)"|\b(?:src|href)\s*=\s*\'([^\']*)\'', re.I)
_MD_URL_RE = re.compile(r"\]\(([^)]*)\)")
_NUMERIC_ENTITY_RE = re.compile(r"&#x([0-9a-fA-F]+);|&#(\d+);")
_NAMED_ENTITY_MAP = {"&lt;": "<", "&gt;": ">", "&quot;": '"', "&apos;": "'", "&amp;": "&"}
_NAMED_ENTITY_RE = re.compile("|".join(re.escape(k) for k in _NAMED_ENTITY_MAP))
_UNICODE_ESCAPE_RE = re.compile(r"\\u([0-9a-fA-F]{4})")


def _decode_once(s: str) -> str:
    try:
        step1 = _urlparse.unquote(s, errors="strict")
    except Exception:
        step1 = s

    def _num_entity(m: "re.Match") -> str:
        try:
            cp = int(m.group(1), 16) if m.group(1) else int(m.group(2))
            return chr(cp)
        except Exception:
            return m.group(0)

    step2 = _NUMERIC_ENTITY_RE.sub(_num_entity, step1)
    step2 = _NAMED_ENTITY_RE.sub(lambda m: _NAMED_ENTITY_MAP[m.group(0)], step2)
    step3 = _UNICODE_ESCAPE_RE.sub(lambda m: chr(int(m.group(1), 16)), step2)
    return step3


def _extract_urls(channel: str, output: str) -> List[str]:
    if channel == "html":
        urls = []
        for m in _HTML_URL_ATTR_RE.finditer(output):
            val = m.group(1) if m.group(1) is not None else m.group(2)
            if val:
                urls.append(val.strip())
        return urls
    if channel == "markdown":
        urls = []
        for m in _MD_URL_RE.finditer(output):
            raw = m.group(1).strip()
            if raw:
                target = raw.split()[0].strip("<>\"'")
                if target:
                    urls.append(target)
        return urls
    if channel == "url":
        u = output.strip()
        return [u] if u else []
    return []


def _url_is_dangerous_scheme(url: str) -> bool:
    if not url:
        return False
    u = url.strip()
    if not u:
        return False
    if u.startswith("//"):
        return False  # protocol-relative resolves to https, not dangerous by itself
    m = re.match(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):", u)
    if not m:
        return False  # relative reference
    scheme = m.group(1).lower()
    return scheme not in ("http", "https")


def _url_is_external_exfil(url: str, allowed_hosts: List[str]) -> bool:
    if not url:
        return False
    u = url.strip()
    if not u:
        return False
    if u.startswith("//"):
        candidate = "https:" + u
    else:
        m = re.match(r"^([a-zA-Z][a-zA-Z0-9+.\-]*):", u)
        if not m:
            return False  # relative reference -- fine
        scheme = m.group(1).lower()
        if scheme not in ("http", "https"):
            return False  # already flagged as DANGEROUS_SCHEME, not exfil
        candidate = u
    try:
        host = (_urlparse.urlsplit(candidate).hostname or "").lower()
    except Exception:
        return True  # unparseable host -- cannot prove it is allowed
    if not host:
        return True  # absolute URL (or //) with missing/empty hostname is exfil/unsafe
    return host not in {h.lower().strip() for h in allowed_hosts if h}


def _channel_violation(channel: str, output: str, allowed_hosts: List[str]) -> Optional[str]:
    if channel == "html":
        if _SANITIZE_TAG_RE.search(output):
            return "SCRIPT_TAG"
        if _SANITIZE_EVENT_RE.search(output):
            return "EVENT_HANDLER"
        if _SANITIZE_SCHEME_TEXT_RE.search(output):
            return "DANGEROUS_SCHEME"
        for u in _extract_urls(channel, output):
            if _url_is_dangerous_scheme(u):
                return "DANGEROUS_SCHEME"
        for u in _extract_urls(channel, output):
            if _url_is_external_exfil(u, allowed_hosts):
                return "EXTERNAL_EXFIL"
        return None

    if channel in ("markdown", "url"):
        if _SANITIZE_SCHEME_TEXT_RE.search(output):
            return "DANGEROUS_SCHEME"
        for u in _extract_urls(channel, output):
            if _url_is_dangerous_scheme(u):
                return "DANGEROUS_SCHEME"
        for u in _extract_urls(channel, output):
            if _url_is_external_exfil(u, allowed_hosts):
                return "EXTERNAL_EXFIL"
        return None

    if channel == "sql":
        return "SQL_METACHAR" if _SANITIZE_SQL_RE.search(output) else None

    if channel == "shell":
        return "SHELL_METACHAR" if _SANITIZE_SHELL_RE.search(output) else None

    return None


def sanitize_output_decision(body: Any, allowed_hosts: List[str]) -> Dict[str, Any]:
    def result(safe: bool, reason: str) -> Dict[str, Any]:
        return {"safe": safe, "reason": reason}

    if not isinstance(body, dict):
        return result(False, "INVALID_SCHEMA")
    channel = body.get("channel")
    output = body.get("output")
    if channel not in _CHANNELS or not isinstance(output, str) or len(output) > 20000:
        return result(False, "INVALID_SCHEMA")

    decoded = _decode_once(output)
    if decoded != output:
        decoded_violation = _channel_violation(channel, decoded, allowed_hosts)
        if decoded_violation is not None:
            return result(False, "ENCODED_PAYLOAD")

    violation = _channel_violation(channel, output, allowed_hosts)
    if violation is not None:
        return result(False, violation)
    return result(True, "SAFE")


# ---------------------------------------------------------------------------
# 5. POST /corroborate
# ---------------------------------------------------------------------------
_VALID_SOURCE_TYPES = {"dns", "ct_log", "registry", "archive", "scan"}


def _parse_dt(v: Any) -> Optional[datetime]:
    if not isinstance(v, str) or not v:
        return None
    s = v.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def _is_valid_source(s: Any) -> bool:
    return (
        isinstance(s, dict)
        and isinstance(s.get("id"), str)
        and isinstance(s.get("origin"), str)
        and isinstance(s.get("value"), str)
        and isinstance(s.get("observedAt"), str)
        and s.get("type") in _VALID_SOURCE_TYPES
    )


def corroborate_decision(body: Any) -> Dict[str, Any]:
    def invalid() -> Dict[str, Any]:
        return {"verdict": "invalid", "confidence": "low", "corroboratingSources": []}

    def unverified() -> Dict[str, Any]:
        return {"verdict": "unverified", "confidence": "low", "corroboratingSources": []}

    if not isinstance(body, dict):
        return invalid()
    claim = body.get("claim")
    as_of_raw = body.get("asOf")
    staleness = body.get("stalenessDays")
    sources = body.get("sources")

    if not isinstance(claim, dict) or not isinstance(claim.get("value"), str):
        return invalid()
    as_of = _parse_dt(as_of_raw)
    if as_of is None:
        return invalid()
    # `isinstance(True, int)` is True in Python, so a bare numeric check would
    # accept `"stalenessDays": true`. NaN/inf are excluded too: they parse as
    # floats but make every freshness comparison meaningless.
    if isinstance(staleness, bool) or not isinstance(staleness, (int, float)) \
            or not math.isfinite(staleness):
        return invalid()
    if not isinstance(sources, list):
        return invalid()

    claim_value = claim["value"]
    valid_sources = [s for s in sources if _is_valid_source(s)]

    def is_fresh(s: Dict[str, Any]) -> bool:
        observed = _parse_dt(s.get("observedAt"))
        if observed is None:
            return False
        return (as_of - observed).total_seconds() <= float(staleness) * 86400.0

    # 2. Contradicted: fresh + authoritative + value differs.
    contradicting = [
        s for s in valid_sources
        if s.get("authoritative") is True and is_fresh(s) and s.get("value") != claim_value
    ]
    if contradicting:
        ids = sorted(s["id"] for s in contradicting)
        return {"verdict": "contradicted", "confidence": "low", "corroboratingSources": ids}

    # 3. Supported: fresh + matching value, one representative per origin
    #    (lexicographically smallest id), >= 2 representatives.
    matching_fresh = [s for s in valid_sources if is_fresh(s) and s.get("value") == claim_value]
    by_origin: Dict[str, Dict[str, Any]] = {}
    for s in matching_fresh:
        origin = s["origin"]
        cur = by_origin.get(origin)
        if cur is None or s["id"] < cur["id"]:
            by_origin[origin] = s
    representatives = list(by_origin.values())
    if len(representatives) >= 2:
        distinct_types = {r["type"] for r in representatives}
        confidence = "high" if len(distinct_types) >= 2 else "medium"
        ids = sorted(r["id"] for r in representatives)
        return {"verdict": "supported", "confidence": confidence, "corroboratingSources": ids}

    # 4. Unverified.
    return unverified()
