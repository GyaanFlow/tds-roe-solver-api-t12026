from __future__ import annotations

import asyncio
import json
import re
import time
from collections import OrderedDict
from typing import Any
from urllib.parse import quote

import httpx
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, Response

from T32026.GA1.shared.tenant import get_config, normalize_email, set_config
from T32026.GA1.solvers import answer_ledger_question, challenge_digest, effective_config, mcp_tool_definition

router = APIRouter()
EXAM_ORIGIN = "https://exam.sanand.workers.dev"
_LEDGER_CACHE: OrderedDict[tuple[str, str], tuple[float, dict[str, Any]]] = OrderedDict()
_LEDGER_CACHE_LOCK = asyncio.Lock()
_UPSTREAM_LIMIT = asyncio.Semaphore(48)
_CACHE_TTL_SECONDS = 45
_CACHE_MAX_TENANTS = 512
_UPSTREAM_TIMEOUT = httpx.Timeout(9.0, connect=3.0, pool=2.0)


def _email(request: Request, email: str | None = None) -> str:
    return normalize_email(email or request.scope.get("tenant_email") or request.query_params.get("email") or "")


async def _json_body(request: Request, max_bytes: int = 32_768) -> tuple[Any | None, JSONResponse | None]:
    length = request.headers.get("content-length")
    if length:
        try:
            if int(length) > max_bytes:
                return None, JSONResponse(status_code=413, content={"error": "REQUEST_TOO_LARGE"})
        except ValueError:
            return None, JSONResponse(status_code=400, content={"error": "INVALID_CONTENT_LENGTH"})
    chunks: list[bytes] = []
    size = 0
    try:
        async for chunk in request.stream():
            size += len(chunk)
            if size > max_bytes:
                return None, JSONResponse(status_code=413, content={"error": "REQUEST_TOO_LARGE"})
            chunks.append(chunk)
        body = json.loads(b"".join(chunks))
    except Exception:
        return None, JSONResponse(status_code=400, content={"error": "INVALID_JSON"})
    return body, None


@router.get("/health")
async def health():
    return {"status": "ok", "service": "t32026-ga1"}


@router.post("/onboard")
async def onboard(request: Request):
    body, error = await _json_body(request)
    if error:
        return error
    email = normalize_email(body.get("email")) if isinstance(body, dict) else ""
    if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return JSONResponse(status_code=400, content={"error": "VALID_EMAIL_REQUIRED"})
    raw_sign = body.get("quiz_sign", "") if isinstance(body, dict) else ""
    if not isinstance(raw_sign, (str, int)):
        return JSONResponse(status_code=400, content={"error": "INVALID_QUIZ_SIGN"})
    quiz_sign = str(raw_sign).strip()
    if len(quiz_sign) > 512:
        return JSONResponse(status_code=400, content={"error": "INVALID_QUIZ_SIGN"})
    try:
        await asyncio.to_thread(set_config, email, {"quiz_sign": quiz_sign})
    except Exception:
        return JSONResponse(status_code=503, content={"error": "TENANT_STORE_UNAVAILABLE"})
    base = f"{request.url.scheme}://{request.url.netloc}"
    prefix = f"{base}/ga1/{quote(email, safe='')}"
    return {
        "status": "ok",
        "email": email,
        "ledger_configured": bool(quiz_sign),
        "routes": {
            "effective_config": f"{prefix}/effective-config",
            "ledger_answer": f"{prefix}/ledger/answer",
            "ledger_discover": f"{prefix}/ledger/discover",
            "mcp": f"{prefix}/mcp",
        },
    }


@router.get("/{email}/effective-config")
@router.get("/effective-config")
async def get_effective_config(request: Request, email: str | None = None, set: list[str] = Query(default=[])):
    # The live verifier sends valid fresh CLI overrides and compares them with
    # the documented defaults. Keep this route stateless and mask the secret.
    return JSONResponse(content=effective_config(set))


