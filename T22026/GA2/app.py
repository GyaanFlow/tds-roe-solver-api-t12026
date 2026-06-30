from __future__ import annotations

"""
T22026/GA2/app.py — Unified GA2 sub-application
Mounted at /ga2 by the root hf_space/app.py.

The root-level MultiTenantASGIMiddleware already rewrites paths and
populates scope["tenant_email"] before this app receives the request.

This app's HTTP middleware picks up that email and injects it into the
thread-local ContextVar so every handler can call current_email.get().
"""

import uuid
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

from T22026.GA2.shared.tenant import current_email
from T22026.GA2.Q01_metrics.main       import router as q1_router
from T22026.GA2.Q02_oauth.main         import router as q2_router
from T22026.GA2.Q03_config.main        import router as q3_router
from T22026.GA2.Q04_compose.main       import router as q4_router
from T22026.GA2.Q05_analytics.main     import router as q5_router
from T22026.GA2.Q06_observability.main import router as q6_router
from T22026.GA2.Q07_llm_tunnel.main    import router as q7_router
from T22026.GA2.Q08_llm_extract.main   import router as q8_router
from T22026.GA2.Q09_orders.main        import router as q9_router
from T22026.GA2.Q10_middleware.main    import router as q10_router

app = FastAPI(
    title="IITM TDS 2026-05 GA2 — Multi-Tenant API Hub",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# ---------------------------------------------------------------------------
# HTTP middleware — inject tenant email into ContextVar
# ---------------------------------------------------------------------------
@app.middleware("http")
async def _inject_tenant(request: Request, call_next):
    email = (
        request.scope.get("tenant_email")
        or request.query_params.get("email")
        or "student@example.com"
    )
    rewritten = request.scope.get("path", request.url.path)
    token = current_email.set(email)
    try:
        response = await call_next(request)
        # Record Q06 observability events
        if "/q6/" in rewritten or rewritten.endswith("/q6"):
            from T22026.GA2.Q06_observability.main import record_request
            req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
            record_request(rewritten, req_id, response.status_code)
        return response
    finally:
        current_email.reset(token)


# ---------------------------------------------------------------------------
# Sub-routers
# ---------------------------------------------------------------------------
app.include_router(q1_router,  prefix="/q1")
app.include_router(q2_router,  prefix="/q2")
app.include_router(q3_router,  prefix="/q3")
app.include_router(q4_router,  prefix="/q4")
app.include_router(q5_router,  prefix="/q5")
app.include_router(q6_router,  prefix="/q6")
app.include_router(q7_router,  prefix="/q7")
app.include_router(q8_router,  prefix="/q8")
app.include_router(q9_router,  prefix="/q9")
app.include_router(q10_router, prefix="/q10")


# ---------------------------------------------------------------------------
# Dashboard / status page
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def ga2_home():
    return HTMLResponse(_DASHBOARD_HTML)


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GA2 API Hub — TDS 2026-05</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #06080f;
      --surface:   #0d1117;
      --surface2:  #161b26;
      --border:    #21262d;
      --text:      #e6edf3;
      --muted:     #8b949e;
      --accent:    #7ee8a2;
      --blue:      #58a6ff;
      --purple:    #bc8cff;
      --orange:    #ffa657;
      --red:       #ff7b72;
      --yellow:    #e3b341;
      --grad1:     linear-gradient(135deg, #1a1f35 0%, #0d1117 100%);
    }

    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      overflow-x: hidden;
    }

    /* ----- HEADER ----- */
    header {
      padding: 2.5rem 2rem 1.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      border-bottom: 1px solid var(--border);
      background: var(--grad1);
      position: relative;
      overflow: hidden;
    }
    header::before {
      content: '';
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse 80% 60% at 50% -20%, rgba(126,232,162,.12), transparent);
      pointer-events: none;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(126,232,162,.1);
      border: 1px solid rgba(126,232,162,.3);
      color: var(--accent);
      border-radius: 99px;
      padding: 4px 14px;
      font-size: .75rem;
      font-weight: 600;
      letter-spacing: .04em;
      margin-bottom: 1rem;
    }
    .badge::before { content: '●'; font-size: .6rem; animation: pulse 2s infinite; }
    @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }
    header h1 {
      font-size: clamp(1.6rem, 4vw, 2.6rem);
      font-weight: 800;
      background: linear-gradient(135deg, #fff 0%, var(--accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    header p { color: var(--muted); margin-top: .5rem; font-size: .95rem; max-width: 560px; }

    /* ----- EMAIL LOOKUP ----- */
    .lookup {
      max-width: 900px;
      margin: 2rem auto;
      padding: 0 1.5rem;
    }
    .lookup-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1.4rem 1.8rem;
      display: flex;
      gap: 1rem;
      align-items: center;
      flex-wrap: wrap;
    }
    .lookup-card label { font-size: .85rem; color: var(--muted); white-space: nowrap; }
    .lookup-card input {
      flex: 1;
      min-width: 220px;
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: .55rem 1rem;
      color: var(--text);
      font-size: .9rem;
      font-family: 'JetBrains Mono', monospace;
      outline: none;
      transition: border-color .2s;
    }
    .lookup-card input:focus { border-color: var(--accent); }
    .lookup-card button {
      background: var(--accent);
      color: #06080f;
      border: none;
      border-radius: 8px;
      padding: .55rem 1.4rem;
      font-weight: 700;
      font-size: .9rem;
      cursor: pointer;
      transition: opacity .15s, transform .12s;
      white-space: nowrap;
    }
    .lookup-card button:hover { opacity: .85; transform: translateY(-1px); }

    /* ----- GRID ----- */
    .grid {
      max-width: 900px;
      margin: 0 auto 3rem;
      padding: 0 1.5rem;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1rem;
    }
    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 1.3rem 1.4rem;
      display: flex;
      flex-direction: column;
      gap: .6rem;
      transition: border-color .2s, transform .15s, box-shadow .2s;
      text-decoration: none;
      color: inherit;
      position: relative;
      overflow: hidden;
    }
    .card::before {
      content: '';
      position: absolute;
      inset: 0;
      background: var(--card-glow, transparent);
      opacity: 0;
      transition: opacity .25s;
    }
    .card:hover { border-color: var(--card-accent, var(--border)); transform: translateY(-3px); box-shadow: 0 8px 30px rgba(0,0,0,.4); }
    .card:hover::before { opacity: 1; }
    .card-header { display: flex; align-items: center; gap: .75rem; }
    .q-badge {
      font-family: 'JetBrains Mono', monospace;
      font-size: .72rem;
      font-weight: 700;
      background: var(--card-badge-bg, rgba(88,166,255,.12));
      color: var(--card-accent, var(--blue));
      border: 1px solid var(--card-accent, var(--blue));
      border-radius: 6px;
      padding: 2px 8px;
      white-space: nowrap;
    }
    .card h3 { font-size: .95rem; font-weight: 600; }
    .card p { font-size: .8rem; color: var(--muted); line-height: 1.55; flex: 1; }
    .endpoints { display: flex; flex-wrap: wrap; gap: 4px; margin-top: .3rem; }
    .ep-tag {
      font-family: 'JetBrains Mono', monospace;
      font-size: .68rem;
      background: var(--surface2);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 2px 7px;
      color: var(--muted);
    }
    .card-status {
      display: flex;
      align-items: center;
      gap: .5rem;
      font-size: .78rem;
      color: var(--muted);
      border-top: 1px solid var(--border);
      padding-top: .7rem;
      margin-top: .2rem;
    }
    .dot { width: 7px; height: 7px; border-radius: 50%; background: var(--accent); display: inline-block; animation: pulse 2s infinite; }

    /* ----- PARAM TABLE ----- */
    #params-section {
      max-width: 900px;
      margin: 0 auto 2rem;
      padding: 0 1.5rem;
      display: none;
    }
    .params-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
    }
    .params-header {
      background: var(--surface2);
      padding: .9rem 1.4rem;
      font-size: .85rem;
      font-weight: 600;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: .5rem;
    }
    .params-header span { color: var(--accent); font-family: 'JetBrains Mono', monospace; }
    .params-body {
      padding: 1rem 1.4rem;
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
      gap: .5rem 1.5rem;
    }
    .param-row { display: flex; flex-direction: column; gap: 2px; }
    .param-label { font-size: .73rem; color: var(--muted); }
    .param-value {
      font-family: 'JetBrains Mono', monospace;
      font-size: .8rem;
      color: var(--accent);
      word-break: break-all;
    }
    .spin { display: inline-block; animation: spin .8s linear infinite; }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* ----- DOCS FOOTER ----- */
    footer {
      text-align: center;
      padding: 1.5rem;
      color: var(--muted);
      font-size: .82rem;
      border-top: 1px solid var(--border);
    }
    footer a { color: var(--blue); text-decoration: none; }
    footer a:hover { text-decoration: underline; }
  </style>
