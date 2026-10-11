from __future__ import annotations

import asyncio
import csv
import io
import json
import re
import time
from collections import OrderedDict
from typing import Any
from urllib.parse import parse_qs, parse_qsl, quote, urlencode, urlsplit

import httpx
from fastapi import APIRouter, Query, Request
from fastapi.responses import JSONResponse, Response

from T32026.GA1.shared.tenant import get_config, normalize_email, set_config
from T32026.GA1.solvers import answer_ledger_question, challenge_digest, effective_config, mcp_tool_definition
from T32026.GA1.termlog import decode_termlog

router = APIRouter()
EXAM_ORIGIN = "https://exam.sanand.workers.dev"
LEDGER_QUESTION_ID = "q-ledger-agent-server"
_LEDGER_CACHE: OrderedDict[tuple[str, str], tuple[float, dict[str, Any]]] = OrderedDict()
_LEDGER_CACHE_LOCK = asyncio.Lock()
_LEDGER_INFLIGHT: dict[str, asyncio.Task] = {}
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


def _quiz_sign_from_question_data_url(value: Any, email: str) -> str | None:
    """Validate the official per-student questionData URL and extract its signature."""
    if not isinstance(value, str) or len(value) > 8192:
        return None
    try:
        parsed = urlsplit(value.strip())
        params = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
    except ValueError:
        return None
    if (parsed.scheme != "https" or parsed.netloc.lower() != "exam.sanand.workers.dev"
            or parsed.path != "/questionData" or parsed.fragment or parsed.username or parsed.password):
        return None
    if any(len(params.get(key, [])) != 1 for key in ("email", "quizSign", "questionId", "path")):
        return None
    if normalize_email(params["email"][0]) != email:
        return None
    if params["questionId"][0] != LEDGER_QUESTION_ID or params["path"][0] != "/":
        return None
    quiz_sign = params["quizSign"][0]
    if not quiz_sign or len(quiz_sign) > 4096:
        return None
    return quiz_sign


@router.get("/health")
async def health():
    return {"status": "ok", "service": "t32026-ga1"}


@router.post("/q13/decode")
@router.post("/{email}/q13/decode")
async def decode_q13(request: Request, email: str | None = None):
    body, error = await _json_body(request, max_bytes=32768)
    if error:
        return error
    if not isinstance(body, dict) or not isinstance(body.get("ciphertext"), str):
        return JSONResponse(status_code=400, content={"error": "CIPHERTEXT_STRING_REQUIRED"})
    try:
        result = decode_termlog(body["ciphertext"])
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "CIPHERTEXT_REQUIRED_ASCII_MAX_16384"})
    # Stateless: no signature, student dataset, or decoded code is stored.
    status = 200 if result["candidates"] else 422
    return JSONResponse(status_code=status, content=result, headers={"Cache-Control": "no-store"})


@router.post("/onboard")
async def onboard(request: Request):
    body, error = await _json_body(request)
    if error:
        return error
    email = normalize_email(body.get("email")) if isinstance(body, dict) else ""
    if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return JSONResponse(status_code=400, content={"error": "VALID_EMAIL_REQUIRED"})
    question_data_url = body.get("question_data_url") if isinstance(body, dict) else None
    quiz_sign = _quiz_sign_from_question_data_url(question_data_url, email)
    if not quiz_sign:
        return JSONResponse(status_code=400, content={"error": "VALID_LEDGER_QUESTION_DATA_URL_REQUIRED"})
    # Reject an expired/incorrect signature before overwriting a working tenant.
    params = {"email": email, "quizSign": quiz_sign, "questionId": LEDGER_QUESTION_ID, "path": "/"}
    try:
        async with httpx.AsyncClient(timeout=_UPSTREAM_TIMEOUT, follow_redirects=False) as client:
            await _fetch_upstream(client, f"{EXAM_ORIGIN}/questionData", params)
    except httpx.TimeoutException:
        return JSONResponse(status_code=504, content={"error": "LEDGER_DISCOVERY_TIMEOUT"})
    except httpx.HTTPStatusError as exc:
        return JSONResponse(status_code=502, content={"error": "LEDGER_UPSTREAM_REJECTED", "upstream_status": exc.response.status_code})
    except httpx.HTTPError:
        return JSONResponse(status_code=502, content={"error": "LEDGER_UPSTREAM_CONNECTION_FAILED"})
    except ValueError:
        return JSONResponse(status_code=502, content={"error": "LEDGER_INVALID_UPSTREAM_JSON"})
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
async def get_effective_config(request: Request, email: str | None = None, set: list[str] = Query(default=[]), version: str = ""):
    student = _email(request, email)
    if not student:
        return JSONResponse(status_code=400, content={"error": "EMAIL_REQUIRED"})
    return JSONResponse(content=effective_config(set, student, version))


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
    if isinstance(value, str):
        if value.startswith("/questionData?") or value.startswith(EXAM_ORIGIN + "/questionData?"):
            try:
                params = parse_qs(urlsplit(value).query)
                if len(params.get("path", [])) == 1:
                    extra = [(k, v) for k, v in parse_qsl(urlsplit(value).query)
                             if k not in {"email", "quizSign", "questionId", "path"}]
                    path = params["path"][0]
                    found.append(path + ("&" if "?" in path else "?") + urlencode(extra) if extra else path)
            except ValueError:
                pass
        elif value.startswith("/") and not value.startswith("//"):
            found.append(value)
    elif isinstance(value, dict):
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
    params = dict(params)
    virtual = urlsplit(params.get("path", "/"))
    params["path"] = virtual.path
    for key, value in parse_qsl(virtual.query):
        if key not in {"email", "quizSign", "questionId", "path"}:
            params[key] = value
    async with _UPSTREAM_LIMIT:
        response = await client.get(url, params=params)
    response.raise_for_status()
    if len(response.content) > 8 * 1024 * 1024:
        raise ValueError("LEDGER_RESPONSE_TOO_LARGE")
    if "ndjson" in response.headers.get("content-type", "").lower():
        return {"orders": [json.loads(line) for line in response.text.splitlines() if line.strip()]}
    if "csv" in response.headers.get("content-type", "").lower():
        return {"rows": list(csv.DictReader(io.StringIO(response.text)))}
    return response.json()


