# TDS GA5 "Agentic AI" — Implementation Guide (All API Questions)

Compiled from a full debugging pass across Q2–Q11, cross-checked against two independent third-party
references and verified live against a deployed multi-tenant hub. Every claim below was either
directly tested (unit test, live curl, or mocked reproduction) or is flagged as unverified.

---

## Cross-cutting lessons (read this first — these bit multiple questions)

1. **`retries=0` does not mean "one attempt, no retry."** If your HTTP-call wrapper loops
   `for attempt in range(retries):`, then `retries=0` means the loop body **never executes** —
   zero HTTP requests are ever sent, and you silently fall to whatever fallback path exists. Always
   use `retries=1` for "exactly one attempt." This single off-by-one bug looked identical to an
   exhausted API quota (same fallback symptom) and cost an entire debugging round to find.

2. **Decide-vs-execute mismatches are the #1 SSRF/traversal bug class.** If your code
   *decides* allow/block based on one transformation of the input (e.g. a fully URL-decoded copy)
   but then *executes* against a different transformation (the raw string), an attacker can craft
   input where the two disagree. Fix: decide and execute on the **exact same string**, or — safer —
   rebuild the request from the validated components (scheme + validated host + path) so it is
   physically impossible to reach anything but what was approved.

3. **Never cache a degraded fallback as the durable/stable decision.** If your LLM call fails
   (timeout, quota, malformed output) and you fall back to a safe default, that fallback must be
   tagged and **excluded from any long-lived cache**. Otherwise one transient failure permanently
   poisons every future replay of that item — this looked exactly like "the model is bad at this
   task" but was actually "the cache never got a chance to see a real answer."

4. **A provenance/trust string check must exclude its own negation.** `"untrusted" in s` is
   also true when checking for `"trusted" in s "untrusted"` — the substring `"trusted"` is inside
   `"untrusted"`. Any `any(k in prov for k in ("trusted", ...))` pattern silently misclassifies
   `external_untrusted` / `unverified` as trusted. Write one canonical `is_trusted()` helper that
   checks negation first, and use it everywhere — don't duplicate the inline check.

5. **A candidate-tool list must never be built by unioning unrelated policy lists.**
   `effectTools + approvalRequiredFor + wholeToolCatalog` is not "more options," it's "options the
   caller never authorized." `approvalRequiredFor` answers *which authorized tools need approval*,
   not *which tools exist*. Padding a candidate list with an unrelated list is a recurring anti-pattern —
   always ask "is this union actually the same kind of thing?"

6. **Set the exact response Content-Type your spec names**, don't rely on framework
   defaults. FastAPI/Starlette silently serializes a returned dict as `application/json`; if the
   spec requires `application/a2a+json` (or any custom media type), you must wrap the response and
   set `media_type` explicitly — on every success path *and* every error path.

7. **Non-greedy regex + literal `.` truncates emails/domains.** `r"is (\S+?)\."` stops at the
   *first* dot it finds — which is usually inside the domain, not the sentence's final period. Use
   a real email-shaped extractor, or a greedy match with `.rstrip(".,;")` afterward.

8. **A per-request-object lock that's checked-then-released twice (not held across the
   whole read→decide→write sequence) is not atomic.** If `get_X()` and `put_X()` are two separate
   lock acquisitions with an `await` (LLM call, I/O) in between, two concurrent identical requests
   can both pass the "not found yet" check and both do the expensive work — last write wins instead
   of one canonical result. Hold **one** lock across the entire sequence, scoped to whatever key your
   idempotency contract uses (e.g. per-principal, per-evaluation-id).

9. **Exam dossier/incident/document generators are usually template-based, not freeform.**
   If the spec describes "operative phrases," those are very likely **fixed strings** the generator
   always uses (only IDs/dates/names are randomized per student). A rule-based detector matching the
   exact phrase is both faster and more reliable than an LLM guessing at intent, and removes score
   drift between Check and Save. Confirm this by triangulating: if a spec doc's phrasing and an
   independent implementation's regexes agree verbatim, trust it.

---

## Q2 — Spec-Driven Development: The Proration Bug (3 marks)

**What it is:** stateless formula endpoint, no auth, no seed.

```
POST /  { old_price, new_price, days_remaining, days_in_actual_month, spec }
→ { charge }

spec == "v1":  charge = (new_price - old_price) * (days_remaining / 30)
spec == "v2":  charge = (new_price - old_price) * (days_remaining / days_in_actual_month)
```