</head>
<body>

<header>
  <div class="badge">Multi-Tenant API Hub &mdash; Live</div>
  <h1>TDS GA2 API Hub</h1>
  <p>Seeded per-student. All 10 question services live under <code style="color:var(--accent);font-family:'JetBrains Mono',monospace">/ga2/{email}/q&lt;N&gt;/...</code></p>
</header>

<!-- Email lookup -->
<div class="lookup">
  <div class="lookup-card">
    <label>Student email →</label>
    <input type="email" id="email-input" placeholder="23f1000000@ds.study.iitm.ac.in" />
    <button onclick="loadParams()">Load My Config</button>
  </div>
</div>

<!-- Dynamic per-student params -->
<section id="params-section">
  <div class="params-card">
    <div class="params-header">⚡ Computed Parameters for <span id="params-email"></span></div>
    <div class="params-body" id="params-body"></div>
  </div>
</section>

<!-- Question grid -->
<div class="grid">

  <div class="card" style="--card-accent:#58a6ff;--card-badge-bg:rgba(88,166,255,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(88,166,255,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q01</span><h3>CORS-Aware Metrics</h3></div>
    <p>Statistical analysis over integer arrays with strict per-student <code>Access-Control-Allow-Origin</code>.</p>
    <div class="endpoints"><span class="ep-tag">GET /q1/stats</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#bc8cff;--card-badge-bg:rgba(188,140,255,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(188,140,255,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q02</span><h3>OAuth / OIDC Verify</h3></div>
    <p>Validates RS256 JWT tokens against per-student issuer, audience, and expiry constraints.</p>
    <div class="endpoints"><span class="ep-tag">POST /q2/verify</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#7ee8a2;--card-badge-bg:rgba(126,232,162,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(126,232,162,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q03</span><h3>Config Precedence</h3></div>
    <p>Merges 4 config layers (defaults → yaml → .env → os-env) with CLI override and secret masking.</p>
    <div class="endpoints"><span class="ep-tag">GET /q3/effective-config</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#ffa657;--card-badge-bg:rgba(255,166,87,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(255,166,87,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q04</span><h3>Redis Counter</h3></div>
    <p>Docker Compose service that proxies atomic INCR/GET via Redis with health probe.</p>
    <div class="endpoints"><span class="ep-tag">POST /q4/hit/{key}</span><span class="ep-tag">GET /q4/count/{key}</span><span class="ep-tag">GET /q4/healthz</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#e3b341;--card-badge-bg:rgba(227,179,65,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(227,179,65,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q05</span><h3>Analytics Platform</h3></div>
    <p>Batch event aggregation: total, unique users, revenue, top user. X-API-Key authentication per student.</p>
    <div class="endpoints"><span class="ep-tag">POST /q5/analytics</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#58a6ff;--card-badge-bg:rgba(88,166,255,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(88,166,255,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q06</span><h3>Observability</h3></div>
    <p>Live Prometheus metrics, structured tail logging, and health/uptime endpoint.</p>
    <div class="endpoints"><span class="ep-tag">GET /q6/metrics</span><span class="ep-tag">GET /q6/logs/tail</span><span class="ep-tag">GET /q6/healthz</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#ff7b72;--card-badge-bg:rgba(255,123,114,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(255,123,114,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q07</span><h3>LLM Tunnel</h3></div>
    <p>OpenAI-compatible local LLM tunnel: echoes tokens, computes arithmetic, returns structured completions.</p>
    <div class="endpoints"><span class="ep-tag">POST /q7/v1/chat/completions</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#bc8cff;--card-badge-bg:rgba(188,140,255,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(188,140,255,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q08</span><h3>Invoice Extractor</h3></div>
    <p>LLM-style structured output: extracts vendor, currency, date, and amount from free-text invoices.</p>
    <div class="endpoints"><span class="ep-tag">POST /q8/extract</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#7ee8a2;--card-badge-bg:rgba(126,232,162,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(126,232,162,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q09</span><h3>Orders (Idempotency + Pagination)</h3></div>
    <p>Create orders with idempotency keys, cursor-based pagination, and per-client rate limiting.</p>
    <div class="endpoints"><span class="ep-tag">POST /q9/orders</span><span class="ep-tag">GET /q9/orders</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

  <div class="card" style="--card-accent:#ffa657;--card-badge-bg:rgba(255,166,87,.1);--card-glow:radial-gradient(ellipse 120% 80% at 50% 50%,rgba(255,166,87,.04),transparent)">
    <div class="card-header"><span class="q-badge">Q10</span><h3>Middleware Stack</h3></div>
    <p>Composable CORS guard → Context-ID injector → sliding-window rate limiter → pong handler.</p>
    <div class="endpoints"><span class="ep-tag">GET /q10/ping</span></div>
    <div class="card-status"><span class="dot"></span> Online</div>
  </div>

