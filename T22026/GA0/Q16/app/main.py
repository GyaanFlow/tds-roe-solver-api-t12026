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

Q16_UI = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Q16 API</title><style>body{font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(120deg,#eefaf0,#edf3ff);margin:0}.wrap{max-width:980px;margin:24px auto;padding:20px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}input{width:100%;padding:10px;border:1px solid #cfd8e3;border-radius:10px}button{background:#14532d;color:#fff;border:0;padding:10px 14px;border-radius:10px;cursor:pointer}pre{background:#0b1020;color:#d1e7ff;padding:12px;border-radius:10px;overflow:auto}</style></head><body><div class='wrap'><div class='card'><h2>T22026 GA0 Q16: Move Rename Hash API</h2><p>Routes: <code>/q16/solve</code>, <code>/ga0/q16/solve</code>, <code>/t22026/ga0/q16/solve</code></p><p>Upload zip and provide your email.</p><input id='email' placeholder='you@example.com'><br><br><input type='file' id='zip' accept='.zip'><br><br><button onclick='run()'>Solve</button><pre id='out'>Waiting...</pre></div></div><script>async function run(){const e=document.getElementById('email').value.trim();const f=document.getElementById('zip').files[0];if(!e||!f){document.getElementById('out').textContent='Provide email and zip.';return;}const fd=new FormData();fd.append('email',e);fd.append('zip_file',f);const r=await fetch('/ga0/q16/solve',{method:'POST',body:fd});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2);}</script></body></html>
"""


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
            if dest.exists():
                base, suf = dest.stem, dest.suffix
                i = 1
                while True:
                    candidate = flat_dir / f"{base}_{i}{suf}"
                    if not candidate.exists():
                        dest = candidate
                        break
                    i += 1
            shutil.move(str(src), str(dest))
            moved += 1
    return moved


def _rename_advance_digits(flat_dir: Path) -> int:
    renamed = 0
    for p in sorted(flat_dir.iterdir(), key=lambda x: x.name):
        if not p.is_file():
            continue
        new_name = p.name.translate(DIGIT_MAP)
        target = flat_dir / new_name
        if target.exists() and target.resolve() != p.resolve():
            base, suf = Path(new_name).stem, Path(new_name).suffix
            i = 1
            while True:
                candidate = flat_dir / f"{base}_{i}{suf}"
                if not candidate.exists():
                    target = candidate
                    break
                i += 1
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