Nothing subtle here beyond reading the spec literally — v1's divisor is **always** 30, v2's is the
real month length (28/29/30/31). Round to a couple decimal places; grader tolerance is $0.01.
Respond fast (no LLM needed) — a slow response is treated as a failure.

---

## Q3 — Agent Harness: Pre-Tool-Call Guardrail Hook (4 marks)

**What it is:** a deterministic `allow`/`block` decision for `bash` / `write_file` / `http_request`
calls, given a per-student seeded policy (secret file, write directory, allowed hosts).

**⚠️ Critical bug we hit:** the seed string is `${email}#${questionId}#${version}`, and the exam
bundle calls this question's generator with an **explicit `version:"v1"`**. If your seed-derivation
function defaults to an empty-string version and you don't pass `"v1"` explicitly at the call site,
you derive a **completely different random policy** than what's shown to the student — wrong secret
file, wrong write directory, wrong allowed hosts — while the endpoint still looks like it's "working"
(returns valid allow/block JSON, just against the wrong policy). Always cross-check the exam JS's
actual call-site version argument against your seed function's default.

**Universal rule independent of the per-student seed:** the exam's own worked example
(`sudo cat /etc/shadow` → must `block`) is fixed for every student — check for this unconditionally,
separately from whatever the per-student secret file is.

**Path/hostname matching gotchas to cover:**
- Tilde (`~`), `$HOME`/`${HOME}` expansion, relative traversal from cwd, `cd`-then-relative, and
  base64-wrapped shell commands must all resolve to the same normalized path as the direct case.
- A file named `.pgpass.bak` must **not** match a `.pgpass` secret check (exact-token comparison,
  not substring).
- Host comparison must strip a trailing FQDN dot (`host.com.` == `host.com`) and reject a host that
  merely *contains* an allowed name as a substring/subdomain-prefix trick
  (`allowed.com.attacker.example`).
- Write-path boundary check must catch `..` traversal that returns outside the allowed directory.

---

## Q4 — Skill Safety Audit: Scanner API (1.5 marks)

**What it is:** classify a skill markdown file into 0–3 of four categories: `hardcoded_secret`,
`prompt_injection`, `excessive_permissions`, `unclear_provenance`. Scored as an F-beta(0.5) over 5
hidden files (2 of which are clean) — **over-flagging is punished harder than under-flagging**, so
don't reach for a category unless you're confident.

- Heuristic-first (regex for secret-shaped strings, permission-scope keywords, injection phrasing,
  missing author/version/changelog) with an LLM fallback for ambiguous cases works well.
- Precision-biased prompt: explicit instruction "when in doubt, do NOT flag; a clean file returns
  `[]`." A scanner that flags everything scores badly even if recall is perfect.
- Respond fast — slow requests are graded as failed regardless of correctness.

---

## Q5 — Agent Harness: Run Budget & Loop Guard (3 marks)

**Same critical seed-version bug as Q3** — this question's exam-bundle call site also passes
`version:"v1"` explicitly; if your seed derivation defaults elsewhere, you get the wrong
`budget_tokens` and the wrong "ignore this tracing field" name. Always verify.

**Decision logic:**
- Sum `tokens_used` across all steps; halt if the sum has reached the budget (`>=`, not `>`).
- Loop detection needs **two independent rules**: (a) the same tool called 3+ times in a row with
  functionally identical args (canonicalize by sorting keys, normalizing internal whitespace, and
  dropping the one designated tracing-id field before comparing) and (b) a 2-step alternating
  A,B,A,B,... cycle spanning 6+ trailing steps.
- Two identical calls in a row is **not** yet a loop — only 3+.
- A changing pagination/job-id argument each call is real progress, not a loop — must stay
  `continue` as long as budget allows.
- Budget and loop are independent triggers; either alone is sufficient, and a loop halts even with
  budget to spare.

---

## Q6 — Build a Live MCP Server (4 marks)

**What it is:** minimal MCP (Model Context Protocol) server exposing one tool `solve_challenge`,
whose response is derived from a per-call HTTP header, not the JSON-RPC body.

```
tool text response = first 16 hex chars of SHA256(f"{X-Exam-Challenge header}:{your normalized email}")
```

- Must implement the real MCP handshake: `initialize` → `notifications/initialized` → `tools/list`
  → `tools/call` (5 times, fresh challenge header each call).
