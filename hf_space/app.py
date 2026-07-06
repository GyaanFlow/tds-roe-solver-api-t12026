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
            match = re.match(r"^/(ga2|ga3)/([^/]+@[^/]+)(/.*)?$", path)
            if match:
                ga_version = match.group(1)
                email = match.group(2).strip()
                rest = match.group(3) or "/"
                
                parts = [p for p in rest.split("/") if p]
                token = None
                known_prefixes = {
                    "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8", "q9", "q10", "q11", "q12", "q13",
                    "solve", "health", "onboard", "status", "config", "docs", "redoc",
                    "answer-image", "extract", "dynamic-extract"
                }
                if parts and parts[0] not in known_prefixes:
                    token = parts[0]
                    rest = "/" + "/".join(parts[1:])
                
                scope["path"] = f"/{ga_version}{rest}"
                scope["tenant_email"] = email
                if token:
                    scope["tenant_token"] = token
        await self.app(scope, receive, send)

app.add_middleware(MultiTenantASGIMiddleware)

class ConditionalCORSMiddleware(CORSMiddleware):
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/ga2") or path.startswith("/ga3"):
                if scope.get("method") == "OPTIONS":
                    await super().__call__(scope, receive, send)
                    return
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
    return {"version": "mock-0.0.1", "commit": os.getenv("GIT_COMMIT", "local"), "build": os.getenv("RENDER_GIT_COMMIT", os.getenv("GIT_COMMIT", "local"))}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>T22026 IITM TDS API Hub</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #030712;
      --surface: #0f172a;
      --card-bg: rgba(17, 24, 39, 0.6);
      --border: rgba(99, 102, 241, 0.15);
      --border-hover: rgba(99, 102, 241, 0.35);
      --text: #f9fafb;
      --muted: #9ca3af;
      --accent: #6366f1;
      --accent-hover: #818cf8;
      --green: #10b981;
      --green-border: rgba(16,185,129,0.25);
      --orange: #fb923c;
      --orange-border: rgba(251,146,60,0.25);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background-color: var(--bg);
      background-image:
        radial-gradient(at 0% 0%, rgba(99,102,241,.12) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(168,85,247,.08) 0px, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 60px 20px;
    }
    .container { width: 100%; max-width: 900px; }
    .header { text-align: center; margin-bottom: 50px; }
    .header h1 {
      font-size: clamp(2rem, 5vw, 3rem); font-weight: 800;
      background: linear-gradient(135deg, #ffffff 30%, #6366f1 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 12px;
      letter-spacing: -0.02em;
    }
    .header p {
      color: var(--muted); max-width: 600px; margin: 0 auto; font-size: 1.05rem; line-height: 1.6;
    }
    
    /* ── DASHBOARD GRID ── */
    .hubs-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 24px;
      margin-bottom: 40px;
    }
    @media (min-width: 768px) {
      .hubs-grid { grid-template-columns: repeat(3, 1fr); }
    }
    
    .hub-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 30px;
      box-shadow: 0 10px 30px rgba(0,0,0,.4);
      transition: border-color .3s, transform .3s, box-shadow .3s;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .hub-card:hover {
      transform: translateY(-4px);
    }
    
    .hub-card.ga3 { border-color: var(--orange-border); }
    .hub-card.ga3:hover { border-color: var(--orange); box-shadow: 0 15px 35px rgba(251,146,60,0.12); }
    
    .hub-card.ga2 { border-color: var(--green-border); }
    .hub-card.ga2:hover { border-color: var(--green); box-shadow: 0 15px 35px rgba(16,185,129,0.12); }
    
    .hub-card.ga0 { border-color: var(--border); }
    .hub-card.ga0:hover { border-color: var(--accent); box-shadow: 0 15px 35px rgba(99,102,241,0.12); }
    
    .hub-meta { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 12px; }
    .hub-meta.c-ga3 { color: var(--orange); }
    .hub-meta.c-ga2 { color: var(--green); }
    .hub-meta.c-ga0 { color: var(--accent); }
    
    .hub-title { font-size: 1.35rem; font-weight: 700; color: #ffffff; margin-bottom: 10px; }
    .hub-desc { font-size: 0.9rem; color: var(--muted); line-height: 1.6; margin-bottom: 24px; flex-grow: 1; }
    
    .btn-stack { display: flex; flex-direction: column; gap: 8px; }
    .btn {
      display: inline-flex; align-items: center; justify-content: center;
      padding: 11px 20px; font-size: 0.88rem; font-weight: 700; border-radius: 12px;
      text-decoration: none; cursor: pointer; transition: opacity 0.2s, transform 0.1s;
      color: #030712; text-align: center;
    }
    .btn:hover { opacity: 0.9; }
    .btn:active { transform: translateY(1px); }
    
    .btn.b-ga3 { background: var(--orange); }
    .btn.b-ga2 { background: var(--green); }
    .btn.b-ga0 { background: var(--accent); color: #ffffff; }
    
    .btn-secondary {
      background: rgba(255,255,255,.05); color: var(--text);
      border: 1px solid rgba(255,255,255,.08);
    }
    .btn-secondary:hover { background: rgba(255,255,255,.1); }
    
    /* GA0 list dropdown */
    .ga0-select {
      width: 100%;
      background: rgba(15,23,42,0.8);
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 10px;
      padding: 10px 14px;
      color: var(--text);
      font-size: 0.83rem;
      outline: none;
      margin-top: 10px;
      cursor: pointer;
    }
    .ga0-select option { background: var(--surface); color: var(--text); }

    .footer {
      text-align: center; color: var(--muted); font-size: .83rem;
      margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,.05);
    }
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <span class="badge">Unified Solution Platform</span>
    <h1>T22026 IITM TDS Solver Gateway</h1>
    <p>Select a graded assignment dashboard below to access multi-tenant endpoint credentials, settings, and interactive solvers.</p>
  </div>

  <div class="hubs-grid">
    <!-- GA3 -->
    <div class="hub-card ga3">
      <div>
        <div class="hub-meta c-ga3">Graded Assignment 3</div>
        <div class="hub-title">GA3 Hub & Solvers</div>
        <div class="hub-desc">13 questions including Multimodal QA, invoice extraction, semantic ranking, and interactive client-side solvers for nonces, context window heist, and terminal cli cast generation.</div>
      </div>
      <div class="btn-stack">
        <a href="/ga3/" class="btn b-ga3">Open GA3 Dashboard</a>
        <a href="/ga3/docs" class="btn btn-secondary">API Reference</a>
      </div>
    </div>

    <!-- GA2 -->
    <div class="hub-card ga2">
      <div>
        <div class="hub-meta c-ga2">Graded Assignment 2</div>
        <div class="hub-title">GA2 API Hub</div>
        <div class="hub-desc">10 multi-tenant API question services (Metrics, OAuth JWT Verification, Config precedence, Redis counters, Analytics, Prometheus metrics, and LLM integrations).</div>
      </div>
      <div class="btn-stack">
        <a href="/ga2/" class="btn b-ga2">Open GA2 Dashboard</a>
        <a href="/ga2/docs" class="btn btn-secondary">API Reference</a>
      </div>
    </div>

    <!-- GA0 -->
    <div class="hub-card ga0">
      <div>
        <div class="hub-meta c-ga0">Graded Assignment 0</div>
        <div class="hub-title">GA0 Services</div>
        <div class="hub-desc">Individual programming task services including Python Code Interpreter, Student Database, Sentiment Analysis batch, forensic Image Reassembly, and Ollama Proxy.</div>
      </div>
      <div class="btn-stack">
        <select class="ga0-select" onchange="if(this.value) window.location.href=this.value;">
          <option value="">⚡ Select GA0 Service...</option>
          <option value="/q-code-interpreter-ai-analysis/">Q5: Code Interpreter</option>
          <option value="/q-fastapi/">Q10: Student CSV API</option>
          <option value="/q-fastapi-sentiment-batch/sentiment">Q11: Sentiment Batch</option>
          <option value="/q-image-grayscale-rebuild/">Q14: Image Rebuild</option>
          <option value="/q-move-rename-files/">Q16: Move/Rename Files</option>
          <option value="/q-ollama/">Q18: Ollama Proxy</option>
          <option value="/q-vercel-latency/">Q25: Vercel Latency API</option>
        </select>
      </div>
    </div>
  </div>

  <div class="footer">
    T22026 IITM TDS Solver Gateway &nbsp;·&nbsp; Powered by FastAPI
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

# Mount GA3 Multi-Tenant Service Hub
ga3 = load_app("ga3_app", BASE / "T22026" / "GA3" / "app.py")
app.mount("/ga3", ga3)
