from __future__ import annotations

"""
T22026/GA6/app.py — Unified GA6 sub-application.
Mounted at /ga6 by the root hf_space/app.py.
"""

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse

from T22026.GA6.main import router as ga6_router

_CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Expose-Headers": "Retry-After, X-Request-ID",
}

app = FastAPI(
    title="IITM TDS 2026-05 GA6 — Web Scraping API Hub",
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
async def ga6_preflight(full_path: str) -> Response:
    return Response(status_code=200, headers=_CORS_HEADERS)


app.include_router(ga6_router)


_HOME_HTML = """<!doctype html>
<html><head><meta charset="utf-8"><title>GA6 — Web Scraping API Hub</title></head>
<body style="font-family: system-ui, sans-serif; max-width: 720px; margin: 40px auto; line-height: 1.5;">
<h2>GA6 &mdash; Web Scraping API Hub</h2>
<p>Only Q7 (Scrape Books to Scrape by Category and Value) is served here. The
other GA6 questions (Q1 rotated-image forensics, Q3 DuckDB regression, Q8
GitHub Action + Playwright, Q10 modem audio decode) genuinely need your own
live exam session, browser tab, or personal infrastructure &mdash; no hosted
API can produce or verify them.</p>
<h3>Q7 endpoint</h3>
<p><code>GET /ga6/{your-email}/scrape-books</code></p>
<p>Returns your seeded assignment (categories, thresholds) and the SHA-256
digest to paste into the exam. This does a live scrape of
<a href="https://books.toscrape.com/">books.toscrape.com</a> on every call --
it is not cached, so it always reflects the site's current state.</p>
</body></html>"""


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def ga6_home():
    return HTMLResponse(_HOME_HTML)