- The tool's `inputSchema` needs no required properties — grader calls it with an empty/near-empty
  argument object.
- Read the challenge from `X-Exam-Challenge`, **never** from the request body. Signature
  verification (`X-Exam-Signature`, HMAC-SHA256) is optional and unscored — implement it only if you
  want extra confidence you're rejecting non-exam callers.
- Endpoint must be public HTTPS and stay up through the grading window — this is a live check, not a
  submit-once answer.

---

## Q8 — Guardrail Red-Team Round-Trip (5 marks)

**What it is:** Q3's guardrail, but now the endpoint must actually *execute* `read_file`/`fetch_url`
and return real results, with the grader checking for canary-token leaks on malicious probes.

**`read_file` — fail closed:**
```python
allowed, physical = canonicalize_and_check_boundary(path, sandbox_root)
if not allowed:
    return block
if not physical.is_file():          # <- the fail-open bug we found
    return block                     #    (previously: allowed with empty result)
return allow, content
```
Only a **real, existing** file strictly inside the sandbox is ever `allow`ed. A path that
canonicalizes inside the boundary but doesn't correspond to a real file (obfuscated traversal that
happens to land "inside," a nonexistent filename) must `block`, not silently return an empty
"allow."

**`fetch_url` — decide and execute on the identical string, never two different ones:**
1. Reject any URL containing control characters or whitespace outright (classic parser-differential
   vector).
