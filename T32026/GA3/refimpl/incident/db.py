"""
SQLite Storage for Observable Incident Triage Agent
Stores incidents, dispatches, receipts, approvals, and OTLP spans.
Handles idempotency, conflict detection, and telemetry replay.
"""

import os
import sqlite3
import json
import time
from typing import Optional, Dict, Any, List

import tempfile
DB_PATH = os.environ.get("GA3_INCIDENT_DB") or os.path.join(tempfile.gettempdir(), "t3ga3_incident_agent.db")

def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=30000")
    except Exception:
        pass
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                run_id TEXT PRIMARY KEY,
                profile TEXT NOT NULL,
                request_hash TEXT NOT NULL,
                request_json TEXT NOT NULL,
                public_marker TEXT NOT NULL,
                status TEXT NOT NULL,
                trace_id TEXT NOT NULL,
                parent_span_id TEXT,
                root_cause TEXT,
                evidence_json TEXT,
                chosen_effect TEXT,
                suppressed_json TEXT,
                root_server_span_id TEXT,
                agent_span_id TEXT,
                model_span_id TEXT,
                tracestate TEXT,
                last_response_json TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            )
        """)
        try:
            conn.execute("ALTER TABLE incidents ADD COLUMN tracestate TEXT")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE incidents ADD COLUMN last_response_json TEXT")
        except Exception:
            pass
        try:
            conn.execute("ALTER TABLE incidents ADD COLUMN receipt_responses_json TEXT")
        except Exception:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS dispatches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                action_id TEXT NOT NULL,
                call_id TEXT NOT NULL,
                phase TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                arguments_json TEXT NOT NULL,
                evidence_json TEXT,
                attempt INTEGER NOT NULL,
                traceparent TEXT NOT NULL,
                client_span_id TEXT NOT NULL,
                approval_id TEXT,
                approval_nonce TEXT,
                tracestate TEXT,
                created_at REAL NOT NULL
            )
        """)
        try:
            conn.execute("ALTER TABLE dispatches ADD COLUMN tracestate TEXT")
        except Exception:
            pass
        conn.execute("""
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                receipt_id TEXT NOT NULL,
                receipt_hash TEXT NOT NULL,
                receipt_type TEXT NOT NULL,
                action_id TEXT,
                call_id TEXT,
                approval_id TEXT,
                attempt INTEGER,
                status_code INTEGER,
                result_class TEXT,
                error_type TEXT,
                nonce TEXT,
                decision TEXT,
                raw_json TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS approvals (
                approval_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                action_id TEXT NOT NULL,
                tool_name TEXT NOT NULL,
                arguments_digest TEXT NOT NULL,
                arguments_json TEXT NOT NULL,
                decision TEXT,
                nonce TEXT,
                created_at REAL NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS otlp_spans (
                span_id TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                trace_id TEXT NOT NULL,
                parent_span_id TEXT,
                name TEXT NOT NULL,
                kind INTEGER NOT NULL,
                attributes_json TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                error_type TEXT,
                links_json TEXT,
                start_time_nano TEXT NOT NULL,
                end_time_nano TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        """)
        conn.commit()

init_db()

def get_incident(run_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM incidents WHERE run_id = ?", (run_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
    return None

def save_incident(
    run_id: str,
    profile: str,
    request_hash: str,
    request_data: Dict[str, Any],
    public_marker: str,
    status_val: str,
    trace_id: str,
    parent_span_id: Optional[str],
    root_cause: str,
    evidence: List[str],
    chosen_effect: Optional[str],
    suppressed: List[str],
    root_server_span_id: str,
    agent_span_id: str,
    model_span_id: str,
    tracestate: Optional[str] = None,
    last_response_json: Optional[str] = None
):
    now = time.time()
    with get_db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO incidents (
                run_id, profile, request_hash, request_json, public_marker,
                status, trace_id, parent_span_id, root_cause, evidence_json,
                chosen_effect, suppressed_json, root_server_span_id, agent_span_id,
                model_span_id, tracestate, last_response_json, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, profile, request_hash, json.dumps(request_data), public_marker,
            status_val, trace_id, parent_span_id, root_cause, json.dumps(evidence),
            chosen_effect, json.dumps(suppressed), root_server_span_id, agent_span_id,
            model_span_id, tracestate, last_response_json, now, now
        ))
        conn.commit()

