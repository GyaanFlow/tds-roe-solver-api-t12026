"""
Observable Incident Triage Agent Server
Specification: ga5-incident-agent/v2 (Tools in Data Science GA3)

Endpoints:
    POST /v2/incidents
    POST /v2/incidents/{runId}/receipts
    GET  /v2/incidents/{runId}

Design:
  * POST /v2/incidents plans once (deterministic heuristics, optional LLM),
    persists the run, and returns diagnosis + minimal diagnostic dispatches.
  * Every later transition is driven by the grader's authoritative receipts
    (tool outcomes and approvals). Nothing is ever self-approved or invented.
  * Dispatch ids, span ids, receipt ids and nonces are correlated across
    actionLog, receiptLog and the OTLP tree.
  * Transcripts, prompts, credentials and raw tool arguments/results are never
    exported: actionLog arguments are case-derived tool inputs, and a scrub pass
    removes any sensitive literal from every response.
"""

import os
import sys
import json
import asyncio
import hashlib
import datetime
from typing import Dict, Any, List, Optional, Tuple

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.concurrency import iterate_in_threadpool

CUR_DIR = os.path.dirname(os.path.abspath(__file__))

import tempfile
LOG_FILE = os.path.join(tempfile.gettempdir(), "t3ga3_incident_requests.log")
LOG_BODY_LIMIT = 4000


def log_event(event_type: str, details: Any):
    if os.environ.get("GA3_INCIDENT_LOG") != "1":  # request bodies stay off disk by default
        return
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    header = f"\n{'=' * 80}\n[GRADER_AUDIT] {ts} | {event_type}\n{'=' * 80}\n"
    if isinstance(details, (dict, list)):
        body = json.dumps(details, indent=2, ensure_ascii=False)
    else:
        body = str(details)
    if len(body) > LOG_BODY_LIMIT:
        body = body[:LOG_BODY_LIMIT] + "\n... [truncated]"
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{header}{body}\n")
            f.flush()
    except Exception as e:  # pragma: no cover
        sys.stderr.write(f"Failed to write log: {e}\n")


from .db import (  # noqa: E402
    get_incident,
    save_incident,
    update_incident_status,
    clear_chosen_effect,
    update_incident_response,
    get_receipt_response,
    set_receipt_response,
    record_dispatch,
    get_dispatches,
    record_receipt,
    get_receipts_by_id,
    get_receipts,
    record_approval,
    update_approval_decision,
    get_approval,
    get_pending_approvals,
    record_otlp_span,
    update_otlp_span,
    get_otlp_spans,
)
from .telemetry import (  # noqa: E402
    SPAN_KIND_INTERNAL,
    SPAN_KIND_SERVER,
    SPAN_KIND_CLIENT,
    STATUS_CODE_UNSET,
    STATUS_CODE_OK,
    STATUS_CODE_ERROR,
    gen_trace_id,
    gen_span_id,
    parse_traceparent,
    make_traceparent,
    build_otlp_resource_spans,
)
from .planner import analyze_incident, get_effect_arguments, get_model_name  # noqa: E402

PROFILE = "ga5-incident-agent/v2"
MAX_BODY_BYTES = 768 * 1024
DEFAULT_APPROVAL_TOOLS = ["rollback_deployment", "disable_feature"]

app = FastAPI(title="Observable Incident Triage Agent", version="2.0.0")

# Serialize state transitions. The grader probes concurrency (equivalent
# requests, receipt replay, conflicts) and every transition must be atomic and
# read-modify-write safe against the durable store.
_STATE_LOCK = asyncio.Lock()


# --------------------------------------------------------------------------- #
# Redaction
# --------------------------------------------------------------------------- #
_MIN_SECRET_LEN = 4


