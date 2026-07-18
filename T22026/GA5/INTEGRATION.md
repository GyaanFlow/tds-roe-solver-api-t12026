# GA5 Live API — Integration Spec

Fixed request/response contract for the 9 GA5 questions implemented as live API endpoints
(Q2 proration, Q3 pre-tool-call guardrail, Q4 skill safety audit, Q5 budget/loop guard,
Q6 MCP server, Q8 guardrail red-team, Q9 mailroom action gate, Q10 A2A invoice agent, Q11
observable incident-response agent). Only Q1 (offline maze BFS — belongs in your other
solver) and Q7 (LXD sandbox — manual infrastructure work) remain out of scope for this hub.

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
    "https://<host>/ga5/me%40x.com/guardrail-redteam",
    "https://<host>/ga5/me%40x.com/mailroom",
    "https://<host>/ga5/me%40x.com/v2/incidents"
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

## 8. Q9 — Lethal-Trifecta Mailroom Action Gate

A durable, idempotent two-phase agent. **Requires an AIPipe token** (embedded in the URL
path, same as Q4) — dossier triage is a genuine semantic judgment call, so it uses an LLM.

**Route:** `POST /ga5/<email>/<YOUR_AIPIPE_TOKEN>/mailroom` (alias `/q9`) — single endpoint,
dispatches on `"operation"`.

### Phase 1 — `propose`
```json
{
  "profile": "ga5-mailroom-action-gate/v2",
  "operation": "propose",
  "evaluationId": "opaque id",
  "corpus": {"coreId": "...", "auditId": "...", "stableCount": 64, "freshCount": 3},
  "allowedActions": ["create_draft","update_internal_record","send_approved_notice","request_confirmation","quarantine_item","no_action"],
  "dossiers": [{"dossierId":"...","partition":"stable_core","receivedAt":"...","mailbox":"...","objective":"...",
                "sources":[{"sourceId":"...","kind":"...","provenance":"...","title":"...","lines":[{"lineId":"...","text":"..."}]}]}]
}
```
Response:
```json
{
  "profile": "ga5-mailroom-action-gate/v2", "evaluationId": "...", "status": "awaiting_receipts",
  "inputDigest": "sha256 hex over recursively key-sorted compact JSON of `dossiers`",
  "proposals": [{"dossierId":"...","callId":"...","action":"...","target":{"kind":"...","id":"..."}|null,
                 "payload":{"...":"..."},"evidence":["lineId",...]}]
}
```
- Exactly one proposal per dossier, unique `callId`s, target/payload keys are **exact** per
  the frozen schema for each of the 6 actions (see `T22026/GA5/mailroom.py::_ACTION_SCHEMAS`).
- **Idempotent**: replaying the exact same `evaluationId` + `dossiers` returns the
  byte-identical cached response — no re-triage. The same `evaluationId` with *different*
  content → **HTTP 409**.
- **Stable-core reuse**: proposals are cached by `(dossierId, content fingerprint)`, so
  identical dossier content across different evaluations reuses the cached decision —
  only genuinely new/changed dossiers trigger an LLM call.
- Malformed schema (missing `dossierId`, duplicate `dossierId`s, empty `dossiers`, wrong
  `profile`) → **400/422**, before any AI work.

### Phase 2 — `commit`
```json
{
  "profile": "ga5-mailroom-action-gate/v2", "operation": "commit",
  "evaluationId": "same id", "inputDigest": "same digest",
  "receipts": [{"dossierId":"...","callId":"...","action":"...","accepted":true,
                "proposalDigest":"...","receiptId":"..."}]
}
```
Response:
```json
{
  "profile": "ga5-mailroom-action-gate/v2", "evaluationId": "...", "status": "completed",
  "inputDigest": "...", "outcomes": [{"dossierId":"...","callId":"...","action":"...",
                "proposalDigest":"...","receiptId":"...","status":"executed"|"rejected"}]
}
```
- `status` is `"executed"` only when `receipt.accepted` is `true`, else `"rejected"`.
- Every receipt is validated against the **persisted** proposal (its `dossierId`, `action`,
  and recomputed `proposalDigest` must match exactly) — a forged/tampered receipt → **400**.
- Unknown `evaluationId` → **404**. Exact commit replay → byte-identical cached response.
  A *different* receipt set submitted against an already-committed evaluation → **409**
  (the terminal state is immutable — this is a conflict, not a replay).

---

## 9. Q10 — A2A Invoice Action Agent

