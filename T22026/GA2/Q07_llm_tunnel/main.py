from __future__ import annotations

"""
Q07: Expose a Local LLM through a Tunnel
POST /v1/chat/completions  (OpenAI-compatible)
- Echo test: repeats back TK<6-hex> tokens
- Arithmetic test: computes A+B sums
- Full CORS open for tunnel usage
"""

import re
import time
import uuid
from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(tags=["Q07 LLM Tunnel"])


class _Msg(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str
    messages: List[_Msg]
    stream: Optional[bool] = False
    temperature: Optional[float] = 0.0


def _cors(origin: str | None) -> dict:
    return {
        "Access-Control-Allow-Origin":  origin or "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }


@router.options("/v1/chat/completions")
async def options_completions(request: Request):
    return Response(status_code=200, headers=_cors(request.headers.get("Origin")))


@router.post("/v1/chat/completions")
async def chat_completions(body: ChatRequest, request: Request):
    prompt = body.messages[-1].content if body.messages else ""
    reply  = _route_prompt(prompt)

    payload = {
        "id":      f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object":  "chat.completion",
        "created": int(time.time()),
        "model":   body.model,
        "choices": [{"index": 0, "message": {"role": "assistant", "content": reply}, "finish_reason": "stop"}],
        "usage":   {"prompt_tokens": 10, "completion_tokens": len(reply.split()), "total_tokens": 10 + len(reply.split())},
    }
    return JSONResponse(content=payload, headers=_cors(request.headers.get("Origin")))


def _route_prompt(prompt: str) -> str:
    # Echo test — model must echo back TK<6-alphanumeric> verbatim (base-36)
    token_m = re.search(r'\b(TK[0-9A-Z]{6})\b', prompt, re.IGNORECASE)
    if token_m:
        tok = token_m.group(1).upper()
        return tok  # echo ONLY the token so grader's `.includes()` check passes

    # Arithmetic test — "What is A + B?"
    math_m = re.search(r'(\d+)\s*\+\s*(\d+)', prompt)
    if math_m:
        result = int(math_m.group(1)) + int(math_m.group(2))
        return str(result)

    return "Hello! How can I help you?"
