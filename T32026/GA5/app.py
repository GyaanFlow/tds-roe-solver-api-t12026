from __future__ import annotations

import time

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from T32026.GA5.dashboard import DASHBOARD_HTML
from T32026.GA5.main import router

app = FastAPI(title="T3-2026 GA5 API Hub", version="1.0.0")


class _Recorder:
    """Pure-ASGI tee of the two graded POST routes into T22026/GA5/capture.py (private, redacted,
    bounded, temp dir only). Read it with GET /t3ga5/{email}/debug/captures?key=<owner key>. Turn off with T3GA5_CAPTURE=0."""

    def __init__(self, app):  # Starlette passes the wrapped app as app=...
        self.inner = app

    async def __call__(self, scope, receive, send):
        import os
        path = scope.get("path", "")
        if scope.get("type") != "http" or os.environ.get("T3GA5_CAPTURE", "1") == "0" or not (path.rstrip("/").endswith(("/query", "/harness"))):
            return await self.inner(scope, receive, send)
        from T22026.GA5 import capture
        started = time.time()
        req_chunks, resp_chunks, status = [], [], {"v": 0}

        async def _receive():
            message = await receive()
            if message.get("type") == "http.request":
                req_chunks.append(message.get("body", b""))
            return message

        async def _send(message):
            if message.get("type") == "http.response.start":
                status["v"] = message.get("status", 0)
            elif message.get("type") == "http.response.body":
                resp_chunks.append(message.get("body", b""))
            await send(message)

        try:
            await self.inner(scope, _receive, _send)
        finally:
            headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers") or []}
            capture.record(str(scope.get("tenant_email") or "").strip().lower(), "t3ga5", scope.get("method", ""), path, headers,
                           b"".join(req_chunks), status["v"], b"".join(resp_chunks), time.time() - started)


app.add_middleware(_Recorder)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home():
    return HTMLResponse(DASHBOARD_HTML)


@app.options("/{path:path}", include_in_schema=False)
async def preflight(path: str):
    return Response(status_code=204)
