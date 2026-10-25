# T3-2026 GA3 — agent servers

Exam source: `exam-tds-2026-09-ga3.js` (version `v3`). Three 4-mark live servers, all served by the GA5 hub
under one tenant base URL `https://<host>/ga5/<email>/<aipipe-token>`:

| Exam Q | Question id | Submit | Engine |
|---|---|---|---|
| Q2 | `q-a2a-durable-delegate-server-v2` | `<base>/a2a/` | `T22026/GA5/a2a_agent.py` (ours) + `refimpl/a2a/hypemonk_q10.py` readers for distributed audit packages |
| Q3 | `q-taint-aware-agent-executor-server-v2` | `<base>/mailroom` | `refimpl/mailroom` (reference) |
| Q4 | `q-agent-trace-integrity-server-v2` | `<base>` | `refimpl/incident` (reference) |

## Reference engines (`refimpl/`)

`refimpl/mailroom` and `refimpl/incident` are vendored from a peer reference solution
(`tds-ga3/router/q03-safe-ai-mailroom` and `q04-observable-incident-triage`) that scored full marks on the live
grader. Changes on import: package-relative imports, SQLite and logs in the temp dir
(`GA3_MAILROOM_DB`, `GA3_INCIDENT_DB`), request logging off unless `GA3_INCIDENT_LOG=1`. Both are deterministic;
the incident planner only calls a model (Gemini via `GEMINI_API_KEY`) when its rules find no cause.

`T22026/GA5/app.py::_ReferenceEnginesASGI` routes `<base>/mailroom` and `<base>/v2/incidents…` to them.
Set `GA3_REF_ENGINES=0` to fall back to the original T22026/GA5 handlers.

## Verification

`tests/test_t32026_ga3_refengines.py` replays 43 requests captured from a live Check
(`tests/fixtures/t3ga3_incident_grader_capture.jsonl`) through the gateway, remapping grader IDs, and
requires identical diagnoses, tools, arguments, evidence, approvals, effects and states. Run the suites with the
deployed pins too (`fastapi==0.115.0`), see `hf_space/requirements.txt`.

Grader traffic for any tenant is viewable privately at `<base>/debug/captures` (`T22026/GA5/capture.py`).

## A2A audit readers

`refimpl/a2a/hypemonk_q10.py` is vendored from https://github.com/HypeMonk/TDS-GA5 (`q10.py`, provider-free). Only its
decision readers are used (`distributed_decision`, `semantic_distributed_decision`, `decisive_paragraph`): ours decides the
core layout, these decide the fresh-audit distributed packages, the model handles anything neither reads.
`tests/fixtures/t3ga3_a2a_distributed_cases.json` holds its regression packages. An earlier rule set (same-supplier-and-total
counts as duplicate) was dropped: it contradicts "a payment for a different invoice is not a duplicate".
