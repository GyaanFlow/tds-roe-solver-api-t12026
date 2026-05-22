from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from typing import List, Optional

import requests
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

APP_NAME = "Q5 Code Interpreter API"
APP_VERSION = "1.0.0"
EXEC_TIMEOUT_SECONDS = int(os.getenv("EXEC_TIMEOUT_SECONDS", "4"))
MAX_CODE_CHARS = int(os.getenv("MAX_CODE_CHARS", "12000"))
AIPIPE_BASE_URL = os.getenv("AIPIPE_BASE_URL", "https://aipipe.org/openai/v1/chat/completions")
AIPIPE_MODEL = os.getenv("AIPIPE_MODEL", "openai/gpt-4.1-nano")


class CodeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=MAX_CODE_CHARS)
    aipipe_token: Optional[str] = None


class CodeResponse(BaseModel):
    error: List[int]
    result: str


def extract_primary_error_lines(traceback_text: str) -> List[int]:
    # Matches only <string> frames inside the dynamic exec block
    matches = re.findall(r'File\s+"<string>",\s+line\s+(\d+)', traceback_text)
    if not matches:
        return []
    # The last match in the traceback is the innermost frame where the exception occurred
    return [int(matches[-1])]


def execute_python_code(code: str) -> dict:
    wrapped = textwrap.dedent(
        f"""
        import sys
        import traceback

        code = {code!r}
        namespace = {{}}
        try:
            exec(code, namespace)
        except Exception:
            traceback.print_exc()
            sys.exit(1)
        """
    )

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as tmp:
        tmp.write(wrapped)
        script_path = tmp.name

    try:
        proc = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=EXEC_TIMEOUT_SECONDS,
            check=False,
        )
        if proc.returncode == 0:
            return {"success": True, "output": proc.stdout}
        stderr = proc.stderr or "Execution failed without traceback."
        return {"success": False, "output": stderr}
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "output": f"TimeoutError: execution exceeded {EXEC_TIMEOUT_SECONDS} seconds.",
        }
    finally:
        try:
            os.remove(script_path)
        except OSError:
            pass


def analyze_error_with_ai(code: str, tb: str, token: str) -> List[int]:
    prompt = (
        "Analyze this Python code and traceback. Return only compact JSON: "
        '{"error_lines":[int,...]}. Include only the line number(s) where the exception '
        "is actually raised based on traceback frames.\n\n"
        f"CODE:\n{code}\n\nTRACEBACK:\n{tb}"
    )

    payload = {
        "model": AIPIPE_MODEL,
        "temperature": 0,
        "messages": [
            {"role": "system", "content": "You are a strict JSON-only evaluator."},
            {"role": "user", "content": prompt},
        ],
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    resp = requests.post(AIPIPE_BASE_URL, headers=headers, json=payload, timeout=20)
    if resp.status_code >= 400:
        raise HTTPException(status_code=502, detail=f"AIPipe request failed ({resp.status_code}).")

    try:
        content = resp.json()["choices"][0]["message"]["content"].strip()
        parsed = json.loads(content)
        lines = parsed.get("error_lines", [])
        if not isinstance(lines, list):
            return []
        clean = [int(x) for x in lines if str(x).isdigit() and int(x) > 0]
        return sorted(set(clean))[:5]
    except Exception:
        return []


def resolve_token(req: CodeRequest, header_token: Optional[str]) -> str:
    token = req.aipipe_token or header_token or ""
    token = token.strip()
    if not token:
        raise HTTPException(
            status_code=400,
            detail="Missing AIPipe token. Provide 'aipipe_token' in JSON or 'X-AIPipe-Token' header.",
        )
    return token


app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}


@app.post("/code-interpreter", response_model=CodeResponse)
def code_interpreter(req: CodeRequest, x_aipipe_token: Optional[str] = Header(default=None)) -> CodeResponse:
    token = (req.aipipe_token or x_aipipe_token or "").strip()
    execution = execute_python_code(req.code)

    if execution["success"]:
        return CodeResponse(error=[], result=execution["output"])

    tb = execution["output"]
    error_lines = extract_primary_error_lines(tb)

    if token:
        try:
            ai_lines = analyze_error_with_ai(req.code, tb, token)
            if ai_lines:
                error_lines = ai_lines
        except Exception:
            pass

    return CodeResponse(error=error_lines, result=tb)


@app.post("/ga0/q5/code-interpreter", response_model=CodeResponse)
def code_interpreter_ga0_q5(req: CodeRequest, x_aipipe_token: Optional[str] = Header(default=None)) -> CodeResponse:
    # Strict routed alias for exam-style endpoint naming.
    return code_interpreter(req=req, x_aipipe_token=x_aipipe_token)


@app.post("/t22026/ga0/q5/code-interpreter", response_model=CodeResponse)
def code_interpreter_t22026_ga0_q5(req: CodeRequest, x_aipipe_token: Optional[str] = Header(default=None)) -> CodeResponse:
    # Fully qualified term+GA+question route for long-term compatibility.
    return code_interpreter(req=req, x_aipipe_token=x_aipipe_token)

