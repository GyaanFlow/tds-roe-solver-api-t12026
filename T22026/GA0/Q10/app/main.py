from __future__ import annotations

import csv
import hashlib
import os
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

APP_NAME = "T22026 GA0 Q10 Student API"
APP_VERSION = "1.0.0"
DATA_FILE = Path(os.getenv("Q10_CSV_PATH", "q-fastapi.csv"))
MAX_CLASS_FILTERS = int(os.getenv("MAX_CLASS_FILTERS", "100"))


class Student(BaseModel):
    studentId: int | str
    class_: str

    def to_api_dict(self) -> dict:
        return {"studentId": self.studentId, "class": self.class_}


class StudentsResponse(BaseModel):
    students: List[dict]


def normalize_student_id(raw: str):
    value = (raw or "").strip()
    if value == "":
        return ""
    try:
        return int(value)
    except ValueError:
        return value


@lru_cache(maxsize=1)
def load_students() -> List[Student]:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"CSV file not found: {DATA_FILE}")

    students: List[Student] = []
    with DATA_FILE.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or "studentId" not in reader.fieldnames or "class" not in reader.fieldnames:
            raise ValueError("CSV must contain 'studentId' and 'class' columns")

        for row in reader:
            students.append(Student(studentId=normalize_student_id(row.get("studentId", "")), class_=str(row.get("class", "")).strip()))

    return students


def dataset_fingerprint(students: List[Student]) -> str:
    h = hashlib.sha256()
    for s in students:
        h.update(str(s.studentId).encode("utf-8"))
        h.update(b"|")
        h.update(s.class_.encode("utf-8"))
        h.update(b"\n")
    return h.hexdigest()[:16]


app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_check() -> None:
    # Warm cache and fail fast on bad CSV schema.
    _ = load_students()


@app.get("/health")
def health() -> dict:
    students = load_students()
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
        "rows": len(students),
        "dataset": dataset_fingerprint(students),
    }


@app.get("/api", response_model=StudentsResponse)
def get_students(class_: Optional[List[str]] = Query(default=None, alias="class")) -> StudentsResponse:
    students = load_students()

    if class_ is None:
        return StudentsResponse(students=[s.to_api_dict() for s in students])

    if len(class_) > MAX_CLASS_FILTERS:
        raise HTTPException(status_code=400, detail=f"Too many class filters. Max allowed is {MAX_CLASS_FILTERS}.")

    allowed = {c.strip() for c in class_ if c is not None and c.strip() != ""}
    filtered = [s.to_api_dict() for s in students if s.class_ in allowed]
    return StudentsResponse(students=filtered)


@app.get("/ga0/q10/api", response_model=StudentsResponse)
def get_students_ga0_q10(class_: Optional[List[str]] = Query(default=None, alias="class")) -> StudentsResponse:
    # Strict routed alias for exam-style endpoint naming.
    return get_students(class_=class_)


@app.get("/t22026/ga0/q10/api", response_model=StudentsResponse)
def get_students_t22026_ga0_q10(class_: Optional[List[str]] = Query(default=None, alias="class")) -> StudentsResponse:
    # Fully qualified term+GA+question route for long-term compatibility.
    return get_students(class_=class_)



Q10_UI = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Q10 API</title><style>body{font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(120deg,#fff8ef,#e9f7ff);margin:0}.wrap{max-width:960px;margin:24px auto;padding:20px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}input{width:100%;padding:10px;border:1px solid #cfd8e3;border-radius:10px}button{background:#1d4ed8;color:#fff;border:0;padding:10px 14px;border-radius:10px;cursor:pointer}pre{background:#0b1020;color:#d1e7ff;padding:12px;border-radius:10px;overflow:auto}</style></head><body><div class='wrap'><div class='card'><h2>T22026 GA0 Q10: Student API</h2><p>Routes: <code>/api</code>, <code>/ga0/q10/api</code>, <code>/t22026/ga0/q10/api</code></p><p>Optional class filter (comma-separated):</p><input id='cls' placeholder='1A,1B'><br><br><button onclick='run()'>Fetch</button><pre id='out'>Waiting...</pre></div></div><script>async function run(){const v=document.getElementById('cls').value.trim();let url='/ga0/q10/api';if(v){url+='?'+v.split(',').map(x=>'class='+encodeURIComponent(x.trim())).join('&')}const r=await fetch(url);document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2);}</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def q10_home() -> str:
    return Q10_UI




