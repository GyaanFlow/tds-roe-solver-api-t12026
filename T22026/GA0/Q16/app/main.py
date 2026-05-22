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
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

APP_NAME = "T22026 GA0 Q16 Move Rename Hash API"
APP_VERSION = "1.0.0"
MAX_ZIP_MB = int(os.getenv("MAX_ZIP_MB", "40"))
WORK_ROOT = Path(os.getenv("Q16_WORK_ROOT", "work"))
WORK_ROOT.mkdir(parents=True, exist_ok=True)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DIGIT_MAP = str.maketrans({str(i): str((i + 1) % 10) for i in range(10)})


class Q16Response(BaseModel):
    request_id: str
    email: str
    files_moved: int
    files_renamed: int
    answer_sha256: str
    answer_line: str


app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

Q16_UI = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>Q16 - Move, Rename & Hash Solver</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #10b981;
      --primary-hover: #059669;
      --bg: #0f172a;
      --card-bg: rgba(30, 41, 59, 0.7);
      --border: rgba(255, 255, 255, 0.08);
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at top left, #0f172a, #1e1b4b, #0f172a);
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
      background: linear-gradient(to right, #34d399, #3b82f6);
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
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.15);
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
      background: rgba(16, 185, 129, 0.03);
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
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      border: 0;
      padding: 14px;
      font-size: 1rem;
      font-weight: 600;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    button.btn-solve:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);
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
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(59, 130, 246, 0.15));
      border: 1px solid rgba(16, 185, 129, 0.25);
      border-radius: 16px;
      padding: 20px;
      text-align: center;
      box-shadow: inset 0 1px 1px rgba(255,255,255,0.1);
    }
    .hash-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #34d399;
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
      color: #38bdf8;
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
      <h2>Q16: Move, Rename & Hash Solver</h2>
      <p>Upload the task zip file, enter your registered student email, and compute the correct directory hash instantly.</p>
      
      <div class="routes">
        API Route: <code>POST /ga0/q16/solve</code>
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
        </div>
        <input type='file' id='zip' accept='.zip' style="display: none;" onchange="updateFileLabel(this)">
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
        label.style.color = '#34d399';
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
      
      const base = window.location.href.replace(/\/$/, '');
      const prefix = base.endsWith('/q16') ? base : (window.location.origin + '/q16');
      try {
        const r = await fetch(prefix + '/ga0/q16/solve', { method: 'POST', body: fd });
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
              <span>FILES MOVED</span>
              <strong>\${j.files_moved}</strong>
            </div>
            <div class="result-tile">
              <span>FILES RENAMED</span>
              <strong>\${j.files_renamed}</strong>
            </div>
          </div>
          <div class="hash-card">
            <div class="hash-title">✅ SUBMIT THIS HASH FOR Q16</div>
            <div class="hash-value" id="hash-text">\${j.answer_sha256}</div>
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
</html>"""


def validate_email(email: str) -> str:
    e = (email or "").strip().lower()
    if not EMAIL_RE.match(e):
        raise HTTPException(status_code=400, detail="Invalid email format.")
    return e


def _safe_extract(zf: zipfile.ZipFile, target: Path) -> None:
    for member in zf.infolist():
        member_path = Path(member.filename)
        if member_path.is_absolute() or ".." in member_path.parts:
            raise HTTPException(status_code=400, detail="Unsafe zip path detected.")
    zf.extractall(target)


def _flatten_files(extract_dir: Path, flat_dir: Path) -> int:
    moved = 0
    for root, _, files in os.walk(extract_dir):
        for fname in files:
            src = Path(root) / fname
            dest = flat_dir / fname
            shutil.move(str(src), str(dest))
            moved += 1
    return moved


def _rename_advance_digits(flat_dir: Path) -> int:
    renamed = 0
    # Sort in reverse order to prevent intermediate digit shift collisions (e.g. file1 -> file2 when file2 exists)
    for p in sorted(flat_dir.iterdir(), key=lambda x: x.name, reverse=True):
        if not p.is_file():
            continue
        new_name = p.name.translate(DIGIT_MAP)
        target = flat_dir / new_name
        p.rename(target)
        renamed += 1
    return renamed



def _compute_answer(flat_dir: Path) -> tuple[str, str]:
    lines: List[str] = []
    for p in sorted(flat_dir.iterdir(), key=lambda x: x.name):
        if not p.is_file():
            continue
        try:
            content = p.read_text(encoding="utf-8", errors="strict").splitlines()
            for line in content:
                if line != "":
                    lines.append(f"{p.name}:{line}")
        except UnicodeDecodeError:
            continue
    lines.sort()
    joined = "\n".join(lines) + ("\n" if lines else "")
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()
    return digest, f"{digest}  -"


def solve_zip(email: str, zip_file: UploadFile) -> Q16Response:
    user_email = validate_email(email)
    if not zip_file.filename or not zip_file.filename.lower().endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    data = zip_file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded zip is empty.")
    if len(data) > MAX_ZIP_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Zip too large. Max {MAX_ZIP_MB} MB.")

    request_id = f"q16-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    base = Path(tempfile.mkdtemp(prefix=request_id + "-", dir=str(WORK_ROOT)))
    extract_dir = base / "extracted"
    flat_dir = base / "flat"
    extract_dir.mkdir(parents=True, exist_ok=True)
    flat_dir.mkdir(parents=True, exist_ok=True)

    try:
        zip_path = base / "input.zip"
        zip_path.write_bytes(data)

        with zipfile.ZipFile(zip_path, "r") as zf:
            _safe_extract(zf, extract_dir)

        moved = _flatten_files(extract_dir, flat_dir)
        renamed = _rename_advance_digits(flat_dir)
        digest, answer_line = _compute_answer(flat_dir)

        return Q16Response(
            request_id=request_id,
            email=user_email,
            files_moved=moved,
            files_renamed=renamed,
            answer_sha256=digest,
            answer_line=answer_line,
        )
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file.")
    finally:
        shutil.rmtree(base, ignore_errors=True)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return Q16_UI


@app.get("/q16", response_class=HTMLResponse)
def home_q16() -> str:
    return Q16_UI


@app.get("/q16/", response_class=HTMLResponse)
def home_q16_slash() -> str:
    return Q16_UI


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}


@app.post("/q16/solve", response_model=Q16Response)
def q16_solve(email: str = Form(...), zip_file: UploadFile = File(...)) -> Q16Response:
    return solve_zip(email, zip_file)


@app.post("/ga0/q16/solve", response_model=Q16Response)
def q16_solve_ga0(email: str = Form(...), zip_file: UploadFile = File(...)) -> Q16Response:
    return solve_zip(email, zip_file)


@app.post("/t22026/ga0/q16/solve", response_model=Q16Response)
def q16_solve_t22026(email: str = Form(...), zip_file: UploadFile = File(...)) -> Q16Response:
    return solve_zip(email, zip_file)