def update_incident_response(run_id: str, last_response_json: str):
    now = time.time()
    with get_db() as conn:
        conn.execute("""
            UPDATE incidents
            SET last_response_json = ?, updated_at = ?
            WHERE run_id = ?
        """, (last_response_json, now, run_id))
        conn.commit()


def get_receipt_response(run_id: str, receipt_id: str):
    """Exact JSON body previously returned for this receipt (byte-stable replay)."""
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT receipt_responses_json FROM incidents WHERE run_id = ?", (run_id,))
        row = cur.fetchone()
        if not row or not row["receipt_responses_json"]:
            return None
        try:
            mapping = json.loads(row["receipt_responses_json"])
        except Exception:
            return None
        return mapping.get(receipt_id)


def set_receipt_response(run_id: str, receipt_id: str, response_json: str):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT receipt_responses_json FROM incidents WHERE run_id = ?", (run_id,))
        row = cur.fetchone()
        if not row:
            return
        try:
            mapping = json.loads(row["receipt_responses_json"]) if row["receipt_responses_json"] else {}
        except Exception:
            mapping = {}
        mapping[receipt_id] = response_json
        conn.execute("""
            UPDATE incidents
            SET receipt_responses_json = ?, updated_at = ?
            WHERE run_id = ?
        """, (json.dumps(mapping), time.time(), run_id))
        conn.commit()

def update_incident_status(run_id: str, status_val: str, chosen_effect: Optional[str] = None, suppressed: Optional[List[str]] = None):
    now = time.time()
    with get_db() as conn:
        if chosen_effect is not None and suppressed is not None:
            conn.execute("""
                UPDATE incidents
                SET status = ?, chosen_effect = ?, suppressed_json = ?, updated_at = ?
                WHERE run_id = ?
            """, (status_val, chosen_effect, json.dumps(suppressed), now, run_id))
        elif chosen_effect is not None:
            conn.execute("""
                UPDATE incidents
                SET status = ?, chosen_effect = ?, updated_at = ?
                WHERE run_id = ?
            """, (status_val, chosen_effect, now, run_id))
        elif suppressed is not None:
            conn.execute("""
                UPDATE incidents
                SET status = ?, suppressed_json = ?, updated_at = ?
                WHERE run_id = ?
            """, (status_val, json.dumps(suppressed), now, run_id))
        else:
            conn.execute("""
                UPDATE incidents
                SET status = ?, updated_at = ?
                WHERE run_id = ?
            """, (status_val, now, run_id))
        conn.commit()

def clear_chosen_effect(run_id: str):
    with get_db() as conn:
        conn.execute("UPDATE incidents SET chosen_effect = NULL, updated_at = ? WHERE run_id = ?", (time.time(), run_id))
        conn.commit()

def record_dispatch(
    run_id: str,
    action_id: str,
    call_id: str,
    phase: str,
    tool_name: str,
    arguments: Dict[str, Any],
    evidence: List[str],
    attempt: int,
    traceparent: str,
    client_span_id: str,
    approval_id: Optional[str] = None,
    approval_nonce: Optional[str] = None,
    tracestate: Optional[str] = None
):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO dispatches (
                run_id, action_id, call_id, phase, tool_name,
                arguments_json, evidence_json, attempt, traceparent,
                client_span_id, approval_id, approval_nonce, tracestate, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, action_id, call_id, phase, tool_name,
            json.dumps(arguments), json.dumps(evidence), attempt, traceparent,
            client_span_id, approval_id, approval_nonce, tracestate, time.time()
        ))
        conn.commit()

