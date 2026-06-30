from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

BASE = Path(__file__).resolve().parents[1]


def load_app(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    # Register module so Pydantic forward-ref resolution can find typing symbols
    # under the module namespace during route/model construction.
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "app"):
        raise RuntimeError(f"Module {file_path} has no 'app'")
    return mod.app


q5 = load_app("q5_app", BASE / "T22026" / "GA0" / "Q05" / "app" / "main.py")
q10 = load_app("q10_app", BASE / "T22026" / "GA0" / "Q10" / "app" / "main.py")
q11 = load_app("q11_app", BASE / "T22026" / "GA0" / "Q11" / "app" / "main.py")
q14 = load_app("q14_app", BASE / "T22026" / "GA0" / "Q14" / "app" / "main.py")
q16 = load_app("q16_app", BASE / "T22026" / "GA0" / "Q16" / "app" / "main.py")
q18 = load_app("q18_app", BASE / "T22026" / "GA0" / "Q18" / "app" / "main.py")
q25 = load_app("q25_app", BASE / "T22026" / "GA0" / "Q25" / "app" / "main.py")

app = FastAPI(title="T22026 GA0 Unified API Hub", version="1.0.0")

import re

class MultiTenantASGIMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            match = re.match(r"^/ga2/([^/]+@[^/]+)(/.*)?$", path)
            if match:
                email = match.group(1).strip()
                rest = match.group(2) or "/"
                scope["path"] = f"/ga2{rest}"
                scope["tenant_email"] = email
        await self.app(scope, receive, send)

app.add_middleware(MultiTenantASGIMiddleware)

class ConditionalCORSMiddleware(CORSMiddleware):
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/ga2"):
                await self.app(scope, receive, send)
                return
        await super().__call__(scope, receive, send)