Q5_UI = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>Q5 - Code Interpreter Service</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #0d9488;
      --primary-hover: #0f766e;
      --bg: #0f172a;
      --card-bg: rgba(30, 41, 59, 0.7);
      --border: rgba(255, 255, 255, 0.08);
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at top left, #0f172a, #042f2e, #0f172a);
      color: var(--text);
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .wrap {
      width: 100%;
      max-width: 700px;
      padding: 24px;
      box-sizing: border-box;
    }
    .card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 32px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    h2 {
      margin-top: 0;
      font-weight: 700;
      font-size: 1.8rem;
      background: linear-gradient(to right, #2dd4bf, #3b82f6);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }
    p {
      color: var(--text-muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }
    .routes {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 12px;
      font-size: 0.85rem;
      margin-bottom: 24px;
    }
    .routes code {
      color: #38bdf8;
    }
    .form-group {
      margin-bottom: 20px;
    }
    label {
      display: block;
      font-weight: 500;
      margin-bottom: 8px;
      font-size: 0.9rem;
      color: #e2e8f0;
    }
    input[type='text'], textarea {
      width: 100%;
      padding: 12px 16px;
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-size: 0.95rem;
      transition: all 0.3s;
      box-sizing: border-box;
      font-family: inherit;
    }
    textarea {
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.9rem;
      resize: vertical;
    }
    input[type='text']:focus, textarea:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15);
    }
    button.btn-solve {
      width: 100%;
      background: linear-gradient(135deg, #0d9488, #0f766e);
      color: #fff;
      border: 0;
      padding: 14px;
      font-size: 1rem;
      font-weight: 600;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2);
    }
    button.btn-solve:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(13, 148, 136, 0.35);
    }
    #out {
      margin-top: 24px;
      transition: all 0.3s ease;
    }
    .error-card {
      background: rgba(239, 68, 68, 0.1);
      border: 1px solid rgba(239, 68, 68, 0.2);
      color: #fca5a5;
      padding: 16px;
      border-radius: 12px;
      font-size: 0.95rem;
    }
    .success-card {
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      border-radius: 16px;
      padding: 20px;
    }
    .out-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #2dd4bf;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .console-value {
      font-family: monospace;
      font-size: 0.95rem;
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 14px;
      border-radius: 8px;
      color: #38bdf8;
      word-break: break-all;
      white-space: pre-wrap;
    }
    .submit-container {
      background: rgba(13, 148, 136, 0.1);
      border: 1px solid rgba(13, 148, 136, 0.25);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 28px;
      text-align: center;
    }
    .submit-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #2dd4bf;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .submit-url-box {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 12px;
      font-family: monospace;
      font-size: 0.95rem;
      color: #2dd4bf;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      word-break: break-all;
    }
    .btn-copy {
      background: #0d9488;
      color: white;
      border: none;
      padding: 6px 12px;
      border-radius: 8px;
      cursor: pointer;
      font-family: inherit;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all 0.2s;
    }
    .btn-copy:hover {
      background: #0f766e;
    }
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #10b981;
      color: white;
      padding: 12px 24px;
      border-radius: 8px;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      z-index: 1000;
    }
    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'>
      <h2>Q5: Code Interpreter Service</h2>
      <p>Execute arbitrary Python code and dynamically trace line numbers for primary execution errors using deep traceback parsing.</p>
      
      <div class="routes">
        API Route: <code>POST /ga0/q5/code-interpreter</code>
      </div>

      <div class='submit-container'>
        <div class='submit-title'>Submit this endpoint URL on the exam page</div>
        <div class='submit-url-box'>
          <span id='sub-url'></span>
          <button class='btn-copy' onclick='copyEndpoint()'>Copy URL</button>
        </div>
      </div>

      <div class="form-group">
        <label for="tok">AIPipe Token (Optional)</label>
        <input type="text" id="tok" placeholder="aipipe_xxxxxxxx">
      </div>

      <div class="form-group">
        <label for="code">Python Source Code</label>
        <textarea id="code" rows="8"># Test program
a = 10
b = 0
result = a / b  # Division by zero
print(result)</textarea>
      </div>

      <button class="btn-solve" onclick='run()'>⚡ Execute & Analyze Traceback</button>

      <div id='out'></div>
    </div>
  </div>

  <div id="toast" class="toast"></div>

  <script>
    function updateSubmitURL() {
      const subUrl = window.location.origin + '/q5/ga0/q5/code-interpreter';
      document.getElementById('sub-url').innerText = subUrl;
    }
    window.addEventListener('DOMContentLoaded', updateSubmitURL);

    function copyEndpoint() {
      const el = document.getElementById('sub-url');
      navigator.clipboard.writeText(el.innerText).then(() => {
        showToast('✅ Endpoint URL copied to clipboard!');
      });
    }

    function showToast(msg) {
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 3000);
    }

    async function run() {
      const tok = document.getElementById('tok').value.trim();
      const code = document.getElementById('code').value;
      const out = document.getElementById('out');
      
      out.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 12px;">⏳ Compiling and executing code...</div>`;
      
      const base = window.location.href.replace(/\/$/, '');
      const prefix = base.endsWith('/q5') ? base : (window.location.origin + '/q5');
      try {
        const r = await fetch(prefix + '/ga0/q5/code-interpreter', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ aipipe_token: tok || null, code: code })
        });
        const j = await r.json();
        
        if (!r.ok) {
          out.innerHTML = `<div class="error-card">❌ Error: ${j.detail || 'Failed to interpret code.'}</div>`;
          return;
        }
        
        if (j.error && j.error.length > 0) {
          out.innerHTML = `
            <div class="error-card">
              <div class="out-title" style="color: #ef4444;">⚠️ Runtime Error (Failing Line: ${j.error.join(', ')})</div>
              <div class="console-value" style="color: #fca5a5; border-color: rgba(239, 68, 68, 0.2);">${j.result}</div>
            </div>
          `;
        } else {
          out.innerHTML = `
            <div class="success-card">
              <div class="out-title">✅ Execution Success</div>
              <div class="console-value">${j.result || '[No output]'}</div>
            </div>
          `;
        }
      } catch (err) {
        out.innerHTML = `<div class="error-card">❌ Exception: ${err.message}</div>`;
      }
    }
  </script>
</body>
</html>
"""

@app.get('/', response_class=HTMLResponse)
def q5_home() -> str:
    return Q5_UI