async def _ledger_resources(student: str) -> tuple[dict[str, Any] | None, JSONResponse | None]:
    task = _LEDGER_INFLIGHT.get(student)
    if task is None:
        if len(_LEDGER_INFLIGHT) >= _CACHE_MAX_TENANTS:
            return None, JSONResponse(status_code=503, content={"error": "LEDGER_DISCOVERY_BUSY"})

        async def load():
            try:
                async with asyncio.timeout(12):
                    return await _discover_ledger_resources(student)
            except TimeoutError:
                return None, JSONResponse(status_code=504, content={"error": "LEDGER_DISCOVERY_TIMEOUT"})

        task = asyncio.create_task(load())
        _LEDGER_INFLIGHT[student] = task

        def finished(completed):
            if _LEDGER_INFLIGHT.get(student) is completed:
                _LEDGER_INFLIGHT.pop(student, None)

        task.add_done_callback(finished)
    return await asyncio.shield(task)


async def _discover_ledger_resources(student: str) -> tuple[dict[str, Any] | None, JSONResponse | None]:
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
    base_params = {"email": student, "quizSign": quiz_sign, "questionId": LEDGER_QUESTION_ID, "path": "/"}
    try:
        async with httpx.AsyncClient(timeout=_UPSTREAM_TIMEOUT, follow_redirects=False, limits=httpx.Limits(max_connections=48, max_keepalive_connections=24)) as client:
            root = await _fetch_upstream(client, url, base_params)
            resources: dict[str, Any] = {"/": root}
            seen = {"/"}
            pending = _resource_paths(root)

            async def fetch_path(path: str):
                try:
                    child = await _fetch_upstream(client, url, {**base_params, "path": path})
                    return path, child
                except (httpx.HTTPError, ValueError):
                    return None

            # Follow named root links and the next-page links advertised by
            # their responses. Never send signatures to an arbitrary host.
            for _ in range(12):
                queued = list(dict.fromkeys(path for path in pending if path not in seen))
                paths = queued[:32]
                if not paths:
                    break
                if len(seen) + len(paths) > 256:
                    return None, JSONResponse(status_code=502, content={"error": "LEDGER_DISCOVERY_LIMIT_EXCEEDED"})
                seen.update(paths)
                pending = queued[32:]
                for item in await asyncio.gather(*(fetch_path(path) for path in paths)):
                    if item is not None:
                        resources[item[0]] = item[1]
                        pending.extend(path for path in _resource_paths(item[1]) if path not in seen)
                # Acme's NDJSON export is the complete ledger, including all
                # revisions. Do not spend the deadline fetching 85 order pages.
                bulk = resources.get("/export")
                if isinstance(bulk, dict) and isinstance(bulk.get("orders"), list) and bulk["orders"]:
                    pending = [path for path in pending if urlsplit(path).path != "/orders"]
            if any(path not in seen for path in pending):
                return None, JSONResponse(status_code=502, content={"error": "LEDGER_DISCOVERY_LIMIT_EXCEEDED"})
    except httpx.TimeoutException:
        return None, JSONResponse(status_code=504, content={"error": "LEDGER_DISCOVERY_TIMEOUT"})
    except httpx.HTTPStatusError as exc:
        # Exception text contains the signed request URL. Never expose it.
        status = exc.response.status_code
        content = {"error": "LEDGER_UPSTREAM_REJECTED", "upstream_status": status}
        if status in (401, 403):
            content["action"] = "Save this email's current signed Ledger URL again in the dashboard."
        return None, JSONResponse(status_code=502, content=content)
    except httpx.HTTPError:
        return None, JSONResponse(status_code=502, content={"error": "LEDGER_UPSTREAM_CONNECTION_FAILED"})
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