def get_dispatches(run_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dispatches WHERE run_id = ? ORDER BY id ASC", (run_id,))
        return [dict(r) for r in cur.fetchall()]

def record_receipt(
    run_id: str,
    receipt_id: str,
    receipt_hash: str,
    receipt_type: str,
    raw_json: str,
    action_id: Optional[str] = None,
    call_id: Optional[str] = None,
    approval_id: Optional[str] = None,
    attempt: Optional[int] = None,
    status_code: Optional[int] = None,
    result_class: Optional[str] = None,
    error_type: Optional[str] = None,
    nonce: Optional[str] = None,
    decision: Optional[str] = None
):
    with get_db() as conn:
        conn.execute("""
            INSERT INTO receipts (
                run_id, receipt_id, receipt_hash, receipt_type, action_id,
                call_id, approval_id, attempt, status_code, result_class,
                error_type, nonce, decision, raw_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            run_id, receipt_id, receipt_hash, receipt_type, action_id,
            call_id, approval_id, attempt, status_code, result_class,
            error_type, nonce, decision, raw_json, time.time()
        ))
        conn.commit()

def get_receipts_by_id(receipt_id: str, run_id: str = None) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        if run_id is None:
            cur.execute("SELECT * FROM receipts WHERE receipt_id = ?", (receipt_id,))
        else:
            cur.execute("SELECT * FROM receipts WHERE receipt_id = ? AND run_id = ?",
                        (receipt_id, run_id))
        return [dict(r) for r in cur.fetchall()]

def get_receipts(run_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM receipts WHERE run_id = ? ORDER BY id ASC", (run_id,))
        return [dict(r) for r in cur.fetchall()]

def record_approval(
    approval_id: str,
    run_id: str,
    action_id: str,
    tool_name: str,
    arguments_digest: str,
    arguments: Dict[str, Any]
):
    with get_db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO approvals (
                approval_id, run_id, action_id, tool_name,
                arguments_digest, arguments_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            approval_id, run_id, action_id, tool_name,
            arguments_digest, json.dumps(arguments), time.time()
        ))
        conn.commit()

def update_approval_decision(approval_id: str, decision: str, nonce: str):
    with get_db() as conn:
        conn.execute("""
            UPDATE approvals
            SET decision = ?, nonce = ?
            WHERE approval_id = ?
        """, (decision, nonce, approval_id))
        conn.commit()

def get_approval(approval_id: str) -> Optional[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM approvals WHERE approval_id = ?", (approval_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
    return None

def get_pending_approvals(run_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM approvals WHERE run_id = ? AND decision IS NULL", (run_id,))
        return [dict(r) for r in cur.fetchall()]

def record_otlp_span(
    span_id: str,
    run_id: str,
    trace_id: str,
    parent_span_id: Optional[str],
    name: str,
    kind: int,
    attributes: Dict[str, Any],
    status_code: int = 1,
    error_type: Optional[str] = None,
    links: Optional[List[Dict[str, Any]]] = None,
    start_time_nano: Optional[str] = None,
    end_time_nano: Optional[str] = None
):
    now_nano = str(int(time.time() * 1e9))
    start_t = start_time_nano or now_nano
    end_t = end_time_nano or str(int(start_t) + 50_000_000)
    with get_db() as conn:
        conn.execute("""
            INSERT OR REPLACE INTO otlp_spans (
                span_id, run_id, trace_id, parent_span_id, name,
                kind, attributes_json, status_code, error_type,
                links_json, start_time_nano, end_time_nano, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            span_id, run_id, trace_id, parent_span_id, name,
            kind, json.dumps(attributes), status_code, error_type,
            json.dumps(links) if links else None, start_t, end_t, time.time()
        ))
        conn.commit()

def update_otlp_span(span_id: str, attributes: Optional[Dict[str, Any]] = None, status_code: Optional[int] = None, error_type: Optional[str] = None):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM otlp_spans WHERE span_id = ?", (span_id,))
        row = cur.fetchone()
        if row:
            d = dict(row)
            curr_attrs = json.loads(d["attributes_json"])
            if attributes:
                curr_attrs.update(attributes)
            new_status = status_code if status_code is not None else d["status_code"]
            new_err = error_type if error_type is not None else d["error_type"]
            conn.execute("""
                UPDATE otlp_spans
                SET attributes_json = ?, status_code = ?, error_type = ?
                WHERE span_id = ?
            """, (json.dumps(curr_attrs), new_status, new_err, span_id))
            conn.commit()

def get_otlp_spans(run_id: str) -> List[Dict[str, Any]]:
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM otlp_spans WHERE run_id = ? ORDER BY created_at ASC, rowid ASC",
                    (run_id,))
        return [dict(r) for r in cur.fetchall()]
