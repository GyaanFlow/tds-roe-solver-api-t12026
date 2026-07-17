# GA5 Live API — Integration Spec

Fixed request/response contract for the 6 GA5 questions implemented as live API endpoints
(Q2 proration, Q3 pre-tool-call guardrail, Q4 skill safety audit, Q5 budget/loop guard,
Q6 MCP server, Q8 guardrail red-team). The remaining GA5 questions (Q1 maze, Q7 LXD sandbox,
Q9/Q10/Q11 durable agents) are out of scope for this hub — Q1 is pure offline compute for
your other solver, Q7 is manual infrastructure work, and Q9-11 need dedicated stateful services.

This contract is **stable and additive-only**.

---

## 1. Conventions (same model as GA2/GA3/GA4)

- **Base tenant URL:** `https://<host>/ga5/<url-encoded-email>`
- **Method:** every functional endpoint is `POST` with `Content-Type: application/json`.
- **Per-caller AIPipe token, only for Q4:** Q2/Q3/Q5/Q6 are pure deterministic policy
  engines seeded from your email — **no token needed at all**. Q4 works without a token
  (regex heuristic) but is more accurate with one, embedded in the URL path exactly like
  GA4: `…/ga5/<email>/<YOUR_AIPIPE_TOKEN>/skill-scan`. The owner never pays.
- **Per-student seeding:** Q3 and Q5's policies (secret file, write dir, allowed hosts /
  token budget, tracing-field name, tool pair) are derived deterministically from your
  email using a verified Python port of the exam's JS `seedrandom` — byte-identical to
  Node for the exact seed strings used by `exam-tds-2026-05-ga5.js`. Any email gets its
  own independent, reproducible policy.
- **CORS:** open; preflight `OPTIONS` returns `200`.

### Discovering routes
`POST /ga5/onboard {"email"}` returns the same schema as GA3/GA4's onboard:
```json
{
  "email": "me@x.com", "configured": true, "has_token": false,
  "base_url": "https://<host>", "solver_url_prefix": "https://<host>/ga5/me%40x.com",
  "ready_routes": [
    "https://<host>/ga5/me%40x.com/proration",
    "https://<host>/ga5/me%40x.com/guardrail",
    "https://<host>/ga5/me%40x.com/skill-scan",
    "https://<host>/ga5/me%40x.com/budget-guard",
    "https://<host>/ga5/me%40x.com/mcp",
    "https://<host>/ga5/me%40x.com/guardrail-redteam"
  ],
  "session_id": null
}
```
`GET /ga5/<email>/status` — same shape minus `base_url`/`session_id`.
`GET /ga5/<email>/health` → `{"status":"ok","service":"ga5","timestamp":<float>}`.

### Error contract
- **400** `{"error": "<reason>"}` — malformed/empty JSON, wrong types, missing required fields.
- **500** `{"error": "Internal server error"}` — should not occur for valid input.
- Body cap: **2 MB**; skill text cap: **40,000 chars**.

---

## 2. Q2 — Spec-Driven Development: The Proration Bug

**Route:** `POST /ga5/<email>/proration` (alias `/q2`)

### Request
```json
{ "old_price": 10, "new_price": 20, "days_remaining": 15, "days_in_actual_month": 28, "spec": "v2" }
```
`spec` must be `"v1"` or `"v2"`.

### Response
```json
{ "charge": 5.3571 }
```
- `v1`: `charge = (new_price - old_price) * (days_remaining / 30)`
- `v2`: `charge = (new_price - old_price) * (days_remaining / days_in_actual_month)`

---

## 3. Q3 — Agent Harness: Pre-Tool-Call Guardrail Hook

Deterministic policy engine — no LLM. Your seeded policy (derivable from your email via
`T22026/GA5/seedgen.derive_q3_policy(email)`):
- **secret_file**: one file under `/home/agent` that must never be read (directly, via
  `~`/`$HOME` expansion, relative traversal, or base64-wrapped commands).
- **write_dir**: the only directory `write_file` may target (including subdirs; traversal
  escapes are blocked).
- **allowed_domains**: exactly 2 hostnames `http_request` may reach (exact match only —
  subdomain/suffix confusion is blocked).

**Route:** `POST /ga5/<email>/guardrail` (alias `/q3`)

### Request (one of three shapes)
```json
{ "tool": "bash", "command": "..." }
{ "tool": "write_file", "path": "...", "content": "..." }
{ "tool": "http_request", "method": "GET" | "POST", "url": "..." }
```

### Response
```json
{ "decision": "allow" | "block", "reason": "short human-readable string" }
```

Reads of anything outside your seeded secret file are allowed by design (this policy
protects one file and one write boundary, not the whole filesystem).

---

## 4. Q4 — Skill Safety Audit — Scanner API

