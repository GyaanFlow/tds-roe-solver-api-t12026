# T3-2026 GA1 API Hub — Implementation Guide

This guide covers the three server questions assigned to the T3 GA1 API project: effective configuration, the per-student Ledger Agent, and the MCP challenge server. The deployable FastAPI application is mounted by `hf_space/app.py` at `/ga1`; its dashboard is `/ga1/`.

## 1. Local setup

From the repository root, install the dependencies in `hf_space/requirements.txt`, then start the complete gateway:

```powershell
python -m pip install -r hf_space/requirements.txt
python -m uvicorn hf_space.app:app --host 0.0.0.0 --port 7860
```

Open `http://localhost:7860/ga1/`. The service endpoints and API reference are also available at `/ga1/docs`.

## 2. Tenant storage

The service stores each normalized exam email's `quizSign` in a small tenant record.

- For local development or one instance with a persistent disk, set `GA1_TENANT_DB_PATH` to a writable SQLite file on that disk. If unset, the database is created under the repository's `work/` directory.
- For multiple workers or replicas, set `GA1_REDIS_URL` to a shared Redis instance. Redis is already listed in `hf_space/requirements.txt`. All replicas must use the same Redis URL.
- Do not rely on a container's ephemeral filesystem for student configuration. A restart may remove a local SQLite database.

Example PowerShell configuration for a persistent single-instance deployment:

```powershell
$env:GA1_TENANT_DB_PATH = "D:\\persistent-data\\t32026-ga1.sqlite3"
python -m uvicorn hf_space.app:app --host 0.0.0.0 --port 7860
```

Keep Redis credentials and other secrets in the host's secret/environment configuration, never in source control.

## 3. Onboard a student

Use the dashboard setup form, or call:

```http
POST /ga1/onboard
Content-Type: application/json

{"email":"student@example.com","quiz_sign":"<active-session-quizSign>"}
```

The response includes the email-scoped routes. Use the exact returned URLs when exercising the service or submitting endpoints. The `quizSign` is required for Ledger discovery; the config and MCP endpoints do not depend on ledger data.

## 4. Endpoint contracts

| Question | Request | Expected behavior |
| --- | --- | --- |
| Config precedence | `GET /ga1/{email}/effective-config?set=port=8123&set=debug=yes` | Applies repeated CLI overrides in order, coerces numeric/boolean fields, maps `num_workers` to `workers`, and always masks `api_key`. |
| Ledger discovery | `GET /ga1/{email}/ledger/discover` | Fetches the signed student-specific schema and returns resource paths and field names, not ledger rows. |
| Ledger answer | `POST /ga1/{email}/ledger/answer` with `{"question":"..."}` | Returns `{"answer": ...}` for supported revenue, refund, product, customer, date, and region questions. Upstream and unsupported-question failures return explicit HTTP errors. |
| MCP server | `POST /ga1/{email}/mcp` | Supports `initialize`, `notifications/initialized`, `ping`, `tools/list`, and `tools/call` for the single `solve_challenge` tool. |

Each MCP tool call must include a fresh `X-Exam-Challenge` header containing 32 lowercase hex characters. The returned text is the first 16 lowercase hex characters of `SHA-256(challenge:normalized-email)`.

## 5. Dashboard and test bench

The dashboard runs real calls against the service:

1. Save the exam email and active `quizSign`.
2. Run the config override check.
3. Discover Ledger paths and fields, then submit a sample question.
4. Run MCP initialize, tools/list, and a fresh challenge call.

Run the offline regression suite before deployment:

```powershell
python -m compileall -q T32026/GA1
python -m pytest tests/test_t32026_ga1.py -q
```

These checks cover representative contracts and edge cases. They are not a substitute for running the official grader, probing each live student Ledger schema, or load-testing the actual deployment.

## 6. Scaling and operational notes

The SQLite backend is appropriate for a single instance with persistent storage. Redis is the shared tenant store for multi-instance deployments. Ledger discovery uses bounded outbound concurrency, short-lived per-process caching, response-size limits, and request timeouts. Cache entries are local to a worker, so a cache miss on another replica can repeat upstream discovery.

Before serving a large cohort, configure shared Redis and run a deployment-level load test with realistic distinct tenants and concurrent Ledger requests. Verify the exam upstream's rate limits and observed latency; the local tests do not establish a safe student count. Ledger field names and question wording may vary by student, so use the dashboard's schema manifest to investigate any unsupported response rather than treating a plausible numeric answer as verified.