Implements the actual [A2A 1.0 HTTP+JSON spec](https://a2a-protocol.org/latest/specification/):
agent-card discovery, `message:send`, and a task lifecycle, plus semantic invoice triage.
**Requires an AIPipe token** — embedded in the URL, same as Q4/Q9.

**⚠️ Multi-tenancy caveat you must know:** A2A assumes **one agent per origin**, with the
Agent Card published at a *fixed origin-level path*. This hub serves every student from one
shared origin, so the Agent Card's `supportedInterfaces` is a **shared, accumulating
registry** of every student's base URL — populated by `POST /ga5/onboard`. **You must call
`/ga5/onboard` with your `aipipe_token` at least once** (opening the `/ga5/` dashboard and
clicking "Generate URLs" does this automatically) **before your Q10 submission is graded**,
or your base URL won't be in the card yet.

### Agent Card — `GET https://<host>/.well-known/agent-card.json` (origin-level, public, no auth)
```json
{
  "name": "GA5 Invoice Action Agent", "description": "...", "version": "1.0.0",
  "capabilities": {"streaming": false, "pushNotifications": false},
  "skills": [{"id": "invoice_action_agent", "name": "...", "description": "...", "tags": [...]}],
  "supportedInterfaces": [{"url": "https://<host>/ga5/<email>/<token>/a2a/", "protocolBinding": "HTTP+JSON", "protocolVersion": "1.0"}],
  "defaultInputModes": ["application/vnd.ga5.invoice-claim-batch+json"],
  "defaultOutputModes": ["application/vnd.ga5.invoice-action-proposals+json", "application/vnd.ga5.invoice-action-receipts+json"]
}
```

### All other routes — under your base: `https://<host>/ga5/<email>/<TOKEN>/a2a/`
```
POST {base}/message:send
GET  {base}/tasks/{id}
GET  {base}/tasks
POST {base}/tasks/{id}:cancel
```
Required headers on every call: `A2A-Version: 1.0` and `Authorization: Bearer <TOKEN>` (the
same token embedded in your URL — an exact match is required; wrong/missing → 401/403;
a different `A2A-Version` → 400).

### `message:send` — initial batch
```json
{
  "message": {
    "messageId": "...", "role": "ROLE_USER",
    "parts": [{"mediaType": "application/vnd.ga5.invoice-claim-batch+json",
               "data": {"batchId": "...", "policyRevision": "...", "packages": [{"packageId": "...", "...": "..."}]}}]
  },
  "configuration": {"returnImmediately": false, "historyLength": 20, "acceptedOutputModes": [...]}
}
```
Response: `{"task": Task}` with `Task.state == "TASK_STATE_INPUT_REQUIRED"` and one artifact
Part (`application/vnd.ga5.invoice-action-proposals+json`) containing one proposal per
package: `{"packageId","actionId","action","facts":{"vendorName","invoiceNumber","amountMinor","currency"},"evidenceRefs":[...],"rationale":"60-1500 chars"}`.
`action` ∈ `{settle_invoice, request_approval, hold_invoice, reject_duplicate, open_exception}`.

### `message:send` — continuation (after your proposals are checked)
```json
{
  "message": {
    "messageId": "new id", "taskId": "exact task id", "contextId": "exact context id", "role": "ROLE_USER",
    "parts": [{"mediaType": "application/vnd.ga5.invoice-action-results+json",
               "data": {"batchId": "...", "results": [{"packageId","actionId","action","outcome": "ACCEPTED"|"REJECTED","receiptNonce"}]}}]
  }
}
```
Response: `Task.state == "TASK_STATE_COMPLETED"`, with an added receipts artifact
(`application/vnd.ga5.invoice-action-receipts+json`) whose `executions` array contains only
the `ACCEPTED` results, each bound to the persisted proposal's `facts`/`evidenceRefs`.

### Durability guarantees
- **Dedup by `(Bearer principal, messageId)`**: exact replay of the same message → byte-identical
  cached response, no re-triage. Same `messageId` with *different* semantic content → **409**
  (`IDEMPOTENCY_CONFLICT`). `configuration` is excluded from the fingerprint.
- **Stable-core reuse**: proposals are cached by package content fingerprint — unchanged
  packages across batches reuse the cached decision, no re-triage.
- **Tenant isolation**: tasks are strictly scoped to the `(email, token)` principal that
  created them — `GET`/`cancel` for another principal's task returns **404** (never reveals
  whether the ID exists).
- **Cancel**: only affects a non-terminal task; canceling an already-completed task is a
  no-op that returns the completed state (never both `COMPLETED` and `CANCELED`).

---

## 10. Q11 — Observable Incident-Response Agent

A durable diagnose → dispatch → (approval-gate) → effect agent that exports a receipt-
correlated OTLP trace. **Requires an AIPipe token** (embedded in the URL, same as Q4/Q9/Q10).

