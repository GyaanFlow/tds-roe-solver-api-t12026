from __future__ import annotations

"""
Q02: OAuth 2.0 / OIDC Token Verification Service
POST /verify
- Validates RS256 JWT: signature, issuer, audience, expiry
- Returns 200 + claims on success, 401 on any failure
"""

import jwt
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from T22026.GA2.shared.tenant import current_email, get_q02_jwt_parameters

router = APIRouter(tags=["Q02 OAuth"])

# The public key from the exam (hardcoded — matches grader's IdP)
_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuY
cxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMID
EkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXc
WyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzf
Wed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsf
ISI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZI
XdQIDAQAB
-----END PUBLIC KEY-----"""


class VerifyRequest(BaseModel):
    token: str


@router.post("/verify")
async def verify_token(req: VerifyRequest):
    email  = current_email.get()
    params = get_q02_jwt_parameters(email)

    try:
        payload = jwt.decode(
            req.token,
            _PUBLIC_KEY,
            algorithms=["RS256"],
            audience=params["aud"],
            issuer=params["iss"],
            options={"require": ["exp", "iss", "aud", "sub"]},
            leeway=0,
        )
        return JSONResponse(
            status_code=200,
            content={
                "valid": True,
                "email": payload.get("email") or payload.get("sub"),
                "sub":   payload.get("sub"),
                "aud":   payload.get("aud"),
            },
        )
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=401, content={"valid": False, "reason": "expired"})
    except jwt.InvalidAudienceError:
        return JSONResponse(status_code=401, content={"valid": False, "reason": "wrong_audience"})
    except jwt.InvalidIssuerError:
        return JSONResponse(status_code=401, content={"valid": False, "reason": "wrong_issuer"})
    except jwt.InvalidSignatureError:
        return JSONResponse(status_code=401, content={"valid": False, "reason": "invalid_signature"})
    except Exception:
        return JSONResponse(status_code=401, content={"valid": False})
