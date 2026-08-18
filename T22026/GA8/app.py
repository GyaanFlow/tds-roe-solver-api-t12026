from __future__ import annotations

"""
T22026/GA8/app.py — Sub-app entry point for Graded Assignment 8.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from T22026.GA8.dashboard import router as dashboard_router
from T22026.GA8.main import router as api_router

app = FastAPI(title="T22026 GA8 MLOps & LLM Systems Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)
app.include_router(api_router)
