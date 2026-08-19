from __future__ import annotations

"""
T22026/GA8/main.py — GA8 FastAPI Router.

Provides robust, multi-tenant dual-route support (both bare and tenant-prefixed routes)
for all 7 live policy endpoints and interactive /solve endpoints for Q8, Q9, Q10.
"""

import logging
from typing import Any, Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from T22026.GA8.solvers import (
    build_corpus_decision,
    bqml_decision,
    promote_decision,
    adapt_decision,
    quantize_decision,
    pipeline_decision,
    verify_bundle_decision,
    solve_q8_lora,
    solve_q9_mlflow,
    solve_q10_carbon,
)

logger = logging.getLogger("ga8_router")
router = APIRouter()


async def _read_json_body(request: Request) -> Any:
    try:
        return await request.json()
    except Exception:
        return None


def _get_email(email: Optional[str], request: Request) -> str:
    if email:
        return email.strip().lower()
    t = getattr(request.state, "tenant_email", None) or request.scope.get("tenant_email")
    if t:
        return str(t).strip().lower()
    return "student@example.com"


# ---------------------------------------------------------------------------
# Q1: POST /build-corpus
# ---------------------------------------------------------------------------
@router.post("/build-corpus")
@router.post("/{email}/build-corpus")
async def build_corpus_endpoint(request: Request, email: Optional[str] = None):
    try:
        body = await _read_json_body(request)
        status_code, resp = build_corpus_decision(body)
        return JSONResponse(status_code=status_code, content=resp)
    except Exception as exc:
        logger.warning("Error in /build-corpus: %s", exc)
        return JSONResponse(status_code=400, content={"error": "INVALID_INPUT"})


# ---------------------------------------------------------------------------
# Q2: POST /bqml
# ---------------------------------------------------------------------------
@router.post("/bqml")
@router.post("/{email}/bqml")
async def bqml_endpoint(request: Request, email: Optional[str] = None):
    try:
        e = _get_email(email, request)
        body = await _read_json_body(request)
        status_code, resp = bqml_decision(body, tenant=e)
        return JSONResponse(status_code=status_code, content=resp)
    except Exception as exc:
        logger.warning("Error in /bqml: %s", exc)
        return JSONResponse(status_code=400, content={"error": "INVALID_INPUT"})


# ---------------------------------------------------------------------------
# Q3: POST /promote
# ---------------------------------------------------------------------------
@router.post("/promote")
@router.post("/{email}/promote")
async def promote_endpoint(request: Request, email: Optional[str] = None):
    try:
        body = await _read_json_body(request)
        status_code, resp = promote_decision(body)
        return JSONResponse(status_code=status_code, content=resp)
    except Exception as exc:
        logger.warning("Error in /promote: %s", exc)
        return JSONResponse(status_code=400, content={"error": "INVALID_INPUT"})


# ---------------------------------------------------------------------------
# Q4: POST /adapt
# ---------------------------------------------------------------------------
@router.post("/adapt")
@router.post("/{email}/adapt")
async def adapt_endpoint(request: Request, email: Optional[str] = None):
    try:
        body = await _read_json_body(request)
        status_code, resp = adapt_decision(body)
        return JSONResponse(status_code=status_code, content=resp)
    except Exception as exc:
        logger.warning("Error in /adapt: %s", exc)
        return JSONResponse(status_code=400, content={"error": "INVALID_INPUT"})


# ---------------------------------------------------------------------------
# Q5: POST /quantize
# ---------------------------------------------------------------------------
@router.post("/quantize")
@router.post("/{email}/quantize")
async def quantize_endpoint(request: Request, email: Optional[str] = None):
    try:
        e = _get_email(email, request)
        body = await _read_json_body(request)
        status_code, resp = quantize_decision(body, tenant=e)
        return JSONResponse(status_code=status_code, content=resp)
    except Exception as exc:
        logger.warning("Error in /quantize: %s", exc)
        return JSONResponse(status_code=400, content={"error": "INVALID_INPUT"})


# ---------------------------------------------------------------------------
# Q6: POST /pipeline
# ---------------------------------------------------------------------------
@router.post("/pipeline")
@router.post("/{email}/pipeline")
async def pipeline_endpoint(request: Request, email: Optional[str] = None):
    try:
        e = _get_email(email, request)
        body = await _read_json_body(request)
        status_code, resp = pipeline_decision(body, tenant=e)
        return JSONResponse(status_code=status_code, content=resp)
    except Exception as exc:
        logger.warning("Error in /pipeline: %s", exc)
        return JSONResponse(status_code=409, content={"error": "INVALID_REQUEST"})


# ---------------------------------------------------------------------------
# Q7: POST /verify-bundle
# ---------------------------------------------------------------------------
@router.post("/verify-bundle")
@router.post("/{email}/verify-bundle")
async def verify_bundle_endpoint(request: Request, email: Optional[str] = None):
    try:
        body = await _read_json_body(request)
        status_code, resp = verify_bundle_decision(body)
        return JSONResponse(status_code=status_code, content=resp)
    except Exception as exc:
        logger.warning("Error in /verify-bundle: %s", exc)
        return JSONResponse(status_code=400, content={"error": "INVALID_INPUT"})


# ---------------------------------------------------------------------------
# Interactive Solvers (Q8, Q9, Q10)
# ---------------------------------------------------------------------------
@router.get("/solve/q8")
@router.get("/{email}/solve/q8")
async def solve_q8_endpoint(request: Request, email: Optional[str] = None):
    e = _get_email(email, request)
    return solve_q8_lora(e)


@router.get("/solve/q9")
@router.get("/{email}/solve/q9")
async def solve_q9_endpoint(request: Request, email: Optional[str] = None, version: str = ""):
    e = _get_email(email, request)
    return solve_q9_mlflow(e, version=version)


@router.get("/solve/q10")
@router.get("/{email}/solve/q10")
async def solve_q10_endpoint(request: Request, email: Optional[str] = None, version: str = ""):
    e = _get_email(email, request)
    return solve_q10_carbon(e, version=version)


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@router.get("/health")
async def health():
    return {"status": "ok", "service": "ga8"}
