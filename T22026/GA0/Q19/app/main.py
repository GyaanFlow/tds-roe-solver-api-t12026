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

Q19_UI = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Q19 API</title><style>body{font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(120deg,#eefbf3,#edf4ff);margin:0}.wrap{max-width:980px;margin:24px auto;padding:20px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}input{width:100%;padding:10px;border:1px solid #cfd8e3;border-radius:10px}button{background:#0f5132;color:#fff;border:0;padding:10px 14px;border-radius:10px;cursor:pointer}pre{background:#0b1020;color:#d1e7ff;padding:12px;border-radius:10px;overflow:auto}</style></head><body><div class='wrap'><div class='card'><h2>T22026 GA0 Q19: Replace Across Files API</h2><p>Routes: <code>/q19/solve</code>, <code>/ga0/q19/solve</code>, <code>/t22026/ga0/q19/solve</code></p><p>Upload zip and provide your email.</p><input id='email' placeholder='you@example.com'><br><br><input type='file' id='zip' accept='.zip'><br><br><button onclick='run()'>Solve</button><div id='out' style='margin-top:12px'></div></div></div><script>async function run(){const e=document.getElementById('email').value.trim();const f=document.getElementById('zip').files[0];if(!e||!f){document.getElementById('out').textContent='Provide email and zip.';return;}const fd=new FormData();fd.append('email',e);fd.append('zip_file',f);const r=await fetch('ga0/q19/solve',{method:'POST',body:fd});const j=await r.json(); const out=document.getElementById('out'); if(!r.ok){out.innerHTML=<div style='padding:10px;border-radius:10px;background:#fee2e2;color:#991b1b'></div>; return;} out.innerHTML=<div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'><div style='padding:10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px'><b>Request ID</b><br></div><div style='padding:10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px'><b>Email</b><br></div><div style='padding:10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px'><b>Files Processed</b><br></div><div style='padding:10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px'><b>Files Modified</b><br></div></div><div style='margin-top:10px;padding:10px;background:#ecfeff;border:1px solid #bae6fd;border-radius:10px'><b>SHA256</b><br><code></code></div>;}</script></body></html>
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





