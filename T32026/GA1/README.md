# T3-2026 GA1 API Hub

This hub implements the three GA1 questions whose official September 2026 source asks the student to deploy a server:

| Exam question | Route | Contract |
| --- | --- | --- |
| Resolve 12-Factor Config Precedence | `GET /ga1/{email}/effective-config?set=key=value` | Student-seeded YAML/.env/OS layers, repeated CLI overrides, typed values, `num_workers` alias, masked `api_key` |
| The Ledger Agent | `POST /ga1/{email}/ledger/answer` | Accepts `{"question":"..."}` and responds with `{"answer":...}` |
| Build a Live MCP Server | `POST /ga1/{email}/mcp` | MCP initialize, tools/list, and tools/call for the required `solve_challenge` tool |

The dashboard is available at `/ga1/`. Save the exam email and paste that student's full signed Ledger `questionData` URL there. The hub validates its host, email, question ID, and root path, then stores only the signature for server-side discovery. Keep the signed URL private. The dashboard's discovery response contains endpoint/schema metadata only, not the private ledger rows.

## Tenant storage and scaling

Ledger discovery follows named links and retains top-level pagination parameters. For the Acme schema, it uses the complete NDJSON export instead of fetching 85 pages: newest `updated_at` per order ID, Asia/Kolkata business dates, paid-only revenue, and `usd_per_unit` currency conversion. Refund counts count current refunded orders; totals use Decimal arithmetic rounded to cents after summation.

Product names are matched against each student's current catalog and applied before aggregation, including distinct-customer and order-count questions. Customer counts count distinct customer IDs rather than products or purchases; named product constraints combine with region, date, and paid/refunded status filters.

Tenant configuration uses SQLite with transactions and WAL mode by default. Set `GA1_TENANT_DB_PATH` to a persistent mounted-volume path for a single-instance deployment. For multiple workers/replicas, set `GA1_REDIS_URL` to a shared Redis service; startup/read failures are reported instead of silently falling back to per-process memory. Do not use a container's ephemeral filesystem for persistent student configuration. Ledger upstream calls are concurrency-limited, bounded by timeouts, and cached briefly in each worker; the tenant store is shared when Redis is configured.

## Local startup

Install the root `hf_space/requirements.txt` dependencies, then start the gateway with `uvicorn hf_space.app:app --port 7860`. Open `/ga1/` for onboarding and the interactive request bench. API docs are available at `/ga1/docs`. Run the local contract and edge checks with `python -m pytest tests/test_t32026_ga1.py`.

## MCP behavior

The MCP route supports JSON-RPC `initialize`, `notifications/initialized`, `tools/list`, `tools/call`, and `ping`. The sole tool has no required input properties. Each call reads `X-Exam-Challenge` from the HTTP request headers and returns the first 16 lowercase hex characters of SHA-256 over `challenge:normalized-email`.

## Scope

The exam's other API-adjacent questions are not hosted services: the `httpbin` question asks the student to make an outbound HTTP request; the HTTP-header question reads a code from the exam's own response; and file/ZIP questions operate on downloadable artifacts. They are outside this API hub.