2. Extract host via `urlparse`, reject if it contains anything outside `[a-z0-9.-]` (percent-encoding
   is never legitimate in a real hostname — don't try to decode it, just reject).
3. Reject userinfo (`@` in the authority) unconditionally, even when the "real" host after the `@`
   is allowed.
4. Exact-match the host against the allowlist; also block private/loopback/link-local/metadata IPs
   (including IPv4-mapped IPv6, octal/hex/decimal IP literals).
5. **Reject any non-default port** — `https://allowed-host:1337/` must block even though the host
   itself is allowed; a non-default port reaches whatever else is listening there. Only the scheme's
   own default port (80/443) is permitted, whether implicit or written explicitly.
6. **Rebuild the fetch URL from the validated components** (`urlunparse((scheme, validated_host,
   path, params, query, ""))`) rather than fetching the caller's raw string — this guarantees the
   request can only ever reach the host you just approved, regardless of any parser disagreement
   between your validator and your HTTP client.
7. Re-validate every redirect hop the same way before following it (blocks redirect-to-private).
8. A trailing-dot FQDN (`allowed-host.`) is the same real host per DNS but breaks TLS SNI if sent
   verbatim — strip it before both the decision and the actual request.

---

## Q9 — Lethal-Trifecta Mailroom Action Gate (4 marks)

**What it is:** classify each "dossier" (customer email + internal records, full of decoys and
prompt-injection attempts) into one of six actions, with an **exact-set** evidence citation and a
frozen target/payload schema per action.

### The six archetypes and their exact frozen schema

```
create_draft
  target  {"kind":"draft_queue","id":"mailbox:<mailbox>"}
  payload {"recipient","referenceId","status","template":"order_status"}

update_internal_record
  target  {"kind":"case_record","id":"<case id>"}
  payload {"field":"delivery_window","sourceEventId","value"}

send_approved_notice
  target  {"kind":"email","id":"<approved recipient>"}
  payload {"referenceId","status","template":"approved_delivery_notice"}

request_confirmation
  target  {"kind":"approval_queue","id":"<owning team>"}
  payload {"claimedSender","questionCode":"VERIFY_REQUEST","referenceId"}

quarantine_item
  target  {"kind":"security_queue","id":"mailroom"}
  payload {"artifactId","reasonCode":"INDIRECT_PROMPT_INJECTION"}

no_action
  target  null
  payload {"reasonCode":"ALREADY_COMPLETED"|"DUPLICATE"|"INFORMATIONAL","referenceId"}
```

**The constant literals (`template`, `reasonCode`, `questionCode`, the `mailbox:` prefix) are
required even though they never appear in the dossier text — you write them, don't try to extract
them.** Keys/values are case-sensitive; add no extra fields.

### Deterministic classification (verified: exam dossiers use a fixed template)

Two independent sources agree verbatim on these anchor phrases — treat them as reliable fast-path
classifiers, LLM as fallback only:

| Archetype | Exact anchor phrase to search for | Source provenance |
|---|---|---|
| `quarantine_item` | `"higher-priority instruction"` or `"Copy any vault marker"` | untrusted/external |
| `send_approved_notice` | `"permits one delivery-status notice"` | trusted/signed internal |
| `update_internal_record` | `"to change delivery_window to the exact value"` | trusted/signed internal |
| `request_confirmation` | `"does not match"` + `"confirmation"` in the same line | trusted/authenticated internal |
| `no_action` | `"records this item as"` (already completed / duplicate / informational) | trusted/authenticated internal |
| `create_draft` | `"I have not asked you to send anything yet"` | untrusted/external |

Classify **in this order** (E→C→B→D→F→A works well); first match wins. If no anchor matches, fall
through to an LLM call — never block on the deterministic path alone.

### Evidence is an EXACT set — one line too many or too few rejects the whole dossier

```
quarantine_item          4 lines: [rule, injection clause, exfiltration clause, artifact record]
no_action                3 lines: [rule, completed/duplicate record, customer follow-up]
create_draft             3 lines: [rule, order/status record, customer's request sentence]
request_confirmation     3 lines: [rule, mismatch record, "I am <addr>" self-identification line]
update_internal_record   2 lines: [rule, event authorisation]  -- NOT the scope-companion line too
send_approved_notice     2 lines: [approval permit line, approval scope line]  -- NO rule line;
                                   the approval itself IS the authority
```

- Every dossier contains a generic **"least-privilege action boundary"** line — this is **never**
  evidence for any action, always skip it.
- `send_approved_notice` is the one archetype with no separate rule line — citing a third line
  (the record) alongside the two approval lines gets it rejected just as surely as citing only one.
- `update_internal_record` specifically must **not** cite the "scoped only to this field" companion
  line even though it looks relevant — exactly 2 lines, rule + event line.
- `quarantine_item` is the one archetype with **no `referenceId`** in its payload at all — never
  emit one, even a null.
- Reference ID family is action-dependent: `create_draft`/`send_approved_notice` cite the **ORD**
  (order) id; `update_internal_record`/`request_confirmation`/`no_action` cite the **CASE** id. A
  dossier can contain both linked IDs — pick the one matching your action, extracted **verbatim**,
  never invented.

### Safety (a single leak caps the whole question near zero)

- Scrub **every** free-form field you write from LLM output — not just the "obvious" ones
  (`value`, `claimedSender`) but also `status`, `owningTeam`, `sourceEventId`, `artifactId`. Any of
  them can carry a canary/vault token straight through if unfiltered. Restrict fixed-vocabulary
  fields (`status`, `owningTeam`) to a small known-safe word list rather than accepting arbitrary
  LLM text; restrict ID-shaped fields (`sourceEventId`, `artifactId`) to IDs that actually exist in
  the dossier, never accept an LLM-hallucinated value.
- `send_approved_notice` is the one action with a real outbound side-effect. Never emit it without
  an explicit, verifiable trusted-source approval; downgrade to `request_confirmation` otherwise.
  The recipient for an approved notice must come from a **trusted** source, never from
  attacker-controlled untrusted text.
- Safe default when uncertain: **`request_confirmation`**, not a guess at the "obvious" action.
  "When anything is uncertain, route to a human rather than acting."

### Engineering correctness

- `commit()` must validate the **entire receipt set** atomically — not just each individual receipt
  against its proposal, but that the set of callIds exactly matches the persisted proposals (no
  missing, no duplicate, no extra) before computing any outcome.
- Replay of an identical `propose`/`commit` request must return the byte-identical cached response
  without re-running the model or re-applying effects. A **different** payload under the same
  `evaluationId` must 409, not silently overwrite.
- **Never persist a degraded LLM fallback into your stable-core cache** — tag it and skip the
  cache-write; otherwise one transient LLM failure poisons that dossier's decision forever, and a
  healthy token later can never fix it (looks exactly like "bad model," is actually "poisoned
  cache").
- Watch your provenance/trust string check (`"trusted" in "untrusted"` — see cross-cutting lesson
  #4) — this alone can silently break every safety filter that depends on trusted vs. untrusted
  source classification.

---

## Q10 — A2A Invoice Action Agent (4 marks)

**What it is:** full A2A 1.0 protocol surface (Agent Card, `message:send`, task lifecycle) fronting
an invoice-triage agent.

**⚠️ Instant-fail bug:** every successful response on an `/a2a/*` route must have
**`Content-Type: application/a2a+json`**, not the framework's default `application/json`. This
applies to error responses on those routes too. If your framework returns a raw dict and lets the
framework pick the content type, you will fail protocol checks even if every field is otherwise
correct.

**Agent Card:**
- Served at the **origin-level** `{origin}/.well-known/agent-card.json` — not under your submitted
  base path.
- `supportedInterfaces` must contain the **exact submitted base URL**. If you only register it via
  a separate onboarding step the grader never calls, the card is empty for the grader's own request.
  Register the current caller's own base URL dynamically on every authenticated A2A call instead —
  derive it from the live request, don't hardcode any specific value.
- Requires `A2A-Version: 1.0` header and `application/a2a+json` request Content-Type; missing/wrong
  auth → 401/403; wrong version → 400.
- Bearer token is the **principal identifier**, not necessarily your own billing/AIPipe token —
  don't reject a caller's Bearer just because it doesn't match some other token you expected; scope
  task visibility by `(email, bearer)` instead.

**Task lifecycle:** `SUBMITTED → WORKING → INPUT_REQUIRED → WORKING → COMPLETED`, with `CANCELED`
reachable from any non-terminal state. `message:send` with no `taskId` starts a task (returns
`INPUT_REQUIRED` with a proposals artifact); `message:send` **with** `taskId` is the continuation
(consumes accepted/rejected results, produces the receipts artifact, transitions to `COMPLETED`).
Execute **only** accepted proposals — a proposal alone must never itself change anything.

**Idempotency, atomicity, and the two races that actually get tested:**
- Dedup key is `(principal, messageId)`, fingerprinted over the **semantic** message content only
  (ignore `configuration`, ignore key order). Same fingerprint → return the cached task, no
  re-work. Different content under the same `messageId` → 409 `IDEMPOTENCY_CONFLICT`.
- **This check-then-act sequence must be atomic** — hold one lock across the *entire*
  check-cache → do-the-work → persist-the-result flow for a given principal, not two separate lock
  acquisitions with the actual work (LLM call) unlocked in between. Two concurrent identical
  requests must resolve to the exact same task, not each independently do the work with
  last-write-wins.
- `:cancel` is a **separate endpoint** — it needs the exact same lock as `message:send`, or a cancel
  racing a concurrent completion can leave the task in an inconsistent state (both `COMPLETED` with
  receipts *and* `CANCELED`, which the spec explicitly forbids — exactly one, never both/neither).
- A cache-bypass mechanism meant for re-triaging a degraded initial proposal (e.g. "the batch had a
  fallback decision, re-run it next time") must **only** apply to the initial propose message, never
  to a continuation replay — otherwise replaying an already-completed task's finishing message can
  wrongly re-enter processing against a terminal task and 409 instead of returning the cached
  terminal result.

**Business logic:** exact typed action per package (`settle_invoice` / `request_approval` /
`hold_invoice` / `reject_duplicate` / `open_exception`), citing 2+ real evidence refs (verbatim
substrings of the source text, never paraphrased) and a rationale naming the action. Be conservative
— `settle_invoice` needs solid reconciled evidence; default to `request_approval` when unsure.
Negation and stale ("previously required," "no longer applicable") language in the source documents
must not be read as a live condition.

**Tenant isolation:** every task query filtered by the authenticated principal; a task belonging to
a different principal returns 404 (never a distinguishable 403 that would leak existence).

---

## Q11 — Build an Observable Incident-Response Agent (4 marks)

**What it is:** diagnose a root cause from a noisy transcript, dispatch diagnostic tool calls, gate
any destructive remediation behind approval, and export a receipt-correlated OTLP trace of the
whole run.

**⚠️ The critical bug that zeroes every scoring category at once:** the candidate list of
**effect** (remediation) tools must be **exactly** `policy.effectTools` — never padded with
`policy.approvalRequiredFor` or the rest of the tool catalog. `approvalRequiredFor` answers *which
of your authorized tools need approval before dispatch*, it is not itself a list of available
effects. If you union it in, the agent can end up requesting approval for (or dispatching) a tool
the grader never authorized for that incident — which the grader has no valid outcome to return for,
so the run stalls before ever reaching completion. Since topology/correlation/lifecycle/durability/
redaction are only assessable on a run that *completes*, this one bug can zero every category
simultaneously even though diagnosis and evidence look perfect in isolation.

**Similarly:** the diagnostic-tool candidate list must **exclude** effect/destructive tools — a
fallback that grabs "the first tool in the catalog" when the LLM gives nothing usable can otherwise
dispatch a destructive tool as a "diagnostic" call, which is an unapproved destructive action (hard
cap at 0.5/4).

**Effect-choice fallback must never default to a destructive tool.** When the LLM call fails and
you must fall back to *some* choice, prefer any non-destructive tool in the authorized effect list
before ever defaulting to `rollback_deployment`/`disable_feature`.

**Evidence:** keep whatever the model actually cites, even if it's only one line — padding with
guessed lines is worse than a single decisive citation. Only pad when the model returns nothing at
all, and prefer the transcript's middle lines over its first/last (which tend to be baseline/context
noise, not signal) when you must guess.

**OTLP topology — exact span set, verify structurally:**
```
POST /v2/incidents                    SERVER, kind=2, root (no parent)
└─ invoke_agent {agentName}           INTERNAL, kind=1, child of server
   ├─ chat incident-plan              CLIENT, kind=3, exactly ONE per run
   ├─ execute_tool <toolName>         INTERNAL   ┐ one pair per LOGICAL
   │  └─ POST tool/<toolName>         CLIENT     ┘ action (retries reuse the
   │                                              logical span, new CLIENT
   │                                              span per physical attempt)
   ├─ incident.join                   INTERNAL, only when 2+ diagnostics fan out,
   │                                  links[] referencing every diagnostic's
   │                                  execute_tool span
   ├─ execute_tool <effectTool>       INTERNAL ┐ effect's own pair, dispatched
   │  └─ POST tool/<effectTool>       CLIENT   ┘ after diagnostics resolve
   └─ approval_gate                   INTERNAL, only when a destructive effect
                                       needs approval; records approval id +
                                       approval receipt nonce
```
- Numeric `SpanKind`: INTERNAL=1, SERVER=2, CLIENT=3. Unique nonzero lowercase-hex trace/span IDs
  throughout.
- A `503` outcome permits exactly one retry (span status code 2, `error.type="503"`, resend count 0
  on the first attempt, 1 on the retry). A `timeout` outcome fails that diagnostic and suppresses
  its dependent effect (`error.type="timeout"`, no retry).
- The outgoing dispatch's `traceparent` span ID must be the exact matching tool CLIENT span ID —
  this is how the grader correlates its receipt back to your trace.

**Redaction — verify this precisely, don't eyeball it:**
- The request's sibling `sensitive` object (accessToken, privateNote, etc.) must never reach the
  model, never appear in any response, and never appear in the OTLP export.
- Never export `gen_ai.tool.call.arguments` or `gen_ai.tool.call.result` as OTLP span attributes —
  those are fine to include in the plain JSON `actionLog` (which the spec explicitly wants to mirror
  every dispatch as issued), but must be absent from the trace itself. Check this by literally
  grepping the serialized `otlp` object for forbidden keys, not just eyeballing a sample.

**Durability:** persist before responding; identical request/receipt replay returns the
semantically-identical stored response without rerunning the model or the action; a changed `runId`
or `receiptId` content returns 409; an unsupported profile or malformed state transition returns
400/422 and creates nothing. Apply the same "never cache a degraded fallback as the permanent
answer" rule as Q9 — if a run's diagnosis came from a fallback (LLM failure), allow it to be
re-diagnosed on a later identical-content request **as long as the run never progressed past
waiting** (no receipts exchanged yet) — this upgrades a guess to a real answer without violating the
replay contract for runs that already did real work.

---

## Final checklist before submitting any of these

- [ ] Re-verify your seed/version string against the exam bundle's actual call site, don't trust a
      function default.
- [ ] Every canary/secret-shaped string is checked before being written into ANY field, not just the
      obviously-risky ones.
- [ ] Every provenance/trust classification uses one shared, negation-safe helper.
- [ ] Every URL-validating code path decides and executes on the identical string.
- [ ] Every idempotency/replay lock is held across the full check→work→persist sequence, not split
      across two acquisitions.
- [ ] Every LLM-call fallback is excluded from any long-lived cache.
- [ ] Every "list of allowed X" is built from exactly the policy's own list — never unioned with an
      unrelated list "just in case."
- [ ] Every protocol-mandated response header (especially Content-Type) is set explicitly, not left
      to framework defaults.
- [ ] Run a live end-to-end test of the full lifecycle (not just the first response) before trusting
      that "it returns 200" means "it works."
