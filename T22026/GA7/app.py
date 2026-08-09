from __future__ import annotations

"""
T22026/GA7/app.py — Unified GA7 sub-application.
Mounted at /ga7 by the root hf_space/app.py.
"""

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

from T22026.GA7.main import router as ga7_router

_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Expose-Headers": "Retry-After, X-Request-ID",
}

app = FastAPI(
    title="IITM TDS 2026-05 GA7 — DevSecOps/AppSec/OSINT Policy Hub",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.middleware("http")
async def _cors_headers(request, call_next):
    response = await call_next(request)
    for key, value in _CORS_HEADERS.items():
        response.headers[key] = value
    return response


@app.options("/{full_path:path}", include_in_schema=False)
async def ga7_preflight(full_path: str) -> Response:
    return Response(status_code=200, headers=_CORS_HEADERS)


app.include_router(ga7_router)


_HOME_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>GA7 — DevSecOps/AppSec/OSINT Policy Hub</title></head>
<body style="font-family: system-ui, sans-serif; max-width: 760px; margin: 40px auto; line-height: 1.5;">
<h2>GA7 &mdash; DevSecOps/AppSec/OSINT Policy Hub</h2>
<p>Five deterministic policy endpoints, one per student email. The other five
GA7 questions (street-view geolocation, google-dorks, cloudflare-waf-bypass,
media-forensics, actions-workflow-audit) are answered directly in the exam
page from data the exam bundle generates client-side &mdash; there is nothing
for a server to host for those.</p>
<h3>Endpoints (replace {email} with your exam email)</h3>
<ul>
<li><code>POST /ga7/{email}/release-gate</code></li>
<li><code>POST /ga7/{email}/action-firewall</code></li>
<li><code>POST /ga7/{email}/terraform/plan</code></li>
<li><code>POST /ga7/{email}/sanitize-output</code></li>
<li><code>POST /ga7/{email}/corroborate</code></li>
<li><code>GET /ga7/{email}/scope</code> &mdash; your seeded tenant/workspace/host assignment, for debugging</li>
</ul>
<p>All five are pure rule engines &mdash; no LLM call, no AIPipe token needed.</p>
</body></html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def ga7_home():
    return HTMLResponse(_HOME_HTML)