**Route:** `POST /ga5/<email>/skill-scan` (alias `/q4`; add `/<TOKEN>/skill-scan` for the LLM pass)

### Request
```json
{ "skill": "---\nname: notes-digest\n---\n\n...markdown skill file text..." }
```

### Response
```json
{ "categories": ["hardcoded_secret", "excessive_permissions"] }
```
`categories` ⊆ `{"hardcoded_secret", "prompt_injection", "excessive_permissions", "unclear_provenance"}`,
possibly `[]` for a clean file. Without a token, a regex heuristic runs (catches
hardcoded secrets, obvious injection phrasing, broad-access phrasing, missing
author/version/changelog). With a token, an LLM pass (gpt-4o-mini) replaces it for
better recall on the semantically fuzzy `prompt_injection` category — precision is
weighted higher than recall in scoring (F-beta 0.5), so both paths are tuned conservative.

---

## 5. Q5 — Agent Harness: Run Budget & Loop Guard

Deterministic — no LLM. Seeded policy (`T22026/GA5/seedgen.derive_q5_policy(email)`)
gives the tracing-field name to ignore when comparing args (one of `trace_id`,
`request_id`, `client_ts` — you don't need to know which; the server derives it).

**Route:** `POST /ga5/<email>/budget-guard` (alias `/q5`)

### Request
```json
{
  "budget_tokens": 20000,
  "steps": [
    { "step_number": 1, "tool": "fetch_page", "args": {"url": "https://example.com/1"}, "tokens_used": 9000 }
  ]
}
```

### Response
```json
{ "decision": "continue" | "halt", "reason": "short human-readable string" }
```

Halts if cumulative `tokens_used` ≥ `budget_tokens`, OR the same tool was called 3+ times
consecutively with canonically-identical args (sorted keys, whitespace-normalized strings,
tracing field ignored), OR the trailing steps show a 6+-length alternating 2-tool cycle.
Legitimate pagination/polling (a changing meaningful argument each call) is not flagged.

---

## 6. Q6 — Build a Live MCP Server

Real MCP protocol (JSON-RPC 2.0 over HTTP POST), no LLM.

**Route:** `POST /ga5/<email>/mcp`

Handles `initialize`, `notifications/initialized` (returns HTTP 202, no body — it's a
notification), `tools/list` (returns one tool: `solve_challenge`, no required input
properties), and `tools/call`.

On `tools/call` for `solve_challenge`, reads the **`X-Exam-Challenge` HTTP header** (not
the JSON body) and returns:
```json
{ "content": [{"type": "text", "text": "<first 16 hex chars of SHA-256(challenge:normalizedEmail)>"}], "isError": false }
```
where `normalizedEmail` is the tenant email (trimmed, lowercased) from the URL path.

---

## 7. Q8 — Guardrail Red-Team Round-Trip

Extends Q3: this endpoint doesn't just decide `allow`/`block` — when it allows a call, it
**actually executes** `read_file`/`fetch_url` and returns the real result. No LLM.

Your seeded scenario (derivable via `T22026/GA5/seedgen.derive_q8_scenario(email)`):
- **sandbox_root**: the only directory `read_file` may read from (subdirs included).
- **outside_dir / canary_path**: a seeded file *outside* the sandbox that must never be
  readable, under any obfuscation (traversal, absolute reference, lookalike names).
- **allowed_hosts**: exactly `["example.com", "www.iana.org"]` for `fetch_url` (fixed, not
  per-student) — private/loopback/link-local/metadata hosts and userinfo-confusion tricks
  (`https://example.com@evil.com/`) are rejected, and redirects are followed only if every
  hop's host stays on the allowlist.

**Route:** `POST /ga5/<email>/guardrail-redteam` (alias `/q8`)

### Request
```json
{ "tool": "read_file", "arguments": { "path": "..." } }
{ "tool": "fetch_url", "arguments": { "url": "..." } }
```

### Response
```json
{ "action": "allow" | "block", "reason": "short explanation", "result": "..." }
```
`result` is present only when `action` is `"allow"` — the actual file contents or fetched
body (truncated to 4000 chars for `fetch_url`).

---

## 8. Quick client snippet

```python
import requests
from urllib.parse import quote

HOST, EMAIL = "https://<host>", "you@example.com"
base = f"{HOST}/ga5/{quote(EMAIL, safe='')}"

print(requests.post(f"{base}/proration", json={
    "old_price": 10, "new_price": 20, "days_remaining": 15,
    "days_in_actual_month": 28, "spec": "v2",
}, timeout=10).json())
```

For the exam, submit each tenant URL directly as the answer — the grader calls it. Only
Q4's URL optionally carries your AIPipe token as a path segment for better accuracy;
Q2/Q3/Q5/Q6 need no token at all.
