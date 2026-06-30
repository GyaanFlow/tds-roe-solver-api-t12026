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
  <title>T22026 GA0 API Hub Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
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
      --glass-blur: blur(16px);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background-color: var(--bg);
      background-image: 
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(168, 85, 247, 0.1) 0px, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }
    .container {
      width: 100%;
      max-width: 1100px;
    }
    .header {
      text-align: center;
      margin-bottom: 40px;
    }
    .header h1 {
      font-size: 2.5rem;
      font-weight: 700;
      background: linear-gradient(135deg, #a5b4fc 0%, #6366f1 50%, #4338ca 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 12px;
    }
    .badge {
      display: inline-block;
      padding: 6px 12px;
      background: rgba(99, 102, 241, 0.1);
      border: 1px solid rgba(99, 102, 241, 0.3);
      border-radius: 20px;
      color: #a5b4fc;
      font-size: 0.85rem;
      font-weight: 500;
      margin-bottom: 15px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .tile {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 24px;
      box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
      transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
      backdrop-filter: var(--glass-blur);
      -webkit-backdrop-filter: var(--glass-blur);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .tile:hover {
      border-color: var(--border-hover);
      transform: translateY(-4px);
      box-shadow: 0 15px 35px rgba(99, 102, 241, 0.15);
    }
    .tile-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 14px;
    }
    .tile-title {
      font-size: 1.2rem;
      font-weight: 600;
      color: #f3f4f6;
    }
    .status-badge {
      font-size: 0.75rem;
      padding: 3px 8px;
      border-radius: 10px;
      font-weight: 600;
    }
    .status-badge.active {
      background: rgba(16, 185, 129, 0.1);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .tile-desc {
      font-size: 0.9rem;
      color: var(--muted);
      line-height: 1.5;
      margin-bottom: 20px;
      flex-grow: 1;
    }
    .tile-actions {
      display: flex;
      gap: 10px;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 18px;
      font-family: inherit;
      font-size: 0.85rem;
      font-weight: 600;
      color: #ffffff;
      background: var(--accent);
      border: none;
      border-radius: 10px;
      cursor: pointer;
      transition: all 0.2s ease;
      text-decoration: none;
      flex: 1;
      text-align: center;
    }
    .btn:hover {
      background: var(--accent-hover);
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text);
      border: 1px solid rgba(255, 255, 255, 0.08);
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.1);
    }
    .footer {
      text-align: center;
      color: var(--muted);
      font-size: 0.85rem;
      margin-top: 30px;
      padding-top: 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <span class="badge">Multi-App Gateway Mounted</span>
      <h1>GA0 Unified API Hub</h1>
      <p style="color: var(--muted); max-width: 600px; margin: 0 auto; font-size: 1.05rem; line-height: 1.6;">
        All seven IITM TDS programming services are live, interactive, and optimized for final submission evaluation.
      </p>
    </div>

    <div class="grid">
      <!-- Q5 -->
      <div class="tile">
        <div>
          <div class="tile-header">
            <span class="tile-title">Q5: Code Interpreter</span>
            <span class="status-badge active">Active</span>
          </div>
          <p class="tile-desc">
            Python execution sandbox with secure traceback-based error line number extraction.
          </p>
          <p style="font-size:0.78rem; color:#818cf8; font-family:monospace; margin-bottom:6px;">
            Exam URL: <strong>/q-code-interpreter-ai-analysis</strong>
          </p>
        </div>
        <div class="tile-actions">
          <a href="/q-code-interpreter-ai-analysis/" class="btn">Open Playground</a>
          <a href="/q-code-interpreter-ai-analysis/health" class="btn btn-secondary">Health</a>
        </div>
      </div>

      <!-- Q10 -->
      <div class="tile">
        <div>
          <div class="tile-header">
            <span class="tile-title">Q10: Student CSV API</span>
            <span class="status-badge active">Active</span>
          </div>
          <p class="tile-desc">
            FastAPI database server filtering students dynamically with Multi-Query list matching.
          </p>
          <p style="font-size:0.78rem; color:#818cf8; font-family:monospace; margin-bottom:6px;">
            Exam URL: <strong>/q-fastapi/api</strong>
          </p>
        </div>
        <div class="tile-actions">
          <a href="/q-fastapi/" class="btn">Open Playground</a>
          <a href="/q-fastapi/health" class="btn btn-secondary">Health</a>
        </div>
      </div>

      <!-- Q11 -->
      <div class="tile">
        <div>
          <div class="tile-header">
            <span class="tile-title">Q11: Sentiment Batch</span>
            <span class="status-badge active">Active</span>
          </div>
          <p class="tile-desc">
            High-performance natural language pipeline classifying sentiment into happy, sad, and neutral.
          </p>
          <p style="font-size:0.78rem; color:#818cf8; font-family:monospace; margin-bottom:6px;">
            Exam URL: <strong>/q-fastapi-sentiment-batch/sentiment</strong>
          </p>
        </div>
        <div class="tile-actions">
          <a href="/q-fastapi-sentiment-batch/" class="btn">Open Playground</a>
          <a href="/q-fastapi-sentiment-batch/health" class="btn btn-secondary">Health</a>
        </div>
      </div>

      <!-- Q14 -->
      <div class="tile">
        <div>
          <div class="tile-header">
            <span class="tile-title">Q14: Image Rebuild</span>
            <span class="status-badge active">Active</span>
          </div>
          <p class="tile-desc">
            Forensic reassembly jigsaw solver & exact luminance-based grayscale PNG exporter.
          </p>
        </div>
        <div class="tile-actions">
          <a href="/q-image-grayscale-rebuild/" class="btn">Open Playground</a>
          <a href="/q-image-grayscale-rebuild/health" class="btn btn-secondary">Health</a>
        </div>
      </div>

      <!-- Q16 -->
      <div class="tile">
        <div>
          <div class="tile-header">
            <span class="tile-title">Q16: Move/Rename Files</span>
            <span class="status-badge active">Active</span>
          </div>
          <p class="tile-desc">
            Zip extraction pipeline performing flat relocation and digital increment renaming.
          </p>
        </div>
        <div class="tile-actions">
          <a href="/q-move-rename-files/" class="btn">Open Playground</a>
          <a href="/q-move-rename-files/health" class="btn btn-secondary">Health</a>
        </div>
      </div>

      <!-- Q18 -->
      <div class="tile">
        <div>
          <div class="tile-header">
            <span class="tile-title">Q18: Ollama Proxy Helper</span>
            <span class="status-badge active">Active</span>
          </div>
          <p class="tile-desc">
            Diagnostic Ollama reverse proxy designed to meet strict ngrok hostname validation constraints.
          </p>
        </div>
        <div class="tile-actions">
          <a href="/q-ollama/" class="btn">Open Playground</a>
          <a href="/q-ollama/health" class="btn btn-secondary">Health</a>
        </div>
      </div>

    </div>

    <!-- Q25 -->
    <div class="grid" style="margin-top: 20px;">
      <div class="tile">
        <div>
          <div class="tile-header">
            <span class="tile-title">Q25: Vercel Latency API</span>
            <span class="status-badge active">Active</span>
          </div>
          <p class="tile-desc">
            Per-region latency analytics engine: avg, p95, uptime, and threshold breach counting.
          </p>
          <p style="font-size:0.78rem; color:#f59e0b; font-family:monospace; margin-bottom:6px;">
            ⚠️ Deploy to Vercel — exam checks vercel.app hostname
          </p>
        </div>
        <div class="tile-actions">
          <a href="/q-vercel-latency/" class="btn">Open Playground</a>
          <a href="/q-vercel-latency/health" class="btn btn-secondary">Health</a>
        </div>
      </div>
    </div>

    <div class="footer">
      Pro-Tip: Run <code>python verify_endpoints.py</code> to test API compliance locally.
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