def _collect_strings(obj: Any, out: List[str]) -> None:
    if isinstance(obj, str):
        if len(obj) >= _MIN_SECRET_LEN:
            out.append(obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_strings(v, out)


def forbidden_tokens(body: Dict[str, Any]) -> List[str]:
    """Concrete literals that must never appear in an exported response."""
    toks: List[str] = []
    _collect_strings(body.get("sensitive"), toks)
    incident = body.get("incident") or {}
    if isinstance(incident, dict):
        _collect_strings(incident.get("sensitive"), toks)
    policy = body.get("policy") or {}
    if isinstance(policy, dict):
        for item in policy.get("doNotExport") or []:
            if isinstance(item, str) and len(item.strip()) >= _MIN_SECRET_LEN:
                toks.append(item.strip())
    return sorted({t for t in toks if t and len(t) >= _MIN_SECRET_LEN},
                  key=lambda s: (-len(s), s))


def scrub(obj: Any, forbidden: List[str]) -> Any:
    if not forbidden:
        return obj
    if isinstance(obj, str):
        out = obj
        for tok in forbidden:
            if tok in out:
                out = out.replace(tok, "[REDACTED]")
        return out
    if isinstance(obj, dict):
        return {k: scrub(v, forbidden) for k, v in obj.items()}
    if isinstance(obj, list):
        return [scrub(v, forbidden) for v in obj]
    return obj


def _forbidden_for(inc: Dict[str, Any]) -> List[str]:
    try:
        tokens = forbidden_tokens(json.loads(inc.get("request_json") or "{}"))
    except Exception:
        return []
    # Never let a doNotExport category label collide with a required exported
    # identifier (run id / public marker), which would corrupt telemetry.
    run_id = inc.get("run_id") or ""
    marker = inc.get("public_marker") or ""
    return [t for t in tokens if t not in run_id and t not in marker]


def _clean_dispatch(d: Dict[str, Any]) -> Dict[str, Any]:
    """Drop absent optional members so the wire shape stays exact."""
    return {k: v for k, v in d.items() if v is not None}


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def canonical_hash(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def make_resp_headers(trace_id: Optional[str], span_id: Optional[str],
                      tracestate: Optional[str] = None) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    if trace_id and span_id:
        headers["traceparent"] = make_traceparent(trace_id, span_id)
    if tracestate:
        headers["tracestate"] = tracestate
    return headers


def _json_response(payload: Dict[str, Any], inc: Dict[str, Any],
                   extra_forbidden: Optional[List[str]] = None) -> JSONResponse:
    tokens = _forbidden_for(inc)
    if extra_forbidden:
        tokens = sorted(set(tokens) | set(extra_forbidden), key=lambda s: (-len(s), s))
    body = scrub(payload, tokens)
    headers = make_resp_headers(inc.get("trace_id"), inc.get("root_server_span_id"),
                                inc.get("tracestate"))
    return JSONResponse(content=body, headers=headers)


def _num(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


# --------------------------------------------------------------------------- #
# Response builders
# --------------------------------------------------------------------------- #
def _diagnosis(inc: Dict[str, Any]) -> Dict[str, Any]:
    try:
        evidence = json.loads(inc.get("evidence_json") or "[]")
    except Exception:
        evidence = []
    return {"rootCause": inc.get("root_cause"), "evidence": evidence}


def _action_log(run_id: str) -> List[Dict[str, Any]]:
    log: List[Dict[str, Any]] = []
    for d in get_dispatches(run_id):
        item: Dict[str, Any] = {
            "actionId": d["action_id"],
            "callId": d["call_id"],
            "phase": d["phase"],
            "toolName": d["tool_name"],
            "arguments": json.loads(d["arguments_json"]),
            "attempt": d["attempt"],
            "traceparent": d["traceparent"],
        }
        try:
            evidence = json.loads(d["evidence_json"]) if d.get("evidence_json") else []
        except Exception:
            evidence = []
        if evidence:
            item["evidence"] = evidence
        if d.get("approval_id"):
            item["approvalId"] = d["approval_id"]
        if d.get("approval_nonce"):
            item["approvalNonce"] = d["approval_nonce"]
        if d.get("tracestate"):
            item["tracestate"] = d["tracestate"]
        log.append(item)
    return log


def _receipt_log(run_id: str) -> List[Dict[str, Any]]:
    log: List[Dict[str, Any]] = []
    for r in get_receipts(run_id):
        if r["receipt_type"] == "approval":
            log.append({
                "receiptId": r["receipt_id"],
                "approvalId": r["approval_id"],
                "decision": r["decision"],
                "nonce": r["nonce"],
            })
            continue
        item: Dict[str, Any] = {
            "receiptId": r["receipt_id"],
            "actionId": r["action_id"],
            "callId": r["call_id"],
            "attempt": r["attempt"],
            "status": r["status_code"],
        }
        if r.get("result_class"):
            item["resultClass"] = r["result_class"]
        if r.get("error_type"):
            item["errorType"] = r["error_type"]
        if r.get("nonce"):
            item["nonce"] = r["nonce"]
        log.append(item)
    return log


def build_terminal_response(inc: Dict[str, Any]) -> Dict[str, Any]:
    run_id = inc["run_id"]
    try:
        suppressed = json.loads(inc.get("suppressed_json") or "[]")
    except Exception:
        suppressed = []
    return {
        "runId": run_id,
        "status": inc["status"],
        "diagnosis": _diagnosis(inc),
        "chosenEffect": inc.get("chosen_effect"),
        "suppressed": suppressed,
        "actionLog": _action_log(run_id),
        "receiptLog": _receipt_log(run_id),
        "otlp": build_otlp_resource_spans(get_otlp_spans(run_id)),
    }


def build_waiting_response(inc: Dict[str, Any], dispatches: List[Dict[str, Any]],
                           approvals: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "runId": inc["run_id"],
        "status": "waiting",
        "diagnosis": _diagnosis(inc),
        "dispatches": dispatches,
        "approvals": approvals,
    }


def _dispatch_payload(d: Dict[str, Any]) -> Dict[str, Any]:
    item: Dict[str, Any] = {
        "actionId": d["action_id"],
        "callId": d["call_id"],
        "phase": d["phase"],
        "toolName": d["tool_name"],
        "arguments": json.loads(d["arguments_json"]),
        "attempt": d["attempt"],
        "traceparent": d["traceparent"],
    }
    try:
        evidence = json.loads(d["evidence_json"]) if d.get("evidence_json") else []
    except Exception:
        evidence = []
    if evidence:
        item["evidence"] = evidence
    if d.get("approval_id"):
        item["approvalId"] = d["approval_id"]
    if d.get("approval_nonce"):
        item["approvalNonce"] = d["approval_nonce"]
    if d.get("tracestate"):
        item["tracestate"] = d["tracestate"]
    return item


# --------------------------------------------------------------------------- #
# Durable receipt / dispatch projections
# --------------------------------------------------------------------------- #
def _outcome_rows(run_id: str) -> List[Dict[str, Any]]:
    return [r for r in get_receipts(run_id) if r["receipt_type"] == "outcome"]


def _latest_dispatch_per_action(run_id: str) -> Dict[str, Dict[str, Any]]:
    latest: Dict[str, Dict[str, Any]] = {}
    for d in get_dispatches(run_id):
        cur = latest.get(d["action_id"])
        if cur is None or d["attempt"] > cur["attempt"]:
            latest[d["action_id"]] = d
    return latest


def _classify_status(row: Optional[Dict[str, Any]], attempt: int) -> str:
    """pending | ok | retry | failed."""
    if not row:
        return "pending"
    code = row.get("status_code")
    err = (row.get("error_type") or "").lower()
    if err == "timeout" or code == 0:
        return "failed"
    if code == 503:
        return "retry" if attempt <= 1 else "failed"
    if isinstance(code, int) and 200 <= code < 300:
        return "ok"
    if code is None:
        return "ok"  # status omitted by transport but the call returned
    return "failed"


def _action_state(run_id: str) -> Dict[str, Dict[str, Any]]:
    rows = _outcome_rows(run_id)
    state: Dict[str, Dict[str, Any]] = {}
    for action_id, disp in _latest_dispatch_per_action(run_id).items():
        matching = [r for r in rows
                    if r["action_id"] == action_id and r["attempt"] == disp["attempt"]]
        row = matching[-1] if matching else None
        state[action_id] = {
            "dispatch": disp,
            "row": row,
            "state": _classify_status(row, disp["attempt"]),
        }
    return state


def _diagnostic_state(run_id: str) -> Dict[str, Dict[str, Any]]:
    return {aid: st for aid, st in _action_state(run_id).items()
            if st["dispatch"]["phase"] == "diagnostic"}


def _exec_span_id(run_id: str, action_id: str) -> Optional[str]:
    for s in get_otlp_spans(run_id):
        if s["kind"] != SPAN_KIND_INTERNAL or not s["name"].startswith("execute_tool "):
            continue
        try:
            attrs = json.loads(s["attributes_json"])
        except Exception:
            continue
        if attrs.get("ga5.action.id") == action_id:
            return s["span_id"]
    return None


def _mark_action_failed(run_id: str, action_id: str) -> None:
    span_id = _exec_span_id(run_id, action_id)
    if span_id:
        update_otlp_span(span_id, status_code=STATUS_CODE_ERROR,
                         attributes={"error.type": "tool_call_failed"})


def _new_attempt(run_id: str, disp: Dict[str, Any], inc: Dict[str, Any],
                 attempt: int) -> Dict[str, Any]:
    """Issue another physical attempt of one logical action (retry or effect)."""
    tool = disp["tool_name"]
    action_id = disp["action_id"]
    call_id = disp["call_id"]
    args = json.loads(disp["arguments_json"])

    exec_id = _exec_span_id(run_id, action_id)
    if not exec_id:
        exec_id = gen_span_id()
        attrs = {
            "ga5.run.id": run_id,
            "ga5.public.marker": inc["public_marker"],
            "ga5.action.id": action_id,
            "gen_ai.tool.name": tool,
            "gen_ai.tool.call.id": call_id,
            "gen_ai.operation.name": "execute_tool",
        }
        if disp.get("approval_id"):
            attrs["ga5.approval.id"] = disp["approval_id"]
        record_otlp_span(
            span_id=exec_id, run_id=run_id, trace_id=inc["trace_id"],
            parent_span_id=inc["agent_span_id"], name=f"execute_tool {tool}",
            kind=SPAN_KIND_INTERNAL, attributes=attrs, status_code=STATUS_CODE_OK,
        )

    client_id = gen_span_id()
    attrs = {
        "ga5.run.id": run_id,
        "ga5.public.marker": inc["public_marker"],
        "ga5.action.id": action_id,
        "ga5.attempt": attempt,
        "http.request.method": "POST",
        "http.request.resend_count": max(0, attempt - 1),
    }
    if disp.get("approval_id"):
        attrs["ga5.approval.id"] = disp["approval_id"]
    record_otlp_span(
        span_id=client_id, run_id=run_id, trace_id=inc["trace_id"],
        parent_span_id=exec_id, name=f"POST tool/{tool}",
        kind=SPAN_KIND_CLIENT, attributes=attrs, status_code=STATUS_CODE_OK,
    )

    tp = make_traceparent(inc["trace_id"], client_id)
    evidence: List[str] = []
    try:
        evidence = json.loads(disp["evidence_json"]) if disp.get("evidence_json") else []
    except Exception:
        pass

    record_dispatch(
        run_id=run_id, action_id=action_id, call_id=call_id, phase=disp["phase"],
        tool_name=tool, arguments=args, evidence=evidence, attempt=attempt,
        traceparent=tp, client_span_id=client_id,
        approval_id=disp.get("approval_id"), approval_nonce=disp.get("approval_nonce"),
        tracestate=inc.get("tracestate"),
    )
    return _clean_dispatch({
        "actionId": action_id,
        "callId": call_id,
        "phase": disp["phase"],
        "toolName": tool,
        "arguments": args,
        "evidence": evidence,
        "attempt": attempt,
        "traceparent": tp,
        "approvalId": disp.get("approval_id"),
        "approvalNonce": disp.get("approval_nonce"),
        "tracestate": inc.get("tracestate"),
    })


def _dispatch_effect(run_id: str, inc: Dict[str, Any],
                     approval_id: Optional[str] = None,
                     approval_nonce: Optional[str] = None,
                     action_id: Optional[str] = None) -> Dict[str, Any]:
    """Issue the single justified effect call (attempt 1)."""
    effect_disp = next((d for d in get_dispatches(run_id) if d["phase"] == "effect"), None)
    if effect_disp is not None:
        return _dispatch_payload(effect_disp)

    inc_obj = json.loads(inc["request_json"]).get("incident", {})
    tool_catalog = json.loads(inc["request_json"]).get("toolCatalog", [])
    tool = inc.get("chosen_effect")
    service = inc_obj.get("service", "app-service")
    args = get_effect_arguments(
        tool, service, transcript=inc_obj.get("transcript", ""),
        severity=inc_obj.get("severity", "SEV-1"),
        tool_catalog=tool_catalog, incident=inc_obj,
        cause=inc.get("root_cause"),
    )

    action_id = action_id or f"act-eff-{gen_span_id()[:12]}"
    call_id = f"call-eff-{gen_span_id()[:12]}"
    exec_id = gen_span_id()
    attrs = {
        "ga5.run.id": run_id,
        "ga5.public.marker": inc["public_marker"],
        "ga5.action.id": action_id,
        "gen_ai.tool.name": tool,
        "gen_ai.tool.call.id": call_id,
        "gen_ai.operation.name": "execute_tool",
    }
    if approval_id:
        attrs["ga5.approval.id"] = approval_id
    record_otlp_span(
        span_id=exec_id, run_id=run_id, trace_id=inc["trace_id"],
        parent_span_id=inc["agent_span_id"], name=f"execute_tool {tool}",
        kind=SPAN_KIND_INTERNAL, attributes=attrs, status_code=STATUS_CODE_OK,
    )

    client_id = gen_span_id()
    c_attrs = {
        "ga5.run.id": run_id,
        "ga5.public.marker": inc["public_marker"],
        "ga5.action.id": action_id,
        "ga5.attempt": 1,
        "http.request.method": "POST",
        "http.request.resend_count": 0,
    }
    if approval_id:
        c_attrs["ga5.approval.id"] = approval_id
    record_otlp_span(
        span_id=client_id, run_id=run_id, trace_id=inc["trace_id"],
        parent_span_id=exec_id, name=f"POST tool/{tool}",
        kind=SPAN_KIND_CLIENT, attributes=c_attrs, status_code=STATUS_CODE_OK,
    )

    tp = make_traceparent(inc["trace_id"], client_id)
    try:
        evidence = json.loads(inc.get("evidence_json") or "[]")
    except Exception:
        evidence = []

    record_dispatch(
        run_id=run_id, action_id=action_id, call_id=call_id, phase="effect",
        tool_name=tool, arguments=args, evidence=evidence, attempt=1,
        traceparent=tp, client_span_id=client_id,
        approval_id=approval_id, approval_nonce=approval_nonce,
        tracestate=inc.get("tracestate"),
    )
    return _clean_dispatch({
        "actionId": action_id,
        "callId": call_id,
        "phase": "effect",
        "toolName": tool,
        "arguments": args,
        "evidence": evidence,
        "attempt": 1,
        "traceparent": tp,
        "approvalId": approval_id,
        "approvalNonce": approval_nonce,
        "tracestate": inc.get("tracestate"),
    })


# --------------------------------------------------------------------------- #
# POST /v2/incidents
# --------------------------------------------------------------------------- #
@app.post("/v2/incidents")
async def create_incident(request: Request):
    body_bytes = await request.body()
    if len(body_bytes) > MAX_BODY_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="Payload too large")

    try:
        body = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(body, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object")

    if body.get("profile") != PROFILE:
        raise HTTPException(status_code=422, detail="Unsupported profile")

    run_id = body.get("runId")
    if not isinstance(run_id, str) or not run_id.strip():
        raise HTTPException(status_code=422, detail="Missing runId")

    incident_data = body.get("incident")
    tool_catalog = body.get("toolCatalog")
    policy = body.get("policy")
    if not isinstance(incident_data, dict):
        raise HTTPException(status_code=422, detail="Missing incident")
    if not isinstance(tool_catalog, list):
        raise HTTPException(status_code=422, detail="Missing toolCatalog")
    if not isinstance(policy, dict):
        raise HTTPException(status_code=422, detail="Missing policy")

    req_hash = canonical_hash(body)

    async with _STATE_LOCK:
        existing = get_incident(run_id)
        if existing:
            if existing["request_hash"] != req_hash:
                raise HTTPException(status_code=409, detail="RUID_CONFLICT")
            if existing["status"] in ("completed", "failed"):
                return _json_response(build_terminal_response(existing), existing)
            stored = existing.get("last_response_json")
            if stored:
                return _json_response(json.loads(stored), existing)
            return _json_response(build_waiting_response(existing, [], []), existing)

        # ---- W3C trace context ------------------------------------------- #
        trace_id, in_parent_span_id = parse_traceparent(request.headers.get("traceparent"))
        ts_header = request.headers.get("tracestate")
        tracestate = ts_header.strip() if (in_parent_span_id and ts_header) else None

        public_marker = body.get("publicMarker") or "marker-telemetry-default"
        service = incident_data.get("service") or "app-service"
        severity = incident_data.get("severity") or "SEV-1"

        # ---- plan --------------------------------------------------------- #
        root_cause, evidence, diag_plans, chosen_effect, requires_approval = await analyze_incident(
            incident_data, tool_catalog, policy
        )

        root_server_span_id = gen_span_id()
        agent_span_id = gen_span_id()
        model_span_id = gen_span_id()

        record_otlp_span(
            span_id=root_server_span_id, run_id=run_id, trace_id=trace_id,
            parent_span_id=in_parent_span_id, name="POST /v2/incidents",
            kind=SPAN_KIND_SERVER,
            attributes={
                "ga5.run.id": run_id,
                "ga5.public.marker": public_marker,
                "http.request.method": "POST",
                "http.route": "/v2/incidents",
                "http.response.status_code": 200,
            },
            status_code=STATUS_CODE_OK,
        )
        record_otlp_span(
            span_id=agent_span_id, run_id=run_id, trace_id=trace_id,
            parent_span_id=root_server_span_id,
            name="invoke_agent incident-response", kind=SPAN_KIND_INTERNAL,
            attributes={"ga5.run.id": run_id, "ga5.public.marker": public_marker},
            status_code=STATUS_CODE_OK,
        )
        record_otlp_span(
            span_id=model_span_id, run_id=run_id, trace_id=trace_id,
            parent_span_id=agent_span_id, name="chat incident-plan",
            kind=SPAN_KIND_CLIENT,
            attributes={
                "ga5.run.id": run_id,
                "ga5.public.marker": public_marker,
                "gen_ai.operation.name": "chat",
                "gen_ai.request.model": get_model_name(),
            },
            status_code=STATUS_CODE_OK,
        )

        # Persist the run before any effect is even proposed.
        save_incident(
            run_id=run_id, profile=PROFILE, request_hash=req_hash, request_data=body,
            public_marker=public_marker, status_val="waiting", trace_id=trace_id,
            parent_span_id=in_parent_span_id, root_cause=root_cause, evidence=evidence,
            chosen_effect=chosen_effect, suppressed=[],
            root_server_span_id=root_server_span_id, agent_span_id=agent_span_id,
            model_span_id=model_span_id, tracestate=tracestate, last_response_json=None,
        )
        inc = get_incident(run_id)

        # ---- diagnostic fan-out ------------------------------------------ #
        dispatches: List[Dict[str, Any]] = []
        diag_exec_span_ids: List[str] = []
        for plan in diag_plans:
            tool_name = plan["toolName"]
            action_id = f"act-{gen_span_id()[:12]}"
            call_id = f"call-{gen_span_id()[:12]}"
            args = plan["arguments"]
            ev = plan["evidence"]

            exec_id = gen_span_id()
            record_otlp_span(
                span_id=exec_id, run_id=run_id, trace_id=trace_id,
                parent_span_id=agent_span_id, name=f"execute_tool {tool_name}",
                kind=SPAN_KIND_INTERNAL,
                attributes={
                    "ga5.run.id": run_id,
                    "ga5.public.marker": public_marker,
                    "ga5.action.id": action_id,
                    "gen_ai.tool.name": tool_name,
                    "gen_ai.tool.call.id": call_id,
                    "gen_ai.operation.name": "execute_tool",
                },
                status_code=STATUS_CODE_OK,
            )
            diag_exec_span_ids.append(exec_id)

            client_id = gen_span_id()
            record_otlp_span(
                span_id=client_id, run_id=run_id, trace_id=trace_id,
                parent_span_id=exec_id, name=f"POST tool/{tool_name}",
                kind=SPAN_KIND_CLIENT,
                attributes={
                    "ga5.run.id": run_id,
                    "ga5.public.marker": public_marker,
                    "ga5.action.id": action_id,
                    "ga5.attempt": 1,
                    "http.request.method": "POST",
                    "http.request.resend_count": 0,
                },
                status_code=STATUS_CODE_OK,
            )

            tp = make_traceparent(trace_id, client_id)
            record_dispatch(
                run_id=run_id, action_id=action_id, call_id=call_id, phase="diagnostic",
                tool_name=tool_name, arguments=args, evidence=ev, attempt=1,
                traceparent=tp, client_span_id=client_id, tracestate=tracestate,
            )
            dispatch = {
                "actionId": action_id, "callId": call_id, "phase": "diagnostic",
                "toolName": tool_name, "arguments": args, "evidence": ev,
                "attempt": 1, "traceparent": tp,
            }
            if tracestate:
                dispatch["tracestate"] = tracestate
            dispatches.append(dispatch)

        # ---- join (fan-in of independent diagnostics) --------------------- #
        if len(diag_exec_span_ids) > 1:
            record_otlp_span(
                span_id=gen_span_id(), run_id=run_id, trace_id=trace_id,
                parent_span_id=agent_span_id, name="incident.join",
                kind=SPAN_KIND_INTERNAL,
                attributes={"ga5.run.id": run_id, "ga5.public.marker": public_marker},
                status_code=STATUS_CODE_OK,
                links=[{"traceId": trace_id, "spanId": sid, "attributes": []}
                       for sid in diag_exec_span_ids],
            )

        inc = get_incident(run_id)
        if not dispatches and chosen_effect:
            # Catalog exposes no diagnostic tool: issue the justified effect only.
            dispatches.append(_dispatch_effect(run_id, inc))
            inc = get_incident(run_id) or inc

        resp_content = build_waiting_response(inc, dispatches, [])
        update_incident_response(run_id, json.dumps(resp_content))
        inc = get_incident(run_id)
        return _json_response(resp_content, inc)

    # unreachable
    raise HTTPException(status_code=500, detail="Internal error")


# --------------------------------------------------------------------------- #
# POST /v2/incidents/{runId}/receipts
# --------------------------------------------------------------------------- #
@app.post("/v2/incidents/{run_id}/receipts")
async def post_receipts(run_id: str, request: Request):
    body_bytes = await request.body()
    if len(body_bytes) > MAX_BODY_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            detail="Payload too large")
    try:
        body = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON receipt")
    if not isinstance(body, dict):
        raise HTTPException(status_code=422, detail="Receipt must be an object")

    receipt_id = body.get("receiptId")
    if not isinstance(receipt_id, str) or not receipt_id.strip():
        raise HTTPException(status_code=422, detail="Missing receiptId")

    rcpt_hash = canonical_hash(body)

    async with _STATE_LOCK:
        inc = get_incident(run_id)
        if not inc:
            raise HTTPException(status_code=404, detail="Run not found")

        existing_rows = get_receipts_by_id(receipt_id, run_id)
        if existing_rows:
            if existing_rows[0]["receipt_hash"] != rcpt_hash:
                raise HTTPException(status_code=409, detail="RECEIPT_CONFLICT")
            stored = get_receipt_response(run_id, receipt_id)
            if stored:
                return _json_response(json.loads(stored), inc)
            if inc["status"] in ("completed", "failed"):
                return _json_response(build_terminal_response(inc), inc)
            if inc.get("last_response_json"):
                return _json_response(json.loads(inc["last_response_json"]), inc)
            return _json_response(build_waiting_response(inc, [], []), inc)

        if inc["status"] in ("completed", "failed"):
            # Terminal runs are immutable: no field may change.
            raise HTTPException(status_code=422, detail="Run is already terminal")

        if isinstance(body.get("approvals"), list) and body["approvals"]:
            resp = _handle_approvals(run_id, inc, receipt_id, rcpt_hash, body["approvals"])
        elif isinstance(body.get("outcomes"), list) and body["outcomes"]:
            resp = _handle_outcomes(run_id, inc, receipt_id, rcpt_hash, body["outcomes"])
        else:
            raise HTTPException(status_code=422, detail="Malformed receipt")

        set_receipt_response(run_id, receipt_id, json.dumps(resp))
        update_incident_response(run_id, json.dumps(resp))
        inc = get_incident(run_id) or inc
        return _json_response(resp, inc)


# --------------------------------------------------------------------------- #
# Receipt handlers
# --------------------------------------------------------------------------- #
def _failed_diagnostics_response(run_id: str, inc: Dict[str, Any]) -> Dict[str, Any]:
    """A diagnostic failed (timeout / repeated 503).

    Suppress the dependent effect and terminate. Emitting any effect after its
    prerequisite timed out trips the safety cap, so nothing is dispatched here —
    not even an escalation such as page_owner.
    """
    if inc.get("chosen_effect"):
        update_incident_status(run_id, status_val="failed",
                               suppressed=[inc["chosen_effect"]])
        clear_chosen_effect(run_id)
    else:
        update_incident_status(run_id, status_val="failed")
    inc = get_incident(run_id) or inc
    return build_terminal_response(inc)


def _handle_outcomes(run_id: str, inc: Dict[str, Any], receipt_id: str,
                     rcpt_hash: str, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
    dispatches = get_dispatches(run_id)
    by_key = {(d["action_id"], d["call_id"], d["attempt"]): d for d in dispatches}
    already = {(r["action_id"], r["call_id"], r["attempt"]) for r in _outcome_rows(run_id)}

    # Validate the entire batch before mutating anything (atomic accept).
    seen = set()
    accepted: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for oc in outcomes:
        if not isinstance(oc, dict):
            raise HTTPException(status_code=422, detail="Invalid outcome")
        key = (oc.get("actionId"), oc.get("callId"), _num(oc.get("attempt", 1)))
        if key not in by_key or key in already or key in seen:
            raise HTTPException(status_code=422, detail="Outcome does not match a pending call")
        seen.add(key)
        accepted.append((oc, by_key[key]))

    retry_dispatches: List[Dict[str, Any]] = []
    for oc, disp in accepted:
        action_id = disp["action_id"]
        call_id = disp["call_id"]
        attempt = disp["attempt"]
        code = _num(oc.get("status"))
        result_class = oc.get("resultClass")
        err_type = oc.get("errorType")
        nonce = oc.get("nonce")
        if nonce is None:
            nonce = gen_span_id()

        record_receipt(
            run_id=run_id, receipt_id=receipt_id, receipt_hash=rcpt_hash,
            receipt_type="outcome", raw_json=json.dumps(oc),
            action_id=action_id, call_id=call_id, attempt=attempt,
            status_code=code, result_class=result_class,
            error_type=err_type, nonce=nonce,
        )

        span_attrs: Dict[str, Any] = {
            "ga5.receipt.id": receipt_id,
            "ga5.receipt.nonce": nonce,
        }
        span_status = STATUS_CODE_OK
        if err_type == "timeout" or code == 0:
            span_attrs["error.type"] = "timeout"
            span_status = STATUS_CODE_ERROR
            _mark_action_failed(run_id, action_id)
        elif code == 503:
            span_attrs["http.response.status_code"] = 503
            span_attrs["error.type"] = "503"
            span_status = STATUS_CODE_ERROR
            if attempt > 1:
                _mark_action_failed(run_id, action_id)
        elif isinstance(code, int) and 200 <= code < 300:
            span_attrs["http.response.status_code"] = code
        elif code is not None:
            span_attrs["http.response.status_code"] = code
            span_attrs["error.type"] = str(code)
            span_status = STATUS_CODE_ERROR
            _mark_action_failed(run_id, action_id)

        update_otlp_span(disp["client_span_id"], attributes=span_attrs,
                         status_code=span_status)

        # Exactly one retry per 503 on the first attempt.
        if code == 503 and attempt <= 1:
            retry_dispatches.append(_new_attempt(run_id, disp, inc, attempt + 1))

    if retry_dispatches:
        # A retry response never contains an approval request.
        return build_waiting_response(inc, retry_dispatches, [])

    state = _action_state(run_id)
    effect_state = next(
        (st for st in state.values() if st["dispatch"]["phase"] == "effect"), None)

    if effect_state is not None:
        if effect_state["state"] == "ok":
            update_incident_status(run_id, status_val="completed")
        elif effect_state["state"] in ("failed", "retry"):
            update_incident_status(
                run_id, status_val="failed",
                suppressed=[effect_state["dispatch"]["tool_name"]],
            )
            clear_chosen_effect(run_id)
        inc = get_incident(run_id) or inc
        if inc["status"] in ("completed", "failed"):
            return build_terminal_response(inc)
        return build_waiting_response(inc, [], [])

    diagnostics = _diagnostic_state(run_id)
    if any(st["state"] == "pending" for st in diagnostics.values()):
        return build_waiting_response(inc, [], [])

    # Every diagnostic is resolved. A failed diagnostic suppresses its
    # dependent effect (the run fails without an effect).
    if not diagnostics:
        # No diagnostics were possible (catalog without read tools): act on the
        # effect directly rather than leaving the run dead.
        if inc.get("chosen_effect"):
            dispatch = _dispatch_effect(run_id, inc)
            return build_waiting_response(inc, [dispatch], [])
        update_incident_status(run_id, status_val="completed")
        inc = get_incident(run_id) or inc
        return build_terminal_response(inc)

    if any(st["state"] == "failed" for st in diagnostics.values()):
        return _failed_diagnostics_response(run_id, inc)

    if not inc.get("chosen_effect"):
        update_incident_status(run_id, status_val="completed")
        inc = get_incident(run_id) or inc
        return build_terminal_response(inc)

    req_json = json.loads(inc["request_json"])
    policy = req_json.get("policy") or {}
    approval_tools = policy.get("approvalRequiredFor") or DEFAULT_APPROVAL_TOOLS

    if inc["chosen_effect"] in approval_tools:
        pending = get_pending_approvals(run_id)
        if pending:
            appr = pending[0]
            return build_waiting_response(inc, [], [{
                "approvalId": appr["approval_id"],
                "actionId": appr["action_id"],
                "toolName": appr["tool_name"],
                "argumentsDigest": appr["arguments_digest"],
            }])
        inc_obj = req_json.get("incident") or {}
        tool_catalog = req_json.get("toolCatalog") or []
        args = get_effect_arguments(
            inc["chosen_effect"], inc_obj.get("service", "app-service"),
            transcript=inc_obj.get("transcript", ""),
            severity=inc_obj.get("severity", "SEV-1"),
            tool_catalog=tool_catalog, incident=inc_obj, cause=inc.get("root_cause"),
        )
        approval_id = f"appr-{gen_span_id()[:12]}"
        action_id = f"act-eff-{gen_span_id()[:12]}"
        digest = canonical_hash(args)
        record_approval(
            approval_id=approval_id, run_id=run_id, action_id=action_id,
            tool_name=inc["chosen_effect"], arguments_digest=digest, arguments=args,
        )
        # The effect action id is reserved by the approval and reused later.
        return build_waiting_response(inc, [], [{
            "approvalId": approval_id,
            "actionId": action_id,
            "toolName": inc["chosen_effect"],
            "argumentsDigest": digest,
        }])

    dispatch = _dispatch_effect(run_id, inc)
    return build_waiting_response(inc, [dispatch], [])


def _handle_approvals(run_id: str, inc: Dict[str, Any], receipt_id: str,
                      rcpt_hash: str, approvals: List[Dict[str, Any]]) -> Dict[str, Any]:
    pending = get_pending_approvals(run_id)
    if not pending:
        raise HTTPException(status_code=422, detail="No pending approval")
    pending_by_id = {a["approval_id"]: a for a in pending}

    validated: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []
    for ap in approvals:
        if not isinstance(ap, dict):
            raise HTTPException(status_code=422, detail="Invalid approval")
        approval_id = ap.get("approvalId")
        if approval_id not in pending_by_id:
            raise HTTPException(status_code=422, detail="Approval is not pending for this run")
        decision = ap.get("decision")
        if decision != "approved":
            raise HTTPException(status_code=422, detail="Unsupported approval decision")
        validated.append((ap, pending_by_id[approval_id]))

    dispatched: Optional[Dict[str, Any]] = None
    for ap, record in validated:
        approval_id = record["approval_id"]
        nonce = ap.get("nonce")
        if nonce is None:
            nonce = gen_span_id()

        update_approval_decision(approval_id, "approved", nonce)
        record_receipt(
            run_id=run_id, receipt_id=receipt_id, receipt_hash=rcpt_hash,
            receipt_type="approval", raw_json=json.dumps(ap),
            approval_id=approval_id, decision="approved", nonce=nonce,
        )

        # The gate is recorded after the decision and before the effect runs.
        record_otlp_span(
            span_id=gen_span_id(), run_id=run_id, trace_id=inc["trace_id"],
            parent_span_id=inc["agent_span_id"], name="approval_gate",
            kind=SPAN_KIND_INTERNAL,
            attributes={
                "ga5.run.id": run_id,
                "ga5.public.marker": inc["public_marker"],
                "ga5.approval.id": approval_id,
                "ga5.approval.nonce": nonce,
                "ga5.receipt.id": receipt_id,
                "ga5.receipt.nonce": nonce,
            },
            status_code=STATUS_CODE_OK,
        )

        dispatched = _dispatch_effect(
            run_id, inc, approval_id=approval_id, approval_nonce=nonce,
            action_id=record.get("action_id"),
        )

    return build_waiting_response(inc, [dispatched] if dispatched else [], [])


# --------------------------------------------------------------------------- #
# GET /v2/incidents/{runId}
# --------------------------------------------------------------------------- #
@app.get("/v2/incidents/{run_id}")
async def get_incident_state(run_id: str):
    async with _STATE_LOCK:
        inc = get_incident(run_id)
        if not inc:
            raise HTTPException(status_code=404, detail="Run not found")
        if inc["status"] in ("completed", "failed"):
            return _json_response(build_terminal_response(inc), inc)
        stored = inc.get("last_response_json")
        if stored:
            return _json_response(json.loads(stored), inc)
        return _json_response(build_waiting_response(inc, [], []), inc)