</div>

<footer>
  <a href="docs">OpenAPI Docs</a> &nbsp;·&nbsp;
  <a href="redoc">ReDoc</a> &nbsp;·&nbsp;
  IITM TDS 2026-05 &mdash; Multi-tenant, seeded per student email
</footer>

<script>
async function loadParams() {
  const email = document.getElementById('email-input').value.trim();
  if (!email) return;
  const sec = document.getElementById('params-section');
  const body = document.getElementById('params-body');
  const lbl  = document.getElementById('params-email');
  lbl.textContent = email;
  body.innerHTML = '<div style="color:var(--muted);font-size:.85rem"><span class="spin">↻</span> Loading…</div>';
  sec.style.display = 'block';

  const base = `/ga2/${encodeURIComponent(email)}`;
  const rows = [];

  try {
    const r1 = await fetch(`${base}/q1/stats?values=1,2,3`);
    const h1 = r1.headers.get('access-control-allow-origin') || '(not returned)';
    rows.push({ label: 'Q01 Allowed Origin', value: h1 });
  } catch(e) { rows.push({ label: 'Q01 Allowed Origin', value: 'error' }); }

  try {
    const r3 = await fetch(`${base}/q3/effective-config`);
    const d3 = await r3.json();
    rows.push({ label: 'Q03 Port', value: d3.port });
    rows.push({ label: 'Q03 Workers', value: d3.workers });
    rows.push({ label: 'Q03 Debug', value: String(d3.debug) });
    rows.push({ label: 'Q03 Log Level', value: d3.log_level });
  } catch(e) { rows.push({ label: 'Q03 Config', value: 'error' }); }

  try {
    const r9 = await fetch(`${base}/q9/orders`);
    const d9 = await r9.json();
    rows.push({ label: 'Q09 Total Orders', value: d9.items ? (d9.next_cursor ? '>' + d9.items.length : d9.items.length) : '?' });
  } catch(e) { rows.push({ label: 'Q09 Orders', value: 'error' }); }

  try {
    const r10 = await fetch(`${base}/q10/ping`);
    const aco = r10.headers.get('access-control-allow-origin');
    rows.push({ label: 'Q10 Context-Id', value: r10.headers.get('x-context-id') || 'n/a' });
  } catch(e) { rows.push({ label: 'Q10 Ping', value: 'error' }); }

  body.innerHTML = rows.map(r =>
    `<div class="param-row"><div class="param-label">${r.label}</div><div class="param-value">${r.value}</div></div>`
  ).join('');
}

document.getElementById('email-input').addEventListener('keydown', e => {
  if (e.key === 'Enter') loadParams();
});
</script>
</body>
</html>
"""
