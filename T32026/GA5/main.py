from __future__ import annotations

import hmac
import json
import os
import re
import time
from pathlib import Path
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse

from T32026.GA5 import harness, rag
from T32026.GA5.kb import ollama_dataset, rag_knowledge_base

router = APIRouter()
MAX_BODY = 8 * 1024 * 1024  # a harness batch carries the full policy plus 24 cases
EMAIL_RE = re.compile(r"[^\s@/]+@[^\s@/]+\.[^\s@/]+")


def _email(request: Request, email: str | None = None) -> str:
    return str(email or request.scope.get("tenant_email") or request.query_params.get("email") or "").strip().lower()


def _bad_email(email: str) -> JSONResponse | None:
    if not email or len(email) > 254 or not EMAIL_RE.fullmatch(email):
        return JSONResponse(status_code=400, content={"error": "VALID_EMAIL_REQUIRED"})
    return None


async def _json_body(request: Request, limit: int = MAX_BODY) -> tuple[Any | None, JSONResponse | None]:
    declared = request.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > limit:
        return None, JSONResponse(status_code=413, content={"error": "REQUEST_TOO_LARGE"})
    chunks, size = [], 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > limit:
            return None, JSONResponse(status_code=413, content={"error": "REQUEST_TOO_LARGE"})
        chunks.append(chunk)
    try:
        return json.loads(b"".join(chunks) or b"null"), None
    except Exception:
        return None, JSONResponse(status_code=400, content={"error": "INVALID_JSON"})


@router.get("/health")
async def health():
    return {"status": "ok", "service": "t3ga5"}


# ------------------------------------------------------------------ Q1 RAG Colosseum
@router.post("/{email}/query")
@router.post("/{email}/query/", include_in_schema=False)
@router.post("/query")
@router.post("/query/", include_in_schema=False)
async def rag_query(request: Request, email: str | None = None):
    student = _email(request, email)
    bad = _bad_email(student)
    if bad:
        return bad
    body, error = await _json_body(request, 64 * 1024)
    if error:
        return error
    if not isinstance(body, dict) or not isinstance(body.get("question"), str):
        return JSONResponse(status_code=400, content={"error": "QUESTION_STRING_REQUIRED"})
    question = body["question"][:4000]
    try:
        top_k = int(body.get("top_k", 3))
    except (TypeError, ValueError):
        top_k = 3
    result = rag.answer_question(rag.knowledge_base(student), question, top_k)
    return JSONResponse(content=result, headers={"Cache-Control": "no-store"})


@router.get("/{email}/kb")
@router.get("/kb")
async def knowledge_base(request: Request, email: str | None = None):
    student = _email(request, email)
    bad = _bad_email(student)
    if bad:
        return bad
    kb = rag_knowledge_base(student)
    return {"email": student, "count": len(kb["passages"]), "passages": kb["passages"]}


# ------------------------------------------------------------------ Q4 harness safety router
@router.post("/{email}/harness")
@router.post("/{email}/harness/", include_in_schema=False)
@router.post("/harness")
@router.post("/harness/", include_in_schema=False)
async def harness_route(request: Request, email: str | None = None):
    body, error = await _json_body(request)
    if error:
        return error
    if not isinstance(body, dict):
        return JSONResponse(status_code=400, content={"error": "JSON_OBJECT_REQUIRED"})
    try:
        result = harness.decide_batch(body)
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"error": "INVALID_BATCH", "detail": str(exc)})
    return JSONResponse(content=result, headers={"Cache-Control": "no-store"})


# ------------------------------------------------------------------ Q2 Ollama / FAISS / rank correlation
@router.get("/{email}/answers/ollama-dataset")
@router.get("/answers/ollama-dataset")
async def ollama_dataset_route(request: Request, email: str | None = None, version: str = ""):
    student = _email(request, email)
    bad = _bad_email(student)
    if bad:
        return bad
    data = ollama_dataset(student, version)
    return {"sentences": data["sentences"], "queries": data["queries"]}


@router.get("/{email}/answers/ollama-script")
@router.get("/answers/ollama-script")
async def ollama_script_route(request: Request, email: str | None = None):
    student = _email(request, email)
    bad = _bad_email(student)
    if bad:
        return bad
    script = (Path(__file__).with_name("ollama_matrix.py")).read_text(encoding="utf-8")
    return PlainTextResponse(script, headers={"Content-Disposition": 'attachment; filename="ollama_matrix.py"'})


# ------------------------------------------------------------------ owner-only recorder view
@router.get("/{email}/debug/captures")
@router.get("/debug/captures")
async def debug_captures(request: Request, email: str | None = None, key: str = Query(""), contains: str = "", limit: int = 40, offset: int = 0, clear: int = 0):
    expected = os.environ.get("T3GA5_DEBUG_KEY", "")
    if not expected or not hmac.compare_digest(key.encode(), expected.encode()):
        return JSONResponse(status_code=404, content={"error": "not found"})
    from T22026.GA5 import capture
    student = _email(request, email)
    if clear:
        capture.clear(student, "t3ga5")
        return {"cleared": True}
    rows = capture.read(student, "t3ga5", contains=contains, limit=limit, offset=offset)
    return JSONResponse(content={"count": len(rows), "entries": rows}, headers={"Cache-Control": "no-store"})