**Routes** (under your tenant base `https://<host>/ga5/<email>/<TOKEN>`):
```
POST {base}/v2/incidents
POST {base}/v2/incidents/{runId}/receipts
GET  {base}/v2/incidents/{runId}
```

### `POST /v2/incidents` — start a run
```json
{
  "profile": "ga5-incident-agent/v2", "runId": "stable opaque id",
  "agentName": "incident-response", "publicMarker": "safe telemetry marker",
  "sensitive": {"accessToken": "never export", "privateNote": "never export"},
  "incident": {"incidentId": "...", "title": "...", "service": "...", "severity": "SEV-1",
               "transcript": "evidence-tagged lines like [ev_1] ...", "allowedRootCauses": ["..."]},
  "toolCatalog": [{"name": "...", "description": "...", "inputSchema": {}}],
  "policy": {"maximumDiagnostics": 3, "effectTools": ["..."],
             "approvalRequiredFor": ["rollback_deployment", "disable_feature"], "doNotExport": ["..."]}
}
```
Response (always `status: "waiting"` at this point):
```json
{
  "runId": "...", "status": "waiting",
  "diagnosis": {"rootCause": "one allowed value", "evidence": ["ev_...", "ev_..."]},
  "dispatches": [{"actionId","callId","phase":"diagnostic","toolName","arguments","evidence","attempt":1,"traceparent":"00-<trace id>-<CLIENT span id>-01"}],
  "approvals": []
}
```
1-3 diagnostic calls are dispatched together (fan-out). If an incoming `traceparent` header is
valid, its trace is continued; otherwise a fresh trace is created.

### `POST /v2/incidents/{runId}/receipts` — post outcomes and/or approvals
```json
{ "receiptId": "stable id", "outcomes": [{"actionId","callId","attempt":1,"status":200,"resultClass":"diagnosis_confirmed","nonce":"..."}] }
```
- **503** → exactly one retry (new `attempt`, new CLIENT span). **`status:0, errorType:"timeout"`**
  → that diagnostic fails and its dependent effect is suppressed (reported in `suppressed`).
- Once evidence is confirmed, exactly one effect is chosen. If it's in `approvalRequiredFor`,
  the response instead carries a pending approval (no effect dispatch yet):
  ```json
  {"status":"waiting","dispatches":[],"approvals":[{"approvalId","actionId","toolName","argumentsDigest"}]}
  ```
  `argumentsDigest` is SHA-256 over recursively key-sorted compact JSON of the effect's arguments.
  Approve via the same receipts endpoint:
  ```json
  { "receiptId": "...", "approvals": [{"approvalId":"exact pending id","decision":"approved","nonce":"..."}] }
  ```
  After approval, the effect is dispatched with matching `approvalId`/`approvalNonce`.
- Once the effect's own outcome is posted, the run finalizes:
  ```json
  {
    "runId": "...", "status": "completed" | "failed",
    "diagnosis": {"rootCause","evidence"}, "chosenEffect": "scale_service", "suppressed": [],
    "actionLog": ["every dispatch exactly as issued"],
    "receiptLog": ["every outcome/approval receipt, in order"],
    "otlp": {"resourceSpans": [{"scopeSpans": [{"spans": ["..."]}]}]}
  }
  ```

### Durability & correctness guarantees
- Exact replay of `POST /v2/incidents` (same `runId` + same `incident`/`policy`/`toolCatalog`) →
  byte-identical cached response, no re-diagnosis. Changed content under the same `runId` → **409**.
- Exact replay of an identical receipt → byte-identical cached response. The same `receiptId`
  with different content → **409**. A receipt for a non-pending call → **400**.
- **`GET`** returns the current persisted state at any point in the lifecycle.
- **Redaction**: `sensitive.*`, the transcript, prompts, tool arguments/results, and
  authorization material are never present anywhere in the response or the OTLP spans —
  `gen_ai.tool.call.arguments`/`gen_ai.tool.call.result` are deliberately omitted.
- **OTLP shape**: numeric `SpanKind` (`INTERNAL=1, SERVER=2, CLIENT=3`), unique nonzero
  lowercase-hex trace/span IDs, every span carries `ga5.run.id`/`ga5.public.marker`, the model
  span carries `gen_ai.operation.name="chat"` + `gen_ai.request.model`, each tool's logical
  `execute_tool` span carries `ga5.action.id`/`gen_ai.tool.name`/`gen_ai.tool.call.id`, each
  physical attempt's CLIENT span carries `ga5.attempt`/`ga5.receipt.id`/`ga5.receipt.nonce`/
  `http.request.resend_count`, `incident.join` links every fanned-out diagnostic span, and
  `approval_gate` records the approval ID/nonce.

---

## 11. Quick client snippet

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
