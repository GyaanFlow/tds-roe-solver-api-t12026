from __future__ import annotations

"""
T22026/GA7/main.py — GA7 router.

Five questions, all pure deterministic rule engines -- no LLM, no AIPipe
budget, no fallback path. See solvers.py's module docstring for which GA7
questions are (and are not) served here and why.
"""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from T22026.GA7.solvers import (
    action_firewall_decision,
    action_firewall_scope,
    corroborate_decision,
    release_gate_decision,
    sanitize_output_decision,
    sanitizer_scope,
    terraform_plan_decision,
    terraform_scope,
)

logger = logging.getLogger("ga7_router")
router = APIRouter()


async def _read_json_body(request: Request):
    try:
        return await request.json()
    except Exception:
        return None


def _get_email(email: str | None, request: Request) -> str:
    if email:
        return email
    return getattr(request.state, "tenant_email", None) or request.scope.get("tenant_email") or "23f1000805@ds.study.iitm.ac.in"


@router.post("/release-gate")
@router.post("/{email}/release-gate")
async def release_gate_endpoint(request: Request, email: str | None = None):
    e = _get_email(email, request)
    body = await _read_json_body(request)
    try:
        return release_gate_decision(body if isinstance(body, dict) else {})
    except Exception:
        logger.exception("GA7 release-gate failed for %s", e)
        return JSONResponse(status_code=200, content={"decision": "block", "violations": ["EXCESS_PERMISSION"]})


@router.post("/action-firewall")
@router.post("/{email}/action-firewall")
async def action_firewall_endpoint(request: Request, email: str | None = None):
    e = _get_email(email, request)
    body = await _read_json_body(request)
    try:
        scope = action_firewall_scope(e)
        return action_firewall_decision(body, scope)
    except Exception:
        logger.exception("GA7 action-firewall failed for %s", e)
        return JSONResponse(status_code=200, content={"decision": "block", "reason": "INVALID_SCHEMA"})


@router.post("/terraform/plan")
@router.post("/{email}/terraform/plan")
async def terraform_plan_endpoint(request: Request, email: str | None = None):
    e = _get_email(email, request)
    body = await _read_json_body(request)
    try:
        scope = terraform_scope(e)
        return terraform_plan_decision(body, scope)
    except Exception:
        logger.exception("GA7 terraform/plan failed for %s", e)
        return JSONResponse(status_code=200, content={"decision": "reject", "reason": "INVALID_PLAN"})


@router.post("/sanitize-output")
@router.post("/{email}/sanitize-output")
async def sanitize_output_endpoint(request: Request, email: str | None = None):
    e = _get_email(email, request)
    body = await _read_json_body(request)
    try:
        scope = sanitizer_scope(e)
        return sanitize_output_decision(body, scope["allowedHosts"])
    except Exception:
        logger.exception("GA7 sanitize-output failed for %s", e)
        return JSONResponse(status_code=200, content={"safe": False, "reason": "INVALID_SCHEMA"})


@router.post("/corroborate")
@router.post("/{email}/corroborate")
async def corroborate_endpoint(request: Request, email: str | None = None):
    e = _get_email(email, request)
    body = await _read_json_body(request)
    try:
        return corroborate_decision(body)
    except Exception:
        logger.exception("GA7 corroborate failed for %s", e)
        return JSONResponse(status_code=200,
                             content={"verdict": "invalid", "confidence": "low", "corroboratingSources": []})


# Convenience: GET endpoints returning each student's assigned seeded scope,
# so a consuming solver (or a curious student) can inspect what the hub will
# enforce for their email without guessing.
@router.get("/{email}/scope")
async def scope_endpoint(email: str):
    return {
        "actionFirewall": action_firewall_scope(email),
        "terraform": terraform_scope(email),
        "sanitizer": sanitizer_scope(email),
    }
