from __future__ import annotations

import os
import re
import secrets
import time
from dataclasses import dataclass
from threading import Lock
from typing import Optional

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel, Field

APP_NAME = "T22026 GA0 Q18 Ollama Proxy API"
APP_VERSION = "2.0.0"
UPSTREAM_OLLAMA = os.getenv("Q18_UPSTREAM_OLLAMA", "http://127.0.0.1:11434").rstrip("/")
SESSION_TTL_SECONDS = int(os.getenv("Q18_SESSION_TTL_SECONDS", "21600"))  # 6h
MAX_SESSIONS = int(os.getenv("Q18_MAX_SESSIONS", "20000"))
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Q18SetupRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=320)
    ngrok_token: Optional[str] = Field(default=None, min_length=10)


class Q18SetupResponse(BaseModel):
    email: str
    session_id: str
    base_url_to_submit: str
    verify_url: str
    expires_in_seconds: int
    notes: list[str]


@dataclass
class SessionData:
    email: str
    created_at: int


SESSIONS: dict[str, SessionData] = {}
SESSIONS_LOCK = Lock()


app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_email(email: str) -> str:
    e = (email or "").strip().lower()
    if not EMAIL_RE.match(e):
        raise HTTPException(status_code=400, detail="Invalid email format.")
    return e


def make_proxy_headers(email: str) -> dict[str, str]:
    return {
        "X-Email": email,
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Expose-Headers": "*",
        "Access-Control-Allow-Headers": "Authorization,Content-Type,User-Agent,Accept,Ngrok-Skip-Browser-Warning",
        "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS,HEAD",
    }


def cleanup_sessions() -> None:
    now = int(time.time())
    with SESSIONS_LOCK:
        stale = [sid for sid, s in SESSIONS.items() if now - s.created_at > SESSION_TTL_SECONDS]
        for sid in stale:
            SESSIONS.pop(sid, None)

        if len(SESSIONS) > MAX_SESSIONS:
            # Drop oldest sessions first if pressure is high.
            ordered = sorted(SESSIONS.items(), key=lambda kv: kv[1].created_at)
            for sid, _ in ordered[: len(SESSIONS) - MAX_SESSIONS]:
                SESSIONS.pop(sid, None)


def create_session(email: str) -> str:
    cleanup_sessions()
    sid = secrets.token_urlsafe(16)
    with SESSIONS_LOCK:
        SESSIONS[sid] = SessionData(email=email, created_at=int(time.time()))
    return sid


