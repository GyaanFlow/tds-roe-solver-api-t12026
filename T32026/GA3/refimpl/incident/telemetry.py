"""
Telemetry and OTLP OpenTelemetry Generator
Specification: Tools in Data Science GA3 (q-agent-trace-integrity-server-v2)
W3C Trace Context and OpenTelemetry GenAI Registry Compliance
"""

import re
import secrets
import json
from typing import Dict, Any, List, Optional, Tuple

TRACEPARENT_RE = re.compile(r"^00-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")

SPAN_KIND_INTERNAL = 1
SPAN_KIND_SERVER = 2
SPAN_KIND_CLIENT = 3

STATUS_CODE_UNSET = 0
STATUS_CODE_OK = 1
STATUS_CODE_ERROR = 2


def gen_trace_id() -> str:
    """Generate a 32-character lowercase hex, non-zero trace ID."""
    while True:
        tid = secrets.token_hex(16)
        if tid != "0" * 32:
            return tid


def gen_span_id() -> str:
    """Generate a 16-character lowercase hex, non-zero span ID."""
    while True:
        sid = secrets.token_hex(8)
        if sid != "0" * 16:
            return sid


def parse_traceparent(tp: Optional[str]) -> Tuple[str, Optional[str]]:
    """
    Parse W3C traceparent header: 00-<trace_id>-<parent_span_id>-<flags>.
    Returns (trace_id, parent_span_id).
    If invalid or absent, returns fresh (trace_id, None).
    """
    if tp:
        m = TRACEPARENT_RE.match(tp.strip().lower())
        if m:
            trace_id, parent_span_id, _ = m.groups()
            if trace_id != "00000000000000000000000000000000" and parent_span_id != "0000000000000000":
                return trace_id, parent_span_id
    return gen_trace_id(), None


def make_traceparent(trace_id: str, span_id: str) -> str:
    return f"00-{trace_id}-{span_id}-01"


def format_attributes(attrs: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Format a dict into OTLP attributes.

    OTLP/JSON encodes int64 attribute values as decimal *strings* (proto3 JSON
    mapping), so an int must not be serialized as a bare JSON number.
    """
    res = []
    for k, v in attrs.items():
        if v is None:
            continue
        if isinstance(v, bool):
            res.append({"key": k, "value": {"boolValue": v}})
        elif isinstance(v, int):
            res.append({"key": k, "value": {"intValue": str(v)}})
        elif isinstance(v, float):
            res.append({"key": k, "value": {"doubleValue": v}})
        else:
            res.append({"key": k, "value": {"stringValue": str(v)}})
    return res


def build_otlp_resource_spans(spans_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Assembles complete OTLP ResourceSpans JSON structure.
    """
    # Make every parent's [start,end] enclose its children (deterministic, from stored data)
    spans_data = [dict(s) for s in spans_data]
    by_id = {s["span_id"]: s for s in spans_data}
    for s in spans_data:
        s["start_time_nano"] = int(s.get("start_time_nano") or 0)
        s["end_time_nano"] = int(s.get("end_time_nano") or 0)

    depth = {}

    def _d(s):
        n, cur = 0, s
        while cur.get("parent_span_id") in by_id and n < 50:
            cur = by_id[cur["parent_span_id"]]
            n += 1
        return n

    for s in sorted(spans_data, key=_d, reverse=True):
        p = by_id.get(s.get("parent_span_id"))
        if p:
            p["start_time_nano"] = min(p["start_time_nano"], s["start_time_nano"])
            p["end_time_nano"] = max(p["end_time_nano"], s["end_time_nano"])

    formatted_spans = []
    for s in spans_data:
        span_obj = {
            "traceId": s["trace_id"],
            "spanId": s["span_id"],
            "name": s["name"],
            "kind": s["kind"],
            "startTimeUnixNano": str(s.get("start_time_nano", "1710000000000000000")),
            "endTimeUnixNano": str(s.get("end_time_nano", "1710000001000000000")),
            "attributes": format_attributes(json.loads(s["attributes_json"])),
            "status": {
                "code": s.get("status_code", STATUS_CODE_OK)
            }
        }
        if s.get("parent_span_id"):
            span_obj["parentSpanId"] = s["parent_span_id"]
        if s.get("links_json"):
            span_obj["links"] = json.loads(s["links_json"])
        formatted_spans.append(span_obj)

    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": format_attributes({
                        "service.name": "incident-response"
                    })
                },
                "scopeSpans": [
                    {
                        "scope": {
                            "name": "ga5-incident-agent",
                            "version": "2.0.0"
                        },
                        "spans": formatted_spans
                    }
                ]
            }
        ]
    }