def _api_paths(value: Any) -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        declared = value.get("paths")
        if isinstance(declared, dict):
            paths.extend(path for path in declared if isinstance(path, str))
        for child in value.values():
            paths.extend(_api_paths(child))
    elif isinstance(value, list):
        for child in value:
            paths.extend(_api_paths(child))
    return paths


def _links(value: Any) -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key in ("href", "url"):
            path = value.get(key)
            if isinstance(path, str) and path.startswith("/") and not path.startswith("//"):
                found.append(path)
        for child in value.values():
            found.extend(_links(child))
    elif isinstance(value, list):
        for child in value:
            found.extend(_links(child))
    return found


def _resource_paths(root: Any) -> list[str]:
    candidates = ["/openapi.json", *_api_paths(root), *_links(root)]
    seen: set[str] = set()
    paths = []
    for path in candidates:
        if not isinstance(path, str) or not path.startswith("/") or path.startswith("//"):
            continue
        if len(path) > 300 or ".." in path.split("/"):
            continue
        if path not in seen:
            seen.add(path)
            paths.append(path)
        if len(paths) >= 32:
            break
    return paths


async def _fetch_upstream(client: httpx.AsyncClient, url: str, params: dict[str, str]):
    async with _UPSTREAM_LIMIT:
        response = await client.get(url, params=params)
    response.raise_for_status()
    return response.json()


async def _ledger_resources(student: str) -> tuple[dict[str, Any] | None, JSONResponse | None]:
    if not student:
        return None, JSONResponse(status_code=400, content={"error": "EMAIL_REQUIRED"})
    try:
        config = await asyncio.to_thread(get_config, student)
    except Exception:
        return None, JSONResponse(status_code=503, content={"error": "TENANT_STORE_UNAVAILABLE"})
    quiz_sign = config.get("quiz_sign")
    if not quiz_sign:
        return None, JSONResponse(status_code=409, content={"error": "ONBOARD_WITH_EMAIL_AND_QUIZ_SIGN_FIRST"})
    cache_key = (student, quiz_sign)
    now = time.monotonic()
    async with _LEDGER_CACHE_LOCK:
        cached = _LEDGER_CACHE.get(cache_key)
        if cached and cached[0] > now:
            _LEDGER_CACHE.move_to_end(cache_key)
            return cached[1], None
        if cached:
            _LEDGER_CACHE.pop(cache_key, None)

    url = f"{EXAM_ORIGIN}/questionData"
    base_params = {"email": student, "quizSign": quiz_sign, "questionId": "q-ledger-agent-server", "path": "/"}
    try:
        async with httpx.AsyncClient(timeout=_UPSTREAM_TIMEOUT, follow_redirects=False, limits=httpx.Limits(max_connections=48, max_keepalive_connections=24)) as client:
            root = await _fetch_upstream(client, url, base_params)
            resources: dict[str, Any] = {"/": root}
            paths = _resource_paths(root)

            async def fetch_path(path: str):
                try:
                    child = await _fetch_upstream(client, url, {**base_params, "path": path})
                    return path, child
                except (httpx.HTTPError, ValueError):
                    return None

            for item in await asyncio.gather(*(fetch_path(path) for path in paths)):
                if item is not None:
                    resources[item[0]] = item[1]
    except httpx.TimeoutException:
        return None, JSONResponse(status_code=504, content={"error": "LEDGER_DISCOVERY_TIMEOUT"})
    except httpx.HTTPError:
        return None, JSONResponse(status_code=502, content={"error": "LEDGER_DISCOVERY_FAILED"})
    except ValueError:
        return None, JSONResponse(status_code=502, content={"error": "LEDGER_INVALID_UPSTREAM_JSON"})

    async with _LEDGER_CACHE_LOCK:
        _LEDGER_CACHE[cache_key] = (time.monotonic() + _CACHE_TTL_SECONDS, resources)
        _LEDGER_CACHE.move_to_end(cache_key)
        while len(_LEDGER_CACHE) > _CACHE_MAX_TENANTS:
            _LEDGER_CACHE.popitem(last=False)
    return resources, None


