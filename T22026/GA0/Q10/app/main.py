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

_csv_env = os.getenv("Q10_CSV_PATH")
if _csv_env:
    DATA_FILE = Path(_csv_env)
else:
    DATA_FILE = Path(__file__).resolve().parent.parent / "q-fastapi.csv"

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
    return get_students(class_=class_)


@app.get("/t22026/ga0/q10/api", response_model=StudentsResponse)
def get_students_t22026_ga0_q10(class_: Optional[List[str]] = Query(default=None, alias="class")) -> StudentsResponse:
    return get_students(class_=class_)


# ── Exam-canonical route ──────────────────────────────────────────────────────
# The exam validator takes the submitted URL and calls GET {url}?class=...
# Students should submit: https://<host>/q10/q-fastapi/api
# The exam then calls:    GET   https://<host>/q10/q-fastapi/api?class=1A&class=1B
@app.get("/q-fastapi/api", response_model=StudentsResponse)
def get_students_exam_canonical(class_: Optional[List[str]] = Query(default=None, alias="class")) -> StudentsResponse:
    return get_students(class_=class_)



Q10_UI = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>Q10 - Student API Dashboard</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --primary-glow: rgba(59, 130, 246, 0.25);
      --bg: #090d16;
      --card-bg: rgba(17, 24, 39, 0.7);
      --border: rgba(255, 255, 255, 0.08);
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at top left, #090d16, #0f172a, #1e1b4b, #090d16);
      color: var(--text);
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .wrap {
      width: 100%;
      max-width: 800px;
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
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
    }
    h2 {
      margin-top: 0;
      font-weight: 700;
      font-size: 1.8rem;
      background: linear-gradient(to right, #38bdf8, #3b82f6);
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
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }
    .routes code {
      color: #38bdf8;
    }
    .submit-container {
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.25);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 28px;
      text-align: center;
    }
    .submit-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #93c5fd;
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
      color: #60a5fa;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      word-break: break-all;
    }
    .btn-copy {
      background: #2563eb;
      color: white;
      border: none;
      padding: 6px 12px;
      border-radius: 8px;
      cursor: pointer;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all 0.2s;
    }
    .btn-copy:hover {
      background: #1d4ed8;
    }
    .form-group {
      margin-bottom: 24px;
    }
    label {
      display: block;
      font-weight: 500;
      margin-bottom: 8px;
      font-size: 0.9rem;
      color: #e2e8f0;
    }
    input[type='text'] {
      width: 100%;
      padding: 14px 16px;
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-size: 0.95rem;
      transition: all 0.3s;
      box-sizing: border-box;
    }
    input[type='text']:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-glow);
    }
    button.btn-solve {
      width: 100%;
      background: linear-gradient(135deg, #3b82f6, #2563eb);
      color: #fff;
      border: 0;
      padding: 14px;
      font-size: 1rem;
      font-weight: 600;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.2);
    }
    button.btn-solve:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(59, 130, 246, 0.35);
    }
    button.btn-solve:active {
      transform: translateY(0);
    }
    .results-area {
      margin-top: 28px;
      display: none;
    }
    .table-container {
      max-height: 280px;
      overflow-y: auto;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: rgba(15, 23, 42, 0.4);
      margin-bottom: 16px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.9rem;
      text-align: left;
    }
    th, td {
      padding: 12px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    th {
      background: rgba(15, 23, 42, 0.8);
      color: var(--text-muted);
      font-weight: 600;
      position: sticky;
      top: 0;
    }
    .badge {
      background: rgba(59, 130, 246, 0.15);
      color: #60a5fa;
      padding: 2px 8px;
      border-radius: 6px;
      font-weight: 600;
      font-size: 0.8rem;
      border: 1px solid rgba(59, 130, 246, 0.3);
    }
    pre {
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      overflow: auto;
      font-family: monospace;
      font-size: 0.85rem;
      max-height: 200px;
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
      <h2>T22026 GA0 Q10: Student API Service</h2>
      <p>FastAPI microservice loaded with 2,000 student records. Provides instant dynamic filtering by class.</p>
      
      <div class='routes'>
        <span>Exam Canonical: <code>/q-fastapi/api</code></span>
        <span>Also: <code>/q10/api</code></span>
      </div>

      <div class='submit-container'>
        <div class='submit-title'>Submit this endpoint URL on the exam page</div>
        <div class='submit-url-box'>
          <span id='sub-url'></span>
          <button class='btn-copy' onclick='copyEndpoint()'>Copy URL</button>
        </div>
        <p style="margin: 8px 0 0; font-size: 0.85rem; color: #10b981; font-weight: 600;">✅ SUBMIT THIS URL FOR Q10</p>
      </div>

      <div class='form-group'>
        <label for='cls'>Interactive Sandbox: Class Filters (comma-separated)</label>
        <input id='cls' type='text' placeholder='e.g., 1A, 2B, 12Z' value='1A, 2C'>
      </div>

      <button class='btn-solve' onclick='run()'>Query Student Database</button>

      <div id='res-area' class='results-area'>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h3 style="margin: 0; font-size: 1.1rem;">Found <span id='count' style="color:#60a5fa;">0</span> Students</h3>
          <span class="badge" style="cursor: pointer;" onclick="toggleRaw()">Show Raw JSON</span>
        </div>
        
        <div id='table-container' class='table-container'>
          <table>
            <thead>
              <tr>
                <th>Student ID</th>
                <th>Class</th>
              </tr>
            </thead>
            <tbody id='res-body'></tbody>
          </table>
        </div>

        <pre id='raw-json' style='display: none;'></pre>
      </div>
    </div>
  </div>

  <div id="toast" class="toast">Copied to clipboard!</div>

  <script>
    // Exam validator calls GET {url}?class=... directly on the submitted URL.
    const prefix = window.location.origin;
    document.getElementById('sub-url').textContent = prefix + '/q-fastapi/api';

    function copyEndpoint() {
      const url = document.getElementById('sub-url').textContent;
      navigator.clipboard.writeText(url);
      showToast();
    }

    function showToast() {
      const t = document.getElementById('toast');
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2000);
    }

    let isRawVisible = false;
    function toggleRaw() {
      const table = document.getElementById('table-container');
      const raw = document.getElementById('raw-json');
      isRawVisible = !isRawVisible;
      table.style.display = isRawVisible ? 'none' : 'block';
      raw.style.display = isRawVisible ? 'block' : 'none';
    }

    async function run() {
      const v = document.getElementById('cls').value;
      const path = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';
      let url = window.location.origin + path + 'api';
      if (v) {
        url += '?' + v.split(',').map(x => 'class=' + encodeURIComponent(x.trim())).join('&');
      }
      try {
        const r = await fetch(url);
        if (!r.ok) throw new Error('API returned status ' + r.status);
        const data = await r.json();
        
        document.getElementById('raw-json').textContent = JSON.stringify(data, null, 2);
        
        const tbody = document.getElementById('res-body');
        tbody.innerHTML = '';
        const students = data.students || [];
        document.getElementById('count').textContent = students.length;
        
        students.slice(0, 100).forEach(s => {
          const row = document.createElement('tr');
          row.innerHTML = `<td>${s.studentId}</td><td><span class="badge">${s.class}</span></td>`;
          tbody.appendChild(row);
        });
        
        if (students.length > 100) {
          const row = document.createElement('tr');
          row.innerHTML = `<td colspan="2" style="text-align:center;color:var(--text-muted);">... and ${students.length - 100} more ...</td>`;
          tbody.appendChild(row);
        }
        
        document.getElementById('res-area').style.display = 'block';
      } catch (err) {
        alert('Query failed: ' + err.message);
      }
    }
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def q10_home() -> str:
    return Q10_UI





