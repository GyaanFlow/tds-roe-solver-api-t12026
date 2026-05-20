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
    aipipe_token: Optional[str] = Field(default=None, min_length=20)


class CodeResponse(BaseModel):
    error: List[int]
    result: str


def extract_primary_error_lines(traceback_text: str) -> List[int]:
    # Matches: File "...", line 12
    matches = re.findall(r'File\s+"[^"]+",\s+line\s+(\d+)', traceback_text)
    if not matches:
        return []
    # Typically last frames are closest to failure site.
    deduped = []
    for m in reversed(matches):
        line_no = int(m)
        if line_no not in deduped:
            deduped.append(line_no)
    return sorted(deduped[:3])


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
    token = resolve_token(req, x_aipipe_token)
    execution = execute_python_code(req.code)

    if execution["success"]:
        return CodeResponse(error=[], result=execution["output"])

    tb = execution["output"]
    # Fast heuristic first; AI fallback improves alignment with Q5 style checker.
    error_lines = extract_primary_error_lines(tb)
    try:
        ai_lines = analyze_error_with_ai(req.code, tb, token)
        if ai_lines:
            error_lines = ai_lines
    except HTTPException:
        # Keep deterministic fallback if AI call fails.
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

Q5_UI = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Q5 API</title><style>body{font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(120deg,#f8ffef,#e9f6ff);margin:0}.wrap{max-width:960px;margin:24px auto;padding:20px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}textarea,input{width:100%;padding:10px;border:1px solid #cfd8e3;border-radius:10px}button{background:#0f766e;color:#fff;border:0;padding:10px 14px;border-radius:10px;cursor:pointer}pre{background:#0b1020;color:#d1e7ff;padding:12px;border-radius:10px;overflow:auto}</style></head><body><div class='wrap'><div class='card'><h2>T22026 GA0 Q5: Code Interpreter API</h2><p>Routes: <code>/code-interpreter</code>, <code>/ga0/q5/code-interpreter</code>, <code>/t22026/ga0/q5/code-interpreter</code></p><p>Provide AIPipe token and Python code.</p><input id='tok' placeholder='AIPipe token'><br><br><textarea id='code' rows='8'>print('hello from q5')</textarea><br><br><button onclick='run()'>Run</button><pre id='out'>Waiting...</pre></div></div><script>async function run(){const r=await fetch('/ga0/q5/code-interpreter',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({aipipe_token:document.getElementById('tok').value,code:document.getElementById('code').value})});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2);}</script></body></html>
"""

@app.get('/', response_class=HTMLResponse)
def q5_home() -> str:
    return Q5_UI




