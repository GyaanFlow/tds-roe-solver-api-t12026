from __future__ import annotations

"""
T22026/GA2/app.py — Unified GA2 sub-application
Mounted at /ga2 by the root hf_space/app.py.
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
# Dashboard
# ---------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def ga2_home():
    return HTMLResponse(_DASHBOARD_HTML)


_DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GA2 URL Generator — TDS 2026-05</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg:       #06080f;
      --surface:  #0d1117;
      --s2:       #161b26;
      --s3:       #1c2333;
      --border:   #21262d;
      --text:     #e6edf3;
      --muted:    #8b949e;
      --accent:   #7ee8a2;
      --blue:     #58a6ff;
      --purple:   #bc8cff;
      --orange:   #ffa657;
      --red:      #ff7b72;
      --yellow:   #e3b341;
    }

    body {
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
    }

    /* ── HERO ── */
    .hero {
      background: linear-gradient(160deg, #0d1b2e 0%, #06080f 60%);
      border-bottom: 1px solid var(--border);
      padding: 3rem 1.5rem 2.5rem;
      text-align: center;
      position: relative;
      overflow: hidden;
    }
    .hero::before {
      content: '';
      position: absolute; inset: 0;
      background: radial-gradient(ellipse 80% 55% at 50% -10%, rgba(126,232,162,.13), transparent);
      pointer-events: none;
    }
    .live-pill {
      display: inline-flex; align-items: center; gap: 6px;
      background: rgba(126,232,162,.1); border: 1px solid rgba(126,232,162,.3);
      color: var(--accent); border-radius: 99px; padding: 4px 14px;
      font-size: .72rem; font-weight: 700; letter-spacing: .06em; margin-bottom: 1.2rem;
    }
    .live-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--accent); animation: blink 1.8s infinite; }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:.25} }
    .hero h1 {
      font-size: clamp(1.8rem,4.5vw,3rem); font-weight: 800;
      background: linear-gradient(135deg,#fff 0%, var(--accent) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
      margin-bottom: .6rem;
    }
    .hero p { color: var(--muted); font-size: .95rem; max-width: 540px; margin: 0 auto; line-height: 1.6; }

    /* ── EMAIL INPUT CARD ── */
    .email-wrap {
      max-width: 780px; margin: 2rem auto; padding: 0 1.25rem;
    }
    .email-card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 16px; padding: 1.6rem 2rem;
    }
    .email-card label {
      display: block; font-size: .78rem; font-weight: 600;
      color: var(--muted); letter-spacing: .05em; text-transform: uppercase; margin-bottom: .6rem;
    }
    .email-row { display: flex; gap: .75rem; flex-wrap: wrap; }
    .email-row input {
      flex: 1; min-width: 240px;
      background: var(--s2); border: 1.5px solid var(--border);
      border-radius: 10px; padding: .7rem 1.1rem;
      color: var(--text); font-size: .95rem;
      font-family: 'JetBrains Mono', monospace; outline: none;
      transition: border-color .2s;
    }
    .email-row input:focus { border-color: var(--accent); }
    .email-row input::placeholder { color: #3d444d; }
    .gen-btn {
      background: var(--accent); color: #06080f;
      border: none; border-radius: 10px; padding: .7rem 1.6rem;
      font-size: .9rem; font-weight: 800; cursor: pointer;
      transition: opacity .15s, transform .12s; white-space: nowrap;
    }
    .gen-btn:hover { opacity: .85; transform: translateY(-1px); }

    /* ── SECTION HEADING ── */
    .section {
      max-width: 780px; margin: 0 auto; padding: 0 1.25rem 3rem;
    }
    .section-title {
      font-size: .72rem; font-weight: 700; letter-spacing: .1em;
      text-transform: uppercase; color: var(--muted);
      display: flex; align-items: center; gap: 8px;
      margin: 1.8rem 0 1rem;
    }
    .section-title::after { content:''; flex:1; height:1px; background: var(--border); }

    /* ── URL TABLE ── */
    #url-section { display: none; }
    .url-table {
      display: flex; flex-direction: column; gap: .55rem;
    }
    .url-row {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; overflow: hidden;
      display: grid;
      grid-template-columns: 48px 1fr auto auto;
      align-items: center;
      transition: border-color .2s;
    }
    .url-row:hover { border-color: #30363d; }
    .q-num {
      display: flex; align-items: center; justify-content: center;
      height: 100%; min-height: 56px;
      background: var(--s2); border-right: 1px solid var(--border);
      font-family: 'JetBrains Mono', monospace;
      font-size: .72rem; font-weight: 700;
      color: var(--accent);
    }
    .url-info { padding: .7rem 1rem; overflow: hidden; }
    .url-name { font-size: .8rem; font-weight: 600; color: var(--text); margin-bottom: 3px; }
    .url-method {
      display: inline-block; font-size: .64rem; font-weight: 700;
      padding: 1px 5px; border-radius: 4px; margin-right: 5px;
      font-family: 'JetBrains Mono', monospace; letter-spacing: .04em;
    }
    .m-get  { background: rgba(88,166,255,.15); color: var(--blue); border: 1px solid rgba(88,166,255,.25); }
    .m-post { background: rgba(126,232,162,.12); color: var(--accent); border: 1px solid rgba(126,232,162,.22); }
    .url-path {
      font-family: 'JetBrains Mono', monospace; font-size: .76rem;
      color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }
    .url-path .em { color: #fbbf24; }
    .url-actions { display: flex; gap: 0; }
    .copy-btn {
      background: transparent; border: none; border-left: 1px solid var(--border);
      color: var(--muted); padding: 0 1rem; height: 100%; min-height: 56px;
      cursor: pointer; font-size: .78rem; font-weight: 600;
      display: flex; align-items: center; gap: 5px;
      transition: background .15s, color .15s; white-space: nowrap;
    }
    .copy-btn:hover { background: var(--s2); color: var(--text); }
    .copy-btn.copied { color: var(--accent); }
    .open-btn {
      background: transparent; border: none; border-left: 1px solid var(--border);
      color: var(--muted); padding: 0 .9rem; height: 100%; min-height: 56px;
      cursor: pointer; font-size: .8rem; display: flex; align-items: center;
      transition: background .15s, color .15s; text-decoration: none;
    }
    .open-btn:hover { background: var(--s2); color: var(--blue); }

    /* ── QUICK TIPS ── */
    .tip-box {
      background: var(--s2); border: 1px solid var(--border);
      border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: .6rem;
    }
    .tip-box code {
      font-family: 'JetBrains Mono', monospace; font-size: .78rem;
      background: var(--s3); border: 1px solid var(--border);
      border-radius: 5px; padding: 1px 6px; color: var(--accent);
    }
    .tip-box p { font-size: .83rem; color: var(--muted); line-height: 1.6; }

    /* ── INFO CARDS ── */
    .info-grid {
      display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: .7rem;
    }
    .info-card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 1rem 1.1rem;
    }
    .info-label { font-size: .7rem; color: var(--muted); font-weight: 600; letter-spacing: .04em; text-transform: uppercase; margin-bottom: 4px; }
    .info-val {
      font-family: 'JetBrains Mono', monospace; font-size: .8rem; color: var(--accent);
      word-break: break-all; display: flex; align-items: center; gap: 6px;
    }
    .mini-copy {
      background: none; border: none; color: var(--muted); cursor: pointer;
      font-size: .7rem; flex-shrink: 0; transition: color .15s;
    }
    .mini-copy:hover { color: var(--accent); }
    .loading-dots::after {
      content: '...'; animation: dots 1s infinite;
    }
    @keyframes dots { 0%{content:'.'} 33%{content:'..'} 66%{content:'...'} }

    /* footer */
    footer { text-align: center; color: var(--muted); font-size: .78rem; padding: 2rem 1rem; border-top: 1px solid var(--border); }
    footer a { color: var(--blue); text-decoration: none; }
  </style>
</head>
<body>

<!-- HERO -->
<div class="hero">
  <div class="live-pill"><span class="live-dot"></span>10 SERVICES LIVE</div>
  <h1>GA2 URL Generator</h1>
  <p>Enter your IITM student email to instantly generate all your personalised GA2 API endpoints — ready to copy-paste into the exam grader.</p>
</div>

<!-- EMAIL INPUT -->
<div class="email-wrap">
  <div class="email-card">
    <label>Your Student Email</label>
    <div class="email-row">
      <input type="email" id="email-input"
        placeholder="23f1000000@ds.study.iitm.ac.in"
        autocomplete="off" spellcheck="false" />
      <button class="gen-btn" onclick="generate()">⚡ Generate URLs</button>
    </div>
  </div>
</div>

<!-- URL SECTION (hidden until email entered) -->
<div class="section">

  <div id="url-section">

    <!-- Computed params -->
    <div class="section-title">Your Computed Config</div>
    <div class="info-grid" id="info-grid">
      <div class="info-card"><div class="info-label">Email</div><div class="info-val" id="ic-email">—</div></div>
      <div class="info-card"><div class="info-label">Q01 Allowed Origin</div><div class="info-val" id="ic-origin"><span class="loading-dots"></span></div></div>
      <div class="info-card"><div class="info-label">Q03 Port</div><div class="info-val" id="ic-port"><span class="loading-dots"></span></div></div>
      <div class="info-card"><div class="info-label">Q03 Workers</div><div class="info-val" id="ic-workers"><span class="loading-dots"></span></div></div>
      <div class="info-card"><div class="info-label">Q03 Log Level</div><div class="info-val" id="ic-log"><span class="loading-dots"></span></div></div>
      <div class="info-card"><div class="info-label">Q09 Total Orders</div><div class="info-val" id="ic-orders"><span class="loading-dots"></span></div></div>
    </div>

    <!-- URL list -->
    <div class="section-title">Your Personalised API URLs</div>
    <div class="url-table" id="url-table"></div>

    <!-- Tips -->
    <div class="section-title">Quick Tips</div>
    <div class="tip-box">
      <p>🔑 <strong>Q05 Analytics</strong> requires an <code>X-API-Key</code> header. Your key is unique — fetch it from <code>/q5/analytics</code> after generating.</p>
    </div>
    <div class="tip-box">
      <p>🪪 <strong>Q02 JWT Verify</strong> expects a POST body: <code>{"token": "&lt;your-RS256-jwt&gt;"}</code></p>
    </div>
    <div class="tip-box">
      <p>📦 <strong>Q08 Extract</strong> expects: <code>{"text": "Invoice from Vendor XYZ, amount USD 540.50, date 2026-03-15"}</code></p>
    </div>
    <div class="tip-box">
      <p>🔁 <strong>Q09 Orders</strong> — pass <code>Idempotency-Key: any-uuid</code> header so the same order ID is returned on retry.</p>
    </div>

  </div>

  <!-- empty state -->
  <div id="empty-state" style="text-align:center;padding:3rem 1rem;color:var(--muted);">
    <div style="font-size:2.5rem;margin-bottom:.8rem;">🎯</div>
    <p style="font-size:.95rem;">Enter your email above and click <strong style="color:var(--text)">Generate URLs</strong> to get your personalised endpoints.</p>
  </div>

</div>

<footer>
  <a href="docs">OpenAPI Docs</a> &nbsp;·&nbsp; <a href="redoc">ReDoc</a> &nbsp;·&nbsp;
  IITM TDS 2026-05 GA2 — Multi-tenant, seeded per student email
</footer>

<script>
  // Detect base host automatically
  const BASE = window.location.origin;

  const QUESTIONS = [
    {
      q: 'Q01', name: 'Metrics + CORS',
      method: 'GET',
      path: (e) => `/ga2/${e}/q1/stats?values=1,2,3,4,5`,
      note: 'Comma-separated integers in ?values'
    },
    {
      q: 'Q02', name: 'OAuth JWT Verify',
      method: 'POST',
      path: (e) => `/ga2/${e}/q2/verify`,
      note: 'Body: {"token": "<RS256-jwt>"}'
    },
    {
      q: 'Q03', name: 'Config Precedence',
      method: 'GET',
      path: (e) => `/ga2/${e}/q3/effective-config`,
      note: 'Optional ?set=key=value overrides'
    },
    {
      q: 'Q04', name: 'Redis Counter — Hit',
      method: 'POST',
      path: (e) => `/ga2/${e}/q4/hit/mykey`,
      note: 'Replace mykey with any key name'
    },
    {
      q: 'Q04', name: 'Redis Counter — Count',
      method: 'GET',
      path: (e) => `/ga2/${e}/q4/count/mykey`,
      note: 'Read the current count for a key'
    },
    {
      q: 'Q04', name: 'Redis Healthz',
      method: 'GET',
      path: (e) => `/ga2/${e}/q4/healthz`,
      note: 'Check Redis + service health'
    },
    {
      q: 'Q05', name: 'Analytics (X-API-Key)',
      method: 'POST',
      path: (e) => `/ga2/${e}/q5/analytics`,
      note: 'Add X-API-Key header — key is unique to your email'
    },
    {
      q: 'Q06', name: 'Prometheus Metrics',
      method: 'GET',
      path: (e) => `/ga2/${e}/q6/metrics`,
      note: 'Returns Prometheus text format'
    },
    {
      q: 'Q06', name: 'Log Tail',
      method: 'GET',
      path: (e) => `/ga2/${e}/q6/logs/tail?limit=20`,
      note: 'Returns last N structured log entries'
    },
    {
      q: 'Q06', name: 'Healthz / Uptime',
      method: 'GET',
      path: (e) => `/ga2/${e}/q6/healthz`,
      note: 'Returns status + uptime_s'
    },
    {
      q: 'Q07', name: 'LLM Chat Completions',
      method: 'POST',
      path: (e) => `/ga2/${e}/q7/v1/chat/completions`,
      note: 'OpenAI-compatible, echoes tokens & arithmetic'
    },
    {
      q: 'Q08', name: 'Invoice Extractor',
      method: 'POST',
      path: (e) => `/ga2/${e}/q8/extract`,
      note: 'Body: {"text": "Invoice from Acme, USD 540.50, 2026-03-15"}'
    },
    {
      q: 'Q09', name: 'Create Order',
      method: 'POST',
      path: (e) => `/ga2/${e}/q9/orders`,
      note: 'Header: Idempotency-Key: <uuid>'
    },
    {
      q: 'Q09', name: 'List Orders (Paginated)',
      method: 'GET',
      path: (e) => `/ga2/${e}/q9/orders?limit=10`,
      note: 'Cursor-based pagination via ?cursor=N'
    },
    {
      q: 'Q10', name: 'Ping (Middleware Stack)',
      method: 'GET',
      path: (e) => `/ga2/${e}/q10/ping`,
      note: 'CORS + Context-ID + Rate-limiter → pong'
    },
  ];

  const METHOD_CLASS = { GET: 'm-get', POST: 'm-post' };
  const Q_COLORS = {
    Q01: '#58a6ff', Q02: '#bc8cff', Q03: '#7ee8a2',
    Q04: '#ffa657', Q05: '#e3b341', Q06: '#58a6ff',
    Q07: '#ff7b72', Q08: '#bc8cff', Q09: '#7ee8a2', Q10: '#ffa657'
  };

  let lastEmail = '';

  function generate() {
    const raw = document.getElementById('email-input').value.trim();
    if (!raw || !raw.includes('@')) {
      document.getElementById('email-input').style.borderColor = '#f85149';
      setTimeout(() => document.getElementById('email-input').style.borderColor = '', 1200);
      return;
    }
    lastEmail = raw;
    const enc = encodeURIComponent(raw);

    // Show section
    document.getElementById('url-section').style.display = 'block';
    document.getElementById('empty-state').style.display = 'none';

    // Computed config card
    document.getElementById('ic-email').textContent = raw;

    // Build URL rows
    const table = document.getElementById('url-table');
    table.innerHTML = '';
    QUESTIONS.forEach((q, i) => {
      const path = q.path(enc);
      const fullUrl = BASE + path;
      const color = Q_COLORS[q.q] || '#7ee8a2';

      // email part highlighted in path display
      const displayPath = path.replace(enc, `<span class="em">${enc}</span>`);

      const row = document.createElement('div');
      row.className = 'url-row';
      row.innerHTML = `
        <div class="q-num" style="color:${color}">${q.q}</div>
        <div class="url-info">
          <div class="url-name">
            <span class="url-method ${METHOD_CLASS[q.method]}">${q.method}</span>
            ${q.name}
          </div>
          <div class="url-path" title="${fullUrl}">${displayPath}</div>
        </div>
        <button class="copy-btn" id="copy-${i}" onclick="copyUrl('${fullUrl}', ${i})">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
          </svg>
          Copy
        </button>
        ${q.method === 'GET' ? `<a class="open-btn" href="${fullUrl}" target="_blank" title="Open in new tab">↗</a>` : '<div style="width:16px"></div>'}
      `;
      table.appendChild(row);
    });

    // Fetch live config values
    fetchConfig(enc);
  }

  async function fetchConfig(enc) {
    // Reset loaders
    ['ic-origin','ic-port','ic-workers','ic-log','ic-orders'].forEach(id => {
      document.getElementById(id).innerHTML = '<span style="color:var(--muted);font-size:.7rem">loading…</span>';
    });

    try {
      const r1 = await fetch(`${BASE}/ga2/${enc}/q1/stats?values=1,2,3`);
      const origin = r1.headers.get('access-control-allow-origin') || '(check CORS preflight)';
      setInfo('ic-origin', origin);
    } catch(e) { setInfo('ic-origin', 'fetch failed'); }

    try {
      const r3 = await fetch(`${BASE}/ga2/${enc}/q3/effective-config`);
      const d = await r3.json();
      setInfo('ic-port', String(d.port));
      setInfo('ic-workers', String(d.workers));
      setInfo('ic-log', d.log_level);
    } catch(e) {
      ['ic-port','ic-workers','ic-log'].forEach(id => setInfo(id, 'fetch failed'));
    }

    try {
      const r9 = await fetch(`${BASE}/ga2/${enc}/q9/orders?limit=1`);
      const d = await r9.json();
      // next_cursor is null when we reach the end, so total = last id returned
      const total = d.next_cursor ? '> 10' : (d.items?.length || '?');
      setInfo('ic-orders', d.next_cursor || (d.items?.length ? String(d.items.length) : '?'));
    } catch(e) { setInfo('ic-orders', 'fetch failed'); }
  }

  function setInfo(id, val) {
    const el = document.getElementById(id);
    el.innerHTML = `<span>${val}</span>
      <button class="mini-copy" onclick="navigator.clipboard.writeText('${val.replace(/'/g,"\\'")}').then(()=>this.textContent='✓').then(()=>setTimeout(()=>this.textContent='⎘',1000))" title="Copy">⎘</button>`;
  }

  function copyUrl(url, idx) {
    navigator.clipboard.writeText(url).then(() => {
      const btn = document.getElementById(`copy-${idx}`);
      btn.classList.add('copied');
      btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg> Copied!`;
      setTimeout(() => {
        btn.classList.remove('copied');
        btn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/></svg> Copy`;
      }, 2000);
    });
  }

  // Press Enter to generate
  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('email-input').addEventListener('keydown', e => {
      if (e.key === 'Enter') generate();
    });
  });
</script>
</body>
</html>
"""
