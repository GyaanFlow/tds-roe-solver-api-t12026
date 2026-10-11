from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from T32026.GA1.dashboard import DASHBOARD_HTML
from T32026.GA1.main import router

app = FastAPI(title="T3-2026 GA1 API Hub", version="1.0.0")
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
