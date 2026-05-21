from __future__ import annotations

import hashlib
import os
import re
import shutil
import tempfile
import time
import uuid
import zipfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

APP_NAME = "T22026 GA0 Q19 Replace Across Files API"
APP_VERSION = "1.0.0"
MAX_ZIP_MB = int(os.getenv("MAX_ZIP_MB", "40"))
WORK_ROOT = Path(os.getenv("Q19_WORK_ROOT", "work"))
WORK_ROOT.mkdir(parents=True, exist_ok=True)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Q19Response(BaseModel):
    request_id: str
    email: str
    files_processed: int
    files_modified: int
    sha256: str
    answer_line: str


app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

Q19_UI = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>Q19 - Replace Across Files Solver</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #7c3aed;
      --primary-hover: #6d28d9;
      --bg: #0f172a;
      --card-bg: rgba(30, 41, 59, 0.7);
      --border: rgba(255, 255, 255, 0.08);
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at top left, #0f172a, #2e1065, #0f172a);
      color: var(--text);
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .wrap {
      width: 100%;
      max-width: 600px;
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
      background: linear-gradient(to right, #a78bfa, #22d3ee);
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
    input[type='text'], input[type='email'] {
      width: 100%;
      padding: 12px 16px;
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-size: 0.95rem;
      transition: all 0.3s;
      box-sizing: border-box;
    }
    input[type='text']:focus, input[type='email']:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
    }
    .file-upload-box {
      border: 2px dashed rgba(255, 255, 255, 0.15);
      border-radius: 16px;
      padding: 24px;
      text-align: center;
      cursor: pointer;
      transition: all 0.3s;
      background: rgba(15, 23, 42, 0.2);
    }
    .file-upload-box:hover {
      border-color: var(--primary);
      background: rgba(124, 58, 237, 0.03);
    }
    .file-upload-box input {
      display: none;
    }
    .file-upload-icon {
      font-size: 2rem;
      margin-bottom: 8px;
    }
    button.btn-solve {
      width: 100%;
      background: linear-gradient(135deg, #7c3aed, #6d28d9);
      color: #fff;
      border: 0;
      padding: 14px;
      font-size: 1rem;
      font-weight: 600;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
    }
    button.btn-solve:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(124, 58, 237, 0.35);
    }
    button.btn-solve:active {
      transform: translateY(0);
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
    .success-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      margin-bottom: 16px;
    }
    .result-tile {
      background: rgba(15, 23, 42, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 14px;
    }
    .result-tile span {
      display: block;
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-bottom: 4px;
    }
    .result-tile strong {
      font-size: 1.05rem;
      color: #f1f5f9;
    }
    .hash-card {
      background: linear-gradient(135deg, rgba(124, 58, 237, 0.15), rgba(34, 211, 238, 0.15));
      border: 1px solid rgba(124, 58, 237, 0.25);
      border-radius: 16px;
      padding: 20px;
      text-align: center;
      box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
    }
    .hash-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #a78bfa;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .hash-value {
      font-family: monospace;
      font-size: 1.1rem;
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.1);
      padding: 12px;
      border-radius: 8px;
      color: #22d3ee;
      word-break: break-all;
      margin-bottom: 12px;
      user-select: all;
    }
    .copy-btn {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.1);
      color: var(--text);
      padding: 6px 12px;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 500;
      transition: all 0.2s;
    }
    .copy-btn:hover {
      background: rgba(255, 255, 255, 0.15);
    }
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'>
      <h2>Q19: Replace Across Files Solver</h2>
      <p>Upload the task zip file, enter your registered student email, and replace all instances of "IITM" with "IIT Madras" while generating the correct verification hash.</p>
      
      <div class="routes">
        API Route: <code>POST /ga0/q19/solve</code>
      </div>

      <div class="form-group">
        <label for="email">Student Email Address</label>
        <input type="email" id="email" placeholder="student@example.com">
      </div>

      <div class="form-group">
        <label>Upload Task ZIP</label>
        <div class="file-upload-box" onclick="document.getElementById('zip').click()">
          <div class="file-upload-icon">📦</div>
          <div id="file-label" style="font-weight: 500;">Click to select file</div>
          <div style="font-size: 0.8rem; color: var(--text-muted); margin-top: 4px;">accepts .zip files</div>
          <input type='file' id='zip' accept='.zip' onchange="updateFileLabel(this)">
        </div>
      </div>

      <button class="btn-solve" onclick='run()'>⚡ Reassemble & Compute Hash</button>

      <div id='out'></div>
    </div>
  </div>

  <script>
    function updateFileLabel(input) {
      const label = document.getElementById('file-label');
      if (input.files && input.files[0]) {
        label.textContent = input.files[0].name;
        label.style.color = '#a78bfa';
      } else {
        label.textContent = 'Click to select file';
        label.style.color = 'var(--text)';
      }
    }

    async function run() {
      const e = document.getElementById('email').value.trim();
      const f = document.getElementById('zip').files[0];
      const out = document.getElementById('out');
      
      if (!e || !f) {
        out.innerHTML = `<div class="error-card">⚠️ Please provide both your email and the task zip file.</div>`;
        return;
      }
      
      out.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 12px;">⏳ Processing ZIP payload and computing checksum...</div>`;
      
      const fd = new FormData();
      fd.append('email', e);
      fd.append('zip_file', f);
      
      try {
        const r = await fetch('ga0/q19/solve', { method: 'POST', body: fd });
        const j = await r.json();
        
        if (!r.ok) {
          out.innerHTML = `<div class="error-card">❌ Error: \${j.detail || 'Failed to process files.'}</div>`;
          return;
        }
        
        out.innerHTML = \`
          <div class="success-grid">
            <div class="result-tile">
              <span>REQUEST ID</span>
              <strong>\${j.request_id}</strong>
            </div>
            <div class="result-tile">
              <span>EMAIL</span>
              <strong>\${j.email}</strong>
            </div>
            <div class="result-tile">
              <span>FILES PROCESSED</span>
              <strong>\${j.files_processed}</strong>
            </div>
            <div class="result-tile">
              <span>FILES MODIFIED</span>
              <strong>\${j.files_modified}</strong>
            </div>
          </div>
          <div class="hash-card">
            <div class="hash-title">✅ SUBMIT THIS HASH FOR Q19</div>
            <div class="hash-value" id="hash-text">\${j.sha256}</div>
            <button class="copy-btn" onclick="copyHash()">📋 Copy Hash</button>
          </div>
        \`;
      } catch (err) {
        out.innerHTML = `<div class="error-card">❌ Exception: \${err.message}</div>`;
      }
    }

    function copyHash() {
      const hashText = document.getElementById('hash-text').innerText;
      navigator.clipboard.writeText(hashText).then(() => {
        const btn = document.querySelector('.copy-btn');
        btn.textContent = '✅ Copied!';
        setTimeout(() => { btn.textContent = '📋 Copy Hash'; }, 2000);
      });
    }
  </script>
</body>
</html>
"""


def validate_email(email: str) -> str:
    e = (email or "").strip().lower()
    if not EMAIL_RE.match(e):
        raise HTTPException(status_code=400, detail="Invalid email format.")
    return e


def safe_extract(zf: zipfile.ZipFile, target: Path) -> None:
    for member in zf.infolist():
        p = Path(member.filename)
        if p.is_absolute() or ".." in p.parts:
            raise HTTPException(status_code=400, detail="Unsafe zip path detected.")
    zf.extractall(target)


def process_files(base_dir: Path) -> tuple[int, int, str, str]:
    txt_files = sorted(
        [p for p in base_dir.rglob("file*.txt") if p.is_file()],
        key=lambda x: str(x.relative_to(base_dir)).lower(),
    )
    if not txt_files:
        raise HTTPException(status_code=400, detail="No target files found (file*.txt).")

    modified = 0
    for p in txt_files:
        raw = p.read_bytes()
        try:
            content = raw.decode("utf-8")
        except UnicodeDecodeError:
            content = raw.decode("latin-1")

        new_content = re.sub(r"IITM", "IIT Madras", content, flags=re.IGNORECASE)
        if new_content != content:
            modified += 1
            p.write_bytes(new_content.encode("utf-8"))

    h = hashlib.sha256()
    for p in txt_files:
        h.update(p.read_bytes())
    digest = h.hexdigest()
    return len(txt_files), modified, digest, f"{digest}  -"


def solve(email: str, zip_file: UploadFile) -> Q19Response:
    user_email = validate_email(email)
    if not zip_file.filename or not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    data = zip_file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded zip is empty.")
    if len(data) > MAX_ZIP_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Zip too large. Max {MAX_ZIP_MB} MB.")

    request_id = f"q19-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    run_dir = Path(tempfile.mkdtemp(prefix=request_id + "-", dir=str(WORK_ROOT)))
    extract_dir = run_dir / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)

    try:
        zip_path = run_dir / "input.zip"
        zip_path.write_bytes(data)

        with zipfile.ZipFile(zip_path, "r") as zf:
            safe_extract(zf, extract_dir)

        files_processed, files_modified, sha, answer_line = process_files(extract_dir)

        return Q19Response(
            request_id=request_id,
            email=user_email,
            files_processed=files_processed,
            files_modified=files_modified,
            sha256=sha,
            answer_line=answer_line,
        )
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file.")
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return Q19_UI


@app.get("/q19", response_class=HTMLResponse)
def home_q19() -> str:
    return Q19_UI


@app.get("/q19/", response_class=HTMLResponse)
def home_q19_slash() -> str:
    return Q19_UI


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}


@app.post("/q19/solve", response_model=Q19Response)
def q19_solve(email: str = Form(...), zip_file: UploadFile = File(...)) -> Q19Response:
    return solve(email, zip_file)


@app.post("/ga0/q19/solve", response_model=Q19Response)
def q19_solve_ga0(email: str = Form(...), zip_file: UploadFile = File(...)) -> Q19Response:
    return solve(email, zip_file)


@app.post("/t22026/ga0/q19/solve", response_model=Q19Response)
def q19_solve_t22026(email: str = Form(...), zip_file: UploadFile = File(...)) -> Q19Response:
    return solve(email, zip_file)