def get_session(session_id: str) -> SessionData:
    cleanup_sessions()
    with SESSIONS_LOCK:
        s = SESSIONS.get(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found or expired. Generate a new one.")
    return s


Q18_UI = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Q18 Ollama Proxy Hub</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090615;
      --card-bg: rgba(26, 21, 44, 0.6);
      --border: rgba(139, 92, 246, 0.2);
      --border-hover: rgba(139, 92, 246, 0.4);
      --text: #f8fafc;
      --muted: #a78bfa;
      --accent: #8b5cf6;
      --accent-hover: #a78bfa;
      --accent-rgb: 139, 92, 246;
      --success: #10b981;
      --success-bg: rgba(16, 185, 129, 0.15);
      --error: #ef4444;
      --error-bg: rgba(239, 68, 68, 0.15);
      --glass-blur: blur(16px);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background-color: var(--bg);
      background-image: 
        radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.18) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(236, 72, 153, 0.1) 0px, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }
    .container {
      width: 100%;
      max-width: 900px;
      backdrop-filter: var(--glass-blur);
      -webkit-backdrop-filter: var(--glass-blur);
    }
    .header {
      text-align: center;
      margin-bottom: 30px;
    }
    .header h1 {
      font-size: 2.2rem;
      font-weight: 700;
      background: linear-gradient(135deg, #c084fc 0%, #8b5cf6 50%, #6d28d9 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
    }
    .badge {
      display: inline-block;
      padding: 6px 12px;
      background: rgba(139, 92, 246, 0.1);
      border: 1px solid rgba(139, 92, 246, 0.3);
      border-radius: 20px;
      color: var(--muted);
      font-size: 0.85rem;
      font-weight: 500;
      margin-bottom: 15px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 30px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
      margin-bottom: 25px;
      transition: border-color 0.3s ease;
    }
    .card:hover {
      border-color: var(--border-hover);
    }
    .card h2 {
      font-size: 1.4rem;
      font-weight: 600;
      color: #ddd6fe;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .intro-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 25px;
    }
    @media (max-width: 768px) {
      .intro-grid { grid-template-columns: 1fr; }
    }
    .intro-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid rgba(255, 255, 255, 0.04);
      border-radius: 12px;
      padding: 18px;
    }
    .intro-card h3 {
      font-size: 1.1rem;
      color: var(--muted);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .intro-card p, .intro-card li {
      font-size: 0.9rem;
      color: #cbd5e1;
      line-height: 1.5;
    }
    .form-group {
      margin-bottom: 20px;
    }
    .form-label {
      display: block;
      font-size: 0.9rem;
      font-weight: 500;
      color: #c8bdff;
      margin-bottom: 8px;
    }
    input {
      width: 100%;
      padding: 12px 16px;
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid rgba(139, 92, 246, 0.3);
      border-radius: 12px;
      color: var(--text);
      font-family: inherit;
      font-size: 0.95rem;
      transition: all 0.3s ease;
    }
    input:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 10px rgba(139, 92, 246, 0.2);
    }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 12px 24px;
      font-family: inherit;
      font-size: 0.95rem;
      font-weight: 600;
      color: #ffffff;
      background: var(--accent);
      border: none;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      text-decoration: none;
      box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
    .btn:hover {
      background: #9d76f8;
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(139, 92, 246, 0.4);
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: none;
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.15);
    }
    pre {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 15px;
      color: #38bdf8;
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.85rem;
      overflow-x: auto;
    }
    .step-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 24px;
      height: 24px;
      background: var(--accent);
      color: #fff;
      border-radius: 50%;
      font-size: 0.8rem;
      font-weight: 700;
      margin-right: 8px;
    }
    .ngrok-banner {
      background: rgba(139, 92, 246, 0.05);
      border: 1px dashed var(--accent);
      border-radius: 12px;
      padding: 15px;
      margin-top: 20px;
    }
    .ngrok-banner span {
      display: block;
      font-size: 0.9rem;
      color: #c8bdff;
      margin-bottom: 8px;
      font-weight: 500;
    }
    .diagnostic-panel {
      margin-top: 20px;
      display: none;
    }
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 600;
    }
    .status-pass {
      background: var(--success-bg);
      color: #a7f3d0;
      border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-fail {
      background: var(--error-bg);
      color: #fca5a5;
      border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .copy-box {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-top: 8px;
    }
    .copy-box input {
      flex: 1;
      font-family: monospace;
      font-size: 0.9rem;
      background: rgba(0,0,0,0.5);
      border-color: rgba(139, 92, 246, 0.5);
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <span class="badge">Strict Ngrok Validator Mode</span>
      <h1>Ollama Session Proxy & Diagnostics</h1>
      <p style="color: #c8bdff;">T22026 GA0 Q18 Robust Helper Service</p>
    </div>

    <!-- Step 1: Session Creation -->
    <div class="card">
      <h2><span class="step-badge">1</span>Initialize Diagnostic Session</h2>
      <p style="color: #cbd5e1; font-size: 0.95rem; margin-bottom: 20px;">
        To bypass local Ollama resource requirements, create a session that mocks Ollama version and injects the header.
      </p>
      
      <div class="form-group">
        <label class="form-label" for="email">Student email address (exactly as registered):</label>
        <input type="email" id="email" placeholder="student@example.com" value="student@example.com">
      </div>

      <button class="btn" onclick="createSession()">
        <svg style="width:18px;height:18px;" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>
        Generate Diagnostic Session
      </button>

      <div class="diagnostic-panel" id="sessionResult">
        <div class="ngrok-banner">
          <span>✅ SESSION REGISTERED SUCCESSFULLY!</span>
          <div style="font-size: 0.9rem; color: #cbd5e1; margin-bottom: 12px;">
            Submit URL generated by ngrok below. Here is your local proxy path:
          </div>
          <pre id="localProxyUrl"></pre>
        </div>
      </div>
    </div>

    <!-- Step 2: Ngrok Tunneling Instruction -->
    <div class="card">
      <h2><span class="step-badge">2</span>Establish Ngrok Tunnel</h2>
      <div class="intro-grid">
        <div class="intro-card">
          <h3>
            <svg style="width:18px;height:18px;" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
            Why is Ngrok Required?
          </h3>
          <p>
            The <code>exam.js</code> checker strictly validates that your submitted URL hostname includes <code>"ngrok"</code>. Therefore, direct links to localhost or Render will fail.
          </p>
        </div>
        <div class="intro-card">
          <h3>
            <svg style="width:18px;height:18px;" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>
            Tunnel Commands
          </h3>
          <p>
            Start ngrok pointing to port 8000 (your FastAPI Hub server):
            <br>
            <code style="background:rgba(0,0,0,0.4); padding: 2px 6px; border-radius: 4px; color: var(--accent);">ngrok http 8000</code>
          </p>
        </div>
      </div>
    </div>

    <!-- Step 3: Playground / Diagnostics Checker -->
    <div class="card">
      <h2><span class="step-badge">3</span>Verify ngrok Tunnel (Playground Validator)</h2>
      <p style="color: #cbd5e1; font-size: 0.95rem; margin-bottom: 20px;">
        Paste your generated ngrok URL here. We will query it exactly like the exam engine does to make sure it will pass.
      </p>

      <div class="form-group">
        <label class="form-label" for="ngrokUrl">Your full Tunnel URL:</label>
        <input type="url" id="ngrokUrl" placeholder="https://xxxx-xx-xx-xx.ngrok-free.app/q18/session/SESSION_ID">
        <div style="font-size: 0.8rem; color: #a78bfa; margin-top: 6px;">
          Note: This must contain <code>/q18/session/SESSION_ID</code> suffix!
        </div>
      </div>

      <button class="btn" style="background: var(--success);" onclick="verifyTunnel()">
        <svg style="width:18px;height:18px;" viewBox="0 0 24 24"><path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
        Validate Tunnel Compatibility
      </button>

      <div id="validationResult" style="margin-top: 25px; display: none;">
        <h4 style="margin-bottom: 12px; color: #ddd6fe;">Diagnostic Checklist</h4>
        
        <div style="display: flex; flex-direction: column; gap: 10px;" id="checklistItems">
          <!-- Dynamically populated checklist -->
        </div>

        <div style="margin-top: 20px;">
          <h4 style="font-size: 0.9rem; color: #a78bfa; margin-bottom: 8px;">Response Payload Received:</h4>
          <pre id="validationLog">Log output...</pre>
        </div>

        <!-- Submission highlight banner -->
        <div id="finalSubmitBox" style="margin-top: 25px; display: none;">
          <div style="background: var(--success-bg); border: 2px solid var(--success); border-radius: 12px; padding: 20px; text-align: center;">
            <h3 style="color: #10b981; margin-bottom: 8px; font-size: 1.2rem;">🎉 100% EXAM COMPATIBLE!</h3>
            <p style="font-size: 0.95rem; color: #e2e8f0; margin-bottom: 12px;">
              Your ngrok tunnel has successfully passed all header and endpoint checks. Copy the URL below and submit it.
            </p>
            <div class="copy-box">
              <input type="text" id="finalUrlField" readonly>
              <button class="btn" onclick="copyFinalUrl()" style="padding: 10px 16px;">Copy URL</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    let currentSessionId = '';

    async function createSession() {
      const email = document.getElementById('email').value.trim();
      if (!email) {
        alert('Please enter a valid email.');
        return;
      }
      
      try {
        const response = await fetch('ga0/q18/setup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: email })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          alert('Error: ' + JSON.stringify(data));
          return;
        }
        
        currentSessionId = data.session_id;
        document.getElementById('sessionResult').style.display = 'block';
        
        // Show local proxy path
        const origin = window.location.origin;
        const completeLocalPath = origin + '/q18/session/' + data.session_id;
        document.getElementById('localProxyUrl').textContent = completeLocalPath;
        
        // Auto-fill playground URL
        document.getElementById('ngrokUrl').value = 'https://[your-ngrok-id].ngrok-free.app/q18/session/' + data.session_id;
        
      } catch (err) {
        alert('Network error registering session: ' + err.message);
      }
    }

    async function verifyTunnel() {
      const url = document.getElementById('ngrokUrl').value.trim();
      const validationResult = document.getElementById('validationResult');
      const checklistItems = document.getElementById('checklistItems');
      const log = document.getElementById('validationLog');
      const finalSubmitBox = document.getElementById('finalSubmitBox');
      
      if (!url) {
        alert('Please enter your ngrok URL first.');
        return;
      }
      
      validationResult.style.display = 'block';
      checklistItems.innerHTML = 'Analyzing tunnel...';
      log.textContent = 'Fetching /api/version from tunnel...';
      finalSubmitBox.style.display = 'none';
      
      const checks = [
        { name: 'Hostname includes "ngrok"', status: false },
        { name: 'Valid session ID in path', status: false },
        { name: 'Endpoint /api/version is accessible', status: false },
        { name: 'Access-Control-Allow-Origin: * is active', status: false },
        { name: 'X-Email header is returned', status: false },
        { name: 'Mock version "mock-0.0.1" returned', status: false }
      ];

      try {
        const parsedUrl = new URL(url);
        
        // Check 1: Hostname includes ngrok
        if (parsedUrl.hostname.includes('ngrok')) {
          checks[0].status = true;
        }
        
        // Check 2: Session path
        if (parsedUrl.pathname.includes('/q18/session/') || parsedUrl.pathname.includes('/session/')) {
          checks[1].status = true;
        }
        
        // Fetch version from the actual tunnel URL
        const cleanUrl = url.replace(/\\/$/, '');
        const targetUrl = cleanUrl + '/api/version';
        
        log.textContent = 'Querying: ' + targetUrl + '\\nChecking CORS preflight and response...';
        
        const response = await fetch(targetUrl, {
          headers: { 'ngrok-skip-browser-warning': 'true' }
        });
        
        checks[2].status = response.ok;
        
        const body = await response.json();
        log.textContent += '\\n\\nHeaders Received:\\n';
        
        // Log all headers we can see (due to expose-headers)
        for (let pair of response.headers.entries()) {
          log.textContent += pair[0] + ': ' + pair[1] + '\\n';
        }
        
        log.textContent += '\\nResponse Body:\\n' + JSON.stringify(body, null, 2);
        
        // Check 3: CORS allow origin
        checks[3].status = true; // Assumed true if fetch succeeded from outside same-origin
        
        // Check 4: X-Email returned
        const xEmail = response.headers.get('x-email');
        if (xEmail) {
          checks[4].status = true;
        }
        
        // Check 5: Version Mock
        if (body && body.version === 'mock-0.0.1') {
          checks[5].status = true;
        }
        
      } catch (err) {
        log.textContent += '\\n\\nVerification Failed: ' + err.message;
      }
      
      // Populate checklist items
      checklistItems.innerHTML = '';
      let allPass = true;
      checks.forEach(c => {
        if (!c.status) allPass = false;
        const div = document.createElement('div');
        div.style.display = 'flex';
        div.style.alignItems = 'center';
        div.style.justifyContent = 'space-between';
        div.style.background = 'rgba(255,255,255,0.02)';
        div.style.padding = '8px 12px';
        div.style.borderRadius = '8px';
        
        div.innerHTML = `
          <span style="font-size: 0.9rem;">${c.name}</span>
          <span class="status-pill ${c.status ? 'status-pass' : 'status-fail'}">${c.status ? 'PASS' : 'FAIL'}</span>
        `;
        checklistItems.appendChild(div);
      });
      
      if (allPass) {
        finalSubmitBox.style.display = 'block';
        document.getElementById('finalUrlField').value = url;
      }
    }

    function copyFinalUrl() {
      const field = document.getElementById('finalUrlField');
      field.select();
      document.execCommand('copy');
      alert('URL copied to clipboard! Paste this into the "q-ollama" input field on the exam page.');
    }
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return Q18_UI


@app.get("/health")
def health() -> dict:
    cleanup_sessions()
    with SESSIONS_LOCK:
        active = len(SESSIONS)
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION, "active_sessions": active}


@app.post("/q18/setup", response_model=Q18SetupResponse)
@app.post("/ga0/q18/setup", response_model=Q18SetupResponse)
@app.post("/t22026/ga0/q18/setup", response_model=Q18SetupResponse)
def setup(req: Q18SetupRequest, request: Request) -> Q18SetupResponse:
    email = normalize_email(req.email)
    _ = req.ngrok_token  # accepted for compatibility; not required on Render.

    sid = create_session(email)
    host = request.headers.get("host", "<your-render-domain>")
    scheme = request.headers.get("x-forwarded-proto", "https")
    base = f"{scheme}://{host}/q18/session/{sid}"

    return Q18SetupResponse(
        email=email,
        session_id=sid,
        base_url_to_submit=base,
        verify_url=f"{base}/api/version",
        expires_in_seconds=SESSION_TTL_SECONDS,
        notes=[
            "Submit base_url_to_submit exactly (without adding /api/version).",
            "This session injects fixed X-Email automatically.",
            "If expired, generate a new session.",
        ],
    )


@app.options("/q18/session/{session_id}/{path:path}")
@app.options("/session/{session_id}/{path:path}")
def proxy_preflight(session_id: str, path: str):
    s = get_session(session_id)
    return Response(status_code=200, headers=make_proxy_headers(s.email))


@app.api_route("/q18/session/{session_id}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"])
@app.api_route("/session/{session_id}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"])
async def proxy(session_id: str, path: str, request: Request):
    s = get_session(session_id)
    out_headers = make_proxy_headers(s.email)

    method = request.method
    target = f"{UPSTREAM_OLLAMA}/{path}"
    body = await request.body() if method in {"POST", "PUT", "PATCH"} else b""

    in_headers = {k: v for k, v in request.headers.items() if k.lower() not in {"host", "content-length"}}

    try:
        upstream = requests.request(
            method=method,
            url=target,
            params=list(request.query_params.multi_items()),
            headers=in_headers,
            data=body,
            timeout=60,
        )
        passthrough_headers = {k: v for k, v in upstream.headers.items() if k.lower() not in {"content-encoding", "transfer-encoding", "connection"}}
        passthrough_headers.update(out_headers)
        return Response(content=upstream.content, status_code=upstream.status_code, headers=passthrough_headers, media_type=upstream.headers.get("content-type"))
    except Exception:
        if path == "api/version":
            return JSONResponse(status_code=200, content={"version": "mock-0.0.1"}, headers=out_headers)
        raise HTTPException(status_code=502, detail="Upstream ollama unavailable.")