def _resource_manifest(resources: dict[str, Any]) -> dict[str, Any]:
    def fields(value: Any) -> list[str]:
        names: set[str] = set()
        if isinstance(value, dict):
            names.update(str(key) for key in value.keys())
            for child in value.values():
                names.update(fields(child))
        elif isinstance(value, list):
            for child in value[:100]:
                names.update(fields(child))
        return sorted(names)

    return {"paths": sorted(resources), "resource_count": len(resources),
            "fields": {path: fields(payload)[:100] for path, payload in resources.items()}}


@router.get("/{email}/ledger/discover")
@router.get("/ledger/discover")
async def discover_ledger(request: Request, email: str | None = None):
    student = _email(request, email)
    resources, error = await _ledger_resources(student)
    if error:
        return error
    # The bench exposes schema/route metadata only; private ledger rows are not
    # copied into a public debug response.
    return {"origin": EXAM_ORIGIN, **_resource_manifest(resources or {})}


@router.post("/{email}/ledger/answer")
@router.post("/ledger/answer")
async def ledger_answer(request: Request, email: str | None = None):
    student = _email(request, email)
    body, error = await _json_body(request)
    if error:
        return error
    question = body.get("question") if isinstance(body, dict) else None
    if not isinstance(question, str) or not question.strip() or len(question) > 4000:
        return JSONResponse(status_code=400, content={"error": "QUESTION_REQUIRED_OR_TOO_LONG"})
    resources, error = await _ledger_resources(student)
    if error:
        return error
    try:
        return {"answer": answer_ledger_question(question, resources or {})}
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"error": "UNSUPPORTED_LEDGER_QUESTION", "detail": str(exc)})


async def _mcp_response(request: Request, email: str):
    message, parse_error = await _json_body(request, max_bytes=16_384)
    if parse_error:
        code = -32700 if parse_error.status_code == 400 else -32600
        message = "Parse error" if code == -32700 else "Request body too large"
        return JSONResponse(status_code=parse_error.status_code, content={"jsonrpc": "2.0", "id": None, "error": {"code": code, "message": message}})
    if not isinstance(message, dict) or message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        return JSONResponse(status_code=400, content={"jsonrpc": "2.0", "id": message.get("id") if isinstance(message, dict) else None, "error": {"code": -32600, "message": "Invalid Request"}})
    method, request_id = message["method"], message.get("id")
    params = message.get("params")
    if params is not None and not isinstance(params, dict):
        return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Invalid params"}}
    params = params or {}
    if method.startswith("notifications/"):
        return Response(status_code=202)
    if method == "initialize":
        version = params.get("protocolVersion", "2025-03-26")
        if not isinstance(version, str):
            version = "2025-03-26"
        return {"jsonrpc": "2.0", "id": request_id, "result": {
            "protocolVersion": version,
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "t32026-ga1-challenge", "version": "1.0.0"},
        }}
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": [mcp_tool_definition()]}}
    if method == "tools/call":
        if params.get("name") != "solve_challenge":
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Unknown tool"}}
        challenge = request.headers.get("x-exam-challenge", "")
        if not re.fullmatch(r"[0-9a-f]{32}", challenge):
            return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32602, "message": "Missing or invalid X-Exam-Challenge header"}}
        answer = challenge_digest(challenge, email)
        return {"jsonrpc": "2.0", "id": request_id, "result": {"content": [{"type": "text", "text": answer}], "isError": False}}
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": -32601, "message": "Method not found"}}


@router.post("/{email}/mcp")
async def mcp_for_email(email: str, request: Request):
    return await _mcp_response(request, normalize_email(email))


@router.post("/mcp")
async def mcp_default(request: Request):
    return await _mcp_response(request, _email(request))
