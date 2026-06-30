from __future__ import annotations

"""
Q05: POST Analytics Endpoint
POST /analytics   (X-API-Key header required)
- Aggregates events: total_events, unique_users, revenue, top_user
- Missing / wrong key → 401
- CORS open for browser verification
"""

from fastapi import APIRouter, Header, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from T22026.GA2.shared.tenant import current_email, get_q05_api_key

router = APIRouter(tags=["Q05 Analytics"])


class Event(BaseModel):
    user: str
    amount: float
    ts: int


class AnalyticsRequest(BaseModel):
    events: List[Event]


def _cors(origin: str | None) -> dict:
    return {"Access-Control-Allow-Origin": origin or "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, X-API-Key"}


@router.options("/analytics")
async def options_analytics(request: Request):
    return Response(status_code=200, headers=_cors(request.headers.get("Origin")))


@router.post("/analytics")
async def post_analytics(
    body: AnalyticsRequest,
    request: Request,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
):
    email       = current_email.get()
    expected_key = get_q05_api_key(email)
    origin      = request.headers.get("Origin")

    if not x_api_key or x_api_key != expected_key:
        return JSONResponse(status_code=401, content={"detail": "Unauthorized"}, headers=_cors(origin))

    events = body.events
    total  = len(events)
    users  = {e.user for e in events}

    rev_by_user: dict[str, float] = {}
    for e in events:
        if e.amount > 0:
            rev_by_user[e.user] = rev_by_user.get(e.user, 0.0) + e.amount

    revenue  = sum(rev_by_user.values())
    top_user = max(rev_by_user, key=rev_by_user.get) if rev_by_user else None

    return JSONResponse(
        content={
            "email":        email,
            "total_events": total,
            "unique_users": len(users),
            "revenue":      round(revenue, 6),
            "top_user":     top_user,
        },
        headers=_cors(origin),
    )
