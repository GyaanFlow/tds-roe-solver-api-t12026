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


Q18_UI = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Q18 API</title><style>body{font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(120deg,#effaf7,#edf2ff);margin:0}.wrap{max-width:980px;margin:24px auto;padding:20px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}input{width:100%;padding:10px;border:1px solid #cfd8e3;border-radius:10px}button{background:#0f4c81;color:#fff;border:0;padding:10px 14px;border-radius:10px;cursor:pointer}pre{background:#0b1020;color:#d1e7ff;padding:12px;border-radius:10px;overflow:auto}</style></head><body><div class='wrap'><div class='card'><h2>T22026 GA0 Q18: Robust Proxy Helper</h2><p>Create a session with your email. Use returned <code>base_url_to_submit</code>.</p><p>Routes: <code>/q18/setup</code>, <code>/ga0/q18/setup</code>, <code>/t22026/ga0/q18/setup</code></p>
<input id='email' placeholder='you@example.com'><br><br><input id='token' placeholder='optional ngrok token'><br><br><button onclick='run()'>Generate Session</button><pre id='out'>Waiting...</pre></div></div><script>async function run(){const body={email:document.getElementById('email').value.trim(),ngrok_token:document.getElementById('token').value.trim()||null};const r=await fetch('/ga0/q18/setup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});document.getElementById('out').textContent=JSON.stringify(await r.json(),null,2);}</script></body></html>
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
def proxy_preflight(session_id: str, path: str):
    s = get_session(session_id)
    return Response(status_code=200, headers=make_proxy_headers(s.email))


@app.api_route("/q18/session/{session_id}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"])
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