app.add_middleware(
    ConditionalCORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/version")
def api_version():
    return {"version": "mock-0.0.1"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>T22026 API Hub — GA0 + GA2</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #030712;
      --card-bg: rgba(17, 24, 39, 0.6);
      --border: rgba(99, 102, 241, 0.2);
      --border-hover: rgba(99, 102, 241, 0.4);
      --text: #f9fafb;
      --muted: #9ca3af;
      --accent: #6366f1;
      --accent-hover: #818cf8;
      --green: #10b981;
      --green-bg: rgba(16,185,129,0.1);
      --green-border: rgba(16,185,129,0.25);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background-color: var(--bg);
      background-image:
        radial-gradient(at 0% 0%, rgba(99,102,241,.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(168,85,247,.1) 0px, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }
    .container { width: 100%; max-width: 1100px; }
    .header { text-align: center; margin-bottom: 40px; }
    .header h1 {
      font-size: 2.5rem; font-weight: 700;
      background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 50%, #4338ca 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      margin-bottom: 12px;
    }
    .badge {
      display: inline-block; padding: 6px 14px;
      background: rgba(99,102,241,.1); border: 1px solid rgba(99,102,241,.3);
      border-radius: 20px; color: #a5b4fc; font-size: .85rem; font-weight: 500; margin-bottom: 15px;
    }
    /* Section labels */
    .section-label {
      font-size: .75rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
      color: var(--muted); margin: 30px 0 14px; padding-left: 4px;
      display: flex; align-items: center; gap: 8px;
    }
    .section-label::after { content:''; flex:1; height:1px; background:rgba(255,255,255,.06); }
    /* Grids */
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(310px, 1fr)); gap: 18px; margin-bottom: 10px; }
    .tile {
      background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px;
      padding: 22px; box-shadow: 0 10px 25px rgba(0,0,0,.3);
      transition: all .3s cubic-bezier(.4,0,.2,1); backdrop-filter: blur(16px);
      display: flex; flex-direction: column; justify-content: space-between;
    }
    .tile:hover { border-color: var(--border-hover); transform: translateY(-4px); box-shadow: 0 15px 35px rgba(99,102,241,.15); }
    .tile.ga2-tile { border-color: var(--green-border); background: rgba(16,185,129,.04); }
    .tile.ga2-tile:hover { border-color: rgba(16,185,129,.5); box-shadow: 0 15px 35px rgba(16,185,129,.12); }
    .tile-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; }
    .tile-title { font-size: 1.1rem; font-weight: 600; color: #f3f4f6; }
    .status-badge { font-size: .72rem; padding: 3px 8px; border-radius: 10px; font-weight: 600; }
    .status-badge.active { background: rgba(16,185,129,.1); color: #34d399; border: 1px solid rgba(16,185,129,.2); }
    .status-badge.ga2 { background: rgba(16,185,129,.15); color: #6ee7b7; border: 1px solid rgba(16,185,129,.3); }
    .tile-desc { font-size: .88rem; color: var(--muted); line-height: 1.55; margin-bottom: 18px; flex-grow: 1; }
    .mono-hint { font-size: .73rem; color: #818cf8; font-family: 'JetBrains Mono', monospace; margin-bottom: 8px; word-break: break-all; }
    .tile-actions { display: flex; gap: 8px; }
    .btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 6px;
      padding: 9px 16px; font-family: inherit; font-size: .83rem; font-weight: 600;
      color: #fff; background: var(--accent); border: none; border-radius: 10px;
      cursor: pointer; transition: all .2s ease; text-decoration: none; flex: 1; text-align: center;
    }
    .btn:hover { background: var(--accent-hover); }
    .btn.green { background: #059669; }
    .btn.green:hover { background: #10b981; }
    .btn-secondary {
      background: rgba(255,255,255,.05); color: var(--text);
      border: 1px solid rgba(255,255,255,.08);
    }
    .btn-secondary:hover { background: rgba(255,255,255,.1); }
    /* GA2 hero box */
    .ga2-hero {
      background: linear-gradient(135deg, rgba(16,185,129,.08) 0%, rgba(99,102,241,.08) 100%);
      border: 1px solid var(--green-border); border-radius: 16px; padding: 24px 28px;
      margin-bottom: 14px; display: flex; gap: 24px; align-items: flex-start; flex-wrap: wrap;
    }
    .ga2-hero h2 { font-size: 1.3rem; font-weight: 700; color: #6ee7b7; margin-bottom: 6px; }
    .ga2-hero p { font-size: .9rem; color: var(--muted); max-width: 520px; line-height: 1.6; }
    .ga2-url-box {
      background: rgba(0,0,0,.4); border: 1px solid rgba(16,185,129,.2);
      border-radius: 10px; padding: 12px 16px; margin-top: 12px;
      font-family: 'JetBrains Mono', monospace; font-size: .8rem; color: #6ee7b7;
      white-space: nowrap; overflow-x: auto;
    }
    .ga2-url-box .dim { color: #4b5563; }
    .footer {
      text-align: center; color: var(--muted); font-size: .83rem;
      margin-top: 36px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,.05);
    }
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <span class="badge">GA0 + GA2 · Multi-App Gateway</span>
    <h1>T22026 IITM TDS API Hub</h1>
    <p style="color:var(--muted);max-width:600px;margin:0 auto;font-size:1rem;line-height:1.6;">
      All GA0 programming services and the full GA2 multi-tenant API hub are live on this Space.
    </p>
  </div>

  <!-- ── GA2 Hero ──────────────────────────── -->
  <div class="section-label">🆕 GA2 — Multi-Tenant Services</div>

  <div class="ga2-hero">
    <div style="flex:1;min-width:240px;">
      <h2>GA2 API Hub — 10 Question Services</h2>
      <p>Seeded per student email. Pass your email in the URL path — every student gets their own isolated config, CORS origins, API keys, and rate limits.</p>
      <div class="ga2-url-box">
        <span class="dim">https://your-space.hf.space</span>/ga2/<span style="color:#fbbf24;">your@email.com</span>/q1/stats
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:8px;min-width:180px;">
      <a href="/ga2/" class="btn green" style="text-align:center;">Open GA2 Dashboard</a>
      <a href="/ga2/docs" class="btn btn-secondary" style="text-align:center;">GA2 API Docs</a>
    </div>
  </div>

  <div class="grid">
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q1 · Metrics + CORS</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">Statistical summary (count, sum, min, max, mean) with strict per-student CORS origin enforcement.</p>
        <p class="mono-hint">GET /ga2/{email}/q1/stats?values=1,2,3</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q2 · OAuth JWT Verify</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">RS256 JWT validation with per-student issuer, audience, and expiry checks.</p>
        <p class="mono-hint">POST /ga2/{email}/q2/verify</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q3 · Config Precedence</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">Merges 4 config layers with CLI overrides and secret masking.</p>
        <p class="mono-hint">GET /ga2/{email}/q3/effective-config</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q4 · Redis Counter</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">Atomic INCR/GET via Redis (in-process fallback when Redis unavailable).</p>
        <p class="mono-hint">POST /ga2/{email}/q4/hit/{key}</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q5 · Analytics</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">Batch event aggregation — revenue, unique users, top user — with per-student API key.</p>
        <p class="mono-hint">POST /ga2/{email}/q5/analytics</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q6 · Observability</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">Prometheus metrics, structured tail logs, and uptime health endpoint.</p>
        <p class="mono-hint">GET /ga2/{email}/q6/metrics</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q7 · LLM Tunnel</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">OpenAI-compatible completions endpoint: echoes tokens, computes arithmetic.</p>
        <p class="mono-hint">POST /ga2/{email}/q7/v1/chat/completions</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q8 · Invoice Extractor</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">Extracts vendor, currency, date, and amount from free-text invoice strings.</p>
        <p class="mono-hint">POST /ga2/{email}/q8/extract</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q9 · Orders API</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">Idempotent order creation, cursor pagination, and per-client rate limiting.</p>
        <p class="mono-hint">POST /ga2/{email}/q9/orders</p>
      </div>
    </div>
    <div class="tile ga2-tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q10 · Middleware Stack</span><span class="status-badge ga2">Live</span></div>
        <p class="tile-desc">CORS guard → Context-ID injector → sliding-window rate limiter → pong.</p>
        <p class="mono-hint">GET /ga2/{email}/q10/ping</p>
      </div>
    </div>
  </div>

  <!-- ── GA0 Section ──────────────────────────── -->
  <div class="section-label">GA0 — Programming Services</div>

  <div class="grid">
    <div class="tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q5: Code Interpreter</span><span class="status-badge active">Active</span></div>
        <p class="tile-desc">Python execution sandbox with secure traceback-based error line number extraction.</p>
        <p class="mono-hint">POST /q-code-interpreter-ai-analysis/code-interpreter</p>
      </div>
      <div class="tile-actions">
        <a href="/q-code-interpreter-ai-analysis/" class="btn">Open</a>
        <a href="/q-code-interpreter-ai-analysis/health" class="btn btn-secondary">Health</a>
      </div>
    </div>
    <div class="tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q10: Student CSV API</span><span class="status-badge active">Active</span></div>
        <p class="tile-desc">FastAPI database server filtering students dynamically with multi-query list matching.</p>
        <p class="mono-hint">GET /q-fastapi/api?class=...</p>
      </div>
      <div class="tile-actions">
        <a href="/q-fastapi/" class="btn">Open</a>
        <a href="/q-fastapi/health" class="btn btn-secondary">Health</a>
      </div>
    </div>
    <div class="tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q11: Sentiment Batch</span><span class="status-badge active">Active</span></div>
        <p class="tile-desc">High-performance NLP pipeline classifying sentiment into happy, sad, and neutral.</p>
        <p class="mono-hint">POST /q-fastapi-sentiment-batch/sentiment</p>
      </div>
      <div class="tile-actions">
        <a href="/q-fastapi-sentiment-batch/" class="btn">Open</a>
        <a href="/q-fastapi-sentiment-batch/health" class="btn btn-secondary">Health</a>
      </div>
    </div>
    <div class="tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q14: Image Rebuild</span><span class="status-badge active">Active</span></div>
        <p class="tile-desc">Forensic jigsaw reassembly and luminance-based grayscale PNG exporter.</p>
      </div>
      <div class="tile-actions">
        <a href="/q-image-grayscale-rebuild/" class="btn">Open</a>
        <a href="/q-image-grayscale-rebuild/health" class="btn btn-secondary">Health</a>
      </div>
    </div>
    <div class="tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q16: Move/Rename Files</span><span class="status-badge active">Active</span></div>
        <p class="tile-desc">Zip extraction pipeline performing flat relocation and digit increment renaming.</p>
      </div>
      <div class="tile-actions">
        <a href="/q-move-rename-files/" class="btn">Open</a>
        <a href="/q-move-rename-files/health" class="btn btn-secondary">Health</a>
      </div>
    </div>
    <div class="tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q18: Ollama Proxy</span><span class="status-badge active">Active</span></div>
        <p class="tile-desc">Diagnostic Ollama reverse proxy designed for strict ngrok hostname validation.</p>
      </div>
      <div class="tile-actions">
        <a href="/q-ollama/" class="btn">Open</a>
        <a href="/q-ollama/health" class="btn btn-secondary">Health</a>
      </div>
    </div>
    <div class="tile">
      <div>
        <div class="tile-header"><span class="tile-title">Q25: Vercel Latency API</span><span class="status-badge active">Active</span></div>
        <p class="tile-desc">Per-region latency analytics: avg, p95, uptime, threshold breach counting.</p>
        <p class="mono-hint" style="color:#f59e0b;">⚠️ Deploy to Vercel — exam checks vercel.app hostname</p>
      </div>
      <div class="tile-actions">
        <a href="/q-vercel-latency/" class="btn">Open</a>
        <a href="/q-vercel-latency/health" class="btn btn-secondary">Health</a>
      </div>
    </div>
  </div>

  <div class="footer">
    GA2 URL format: <code style="color:#6ee7b7;">/ga2/your@email.com/q1/stats</code> &nbsp;·&nbsp;
    <a href="/ga2/" style="color:#818cf8;">GA2 Dashboard</a> &nbsp;·&nbsp;
    <a href="/ga2/docs" style="color:#818cf8;">GA2 API Docs</a>
  </div>
</div>
</body>
</html>"""


# ── Exam-canonical mounts (question-ID style, no /qN prefix) ─────────────────
# The exam validator submits URLs in this form:
#   Q5  → POST  {host}/q-code-interpreter-ai-analysis/code-interpreter
#   Q10 → GET   {host}/q-fastapi/api?class=...
#   Q11 → POST  {host}/q-fastapi-sentiment-batch/sentiment
#   Q18 → GET   {host}/q-ollama/api/version  (session-based proxy)
#   Q25 → POST  {host}/q-vercel-latency/api/latency  (needs Vercel host)
app.mount("/q-code-interpreter-ai-analysis", q5)
app.mount("/q-fastapi", q10)
app.mount("/q-fastapi-sentiment-batch", q11)
app.mount("/q-image-grayscale-rebuild", q14)
app.mount("/q-move-rename-files", q16)
app.mount("/q-ollama", q18)
app.mount("/q-vercel-latency", q25)

# Mount GA2 Multi-Tenant Service Hub
ga2 = load_app("ga2_app", BASE / "T22026" / "GA2" / "app.py")
app.mount("/ga2", ga2)
