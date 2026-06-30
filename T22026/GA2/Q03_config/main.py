from __future__ import annotations

"""
Q03: 12-Factor Config Precedence
GET /effective-config?set=key=value&set=...
- Merges 4 layers: defaults < yaml < .env < os-env
- CLI ?set= overrides highest precedence
- api_key always masked as ****
- CORS open (browser can verify directly)
"""

from fastapi import APIRouter, Query, Request, Response
from fastapi.responses import JSONResponse
from typing import List
from T22026.GA2.shared.tenant import current_email, get_q03_config_layers

router = APIRouter(tags=["Q03 Config"])

_COERCE_RULES = {
    "port":      lambda v: int(v),
    "workers":   lambda v: int(v),
    "debug":     lambda v: str(v).lower() in ("1", "true", "yes", "on"),
    "log_level": lambda v: str(v),
    "api_key":   lambda v: str(v),
}

def _coerce(key: str, val: str):
    fn = _COERCE_RULES.get(key)
    return fn(val) if fn else str(val)


def _cors(origin: str | None) -> dict:
    o = origin or "*"
    return {
        "Access-Control-Allow-Origin":  o,
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


@router.options("/effective-config")
async def options_effective_config(request: Request):
    return Response(status_code=200, headers=_cors(request.headers.get("Origin")))


@router.get("/effective-config")
async def get_effective_config(request: Request, set: List[str] = Query(default=[])):
    email  = current_email.get()
    layers = get_q03_config_layers(email)
    config = dict(layers["baseEffective"])

    # Apply CLI overrides (?set=key=value)
    for item in set:
        if "=" in item:
            k, v = item.split("=", 1)
            k = k.strip().lower()
            # Alias: num_workers -> workers (applies to CLI too for safety)
            if k == "num_workers":
                k = "workers"
            if k in config:
                try:
                    config[k] = _coerce(k, v)
                except (ValueError, TypeError):
                    pass  # silently ignore bad cast

    # Secret masking
    config["api_key"] = "****"

    return JSONResponse(content=config, headers=_cors(request.headers.get("Origin")))
