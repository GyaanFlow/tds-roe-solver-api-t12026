from __future__ import annotations

import logging
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List, Optional
from T22026.GA3.shared.tenant import current_email, set_tenant_config
from T22026.GA3.solvers import (
    solve_multimodal_qa,
    solve_invoice_extract,
    solve_dynamic_extract,
    solve_korean_audio,
    solve_structured_extraction,
    solve_semantic_rank,
    solve_cot_math,
    solve_youtube_filter,
    solve_cosine_similarity,
    solve_proof_of_work,
    solve_context_window_heist,
    solve_spin_up_cli,
    solve_embedding_trapdoors,
)

logger = logging.getLogger("ga3_router")
router = APIRouter()

# --- Q2: Multimodal Image QA ---
class MultimodalRequest(BaseModel):
    image_base64: str
    question: str

@router.post("/q2/answer-image")
@router.post("/answer-image")
@router.post("/q2")
async def answer_image(req: MultimodalRequest):
    email = current_email.get()
    logger.info(f"Q2 Multimodal QA for {email}: {req.question}")
    try:
        ans = await solve_multimodal_qa(req.image_base64, req.question)
        return {"answer": str(ans)}
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error in Q2: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Q3: Fixed Schema Invoice Extraction ---
class ExtractRequest(BaseModel):
    invoice_text: str

@router.post("/q3/extract")
@router.post("/extract")
@router.post("/q3")
async def extract_invoice(req: ExtractRequest):
    email = current_email.get()
    logger.info(f"Q3 Fixed Extract for {email}")
    try:
        ans = await solve_invoice_extract(req.invoice_text)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error in Q3: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Q4: Dynamic Schema Structured Extraction ---
class DynamicExtractRequest(BaseModel):
    text: str
    schema: Dict[str, Any]

@router.post("/q4/dynamic-extract")
@router.post("/dynamic-extract")
@router.post("/q4")
async def dynamic_extract(req: DynamicExtractRequest):
    email = current_email.get()
    logger.info(f"Q4 Dynamic Extract for {email}")
    try:
        ans = await solve_dynamic_extract(req.text, req.schema)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error in Q4: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Q6: Korean Audio Dataset API ---
@router.post("/q6")
async def korean_audio(request: Request):
    email = current_email.get()
    body = await request.json()
    logger.info(f"Q6 Korean Audio Request for {email}: keys={list(body.keys())}")
    print(f"DEBUG Q6 Body keys: {list(body.keys())}")
    # Print sample of base64 if present
    if "audio_base64" in body:
        b64 = body["audio_base64"]
        print(f"DEBUG Q6 base64 snippet: {b64[:100]}... length={len(b64)}")
    try:
        ans = await solve_korean_audio(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error in Q6: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Q7: Invoice Intelligence Extraction ---
@router.post("/q7")
async def structured_extraction(request: Request):
    email = current_email.get()
    body = await request.json()
    logger.info(f"Q7 Structured Extraction for {email}")
    try:
        ans = await solve_structured_extraction(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error in Q7: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Q8: Semantic Search Passage Ranking ---
@router.post("/q8")
async def semantic_rank(request: Request):
    email = current_email.get()
    body = await request.json()
    logger.info(f"Q8 Semantic Rank for {email}")
    try:
        ans = await solve_semantic_rank(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error in Q8: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Q9: Word-Problem Solver ---
@router.post("/q9")
async def cot_math(request: Request):
    email = current_email.get()
    body = await request.json()
    logger.info(f"Q9 CoT Math for {email}")
    try:
        ans = await solve_cot_math(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        logger.error(f"Error in Q9: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# --- Config & Solver Routes for Dashboard ---


class OnboardRequest(BaseModel):
    email: str
    aipipe_token: str | None = None


class OnboardResponse(BaseModel):
    email: str
    configured: bool
    has_token: bool
    base_url: str
    solver_url_prefix: str
    ready_routes: List[str]

@router.post("/config")
async def save_config(req: ConfigSaveRequest):
    email = current_email.get()
    set_tenant_config(email, {"aipipe_token": req.aipipe_token})
    return {"status": "ok", "message": f"AIPipe token saved for {email}"}

@router.post("/onboard", response_model=OnboardResponse)
async def onboard(req: OnboardRequest, request: Request):
    email = req.email.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    if req.aipipe_token:
        set_tenant_config(email, {"aipipe_token": req.aipipe_token})
    base = str(request.base_url).rstrip("/")
    ready_routes = [
        f"{base}/ga3/{email}/q2",
        f"{base}/ga3/{email}/q3",
        f"{base}/ga3/{email}/q4",
        f"{base}/ga3/{email}/q6",
        f"{base}/ga3/{email}/q7",
        f"{base}/ga3/{email}/q8",
        f"{base}/ga3/{email}/q9",
    ]
    return OnboardResponse(
        email=email,
        configured=True,
        has_token=bool(req.aipipe_token),
        base_url=base,
        solver_url_prefix=f"{base}/ga3/{email}",
        ready_routes=ready_routes,
    )

@router.post("/solve/q1")
async def solve_q1(request: Request):
    body = await request.json()
    try:
        ans = await solve_youtube_filter(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/solve/q5")
async def solve_q5(request: Request):
    body = await request.json()
    try:
        ans = await solve_cosine_similarity(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/solve/q10")
async def solve_q10(request: Request):
    body = await request.json()
    try:
        ans = await solve_proof_of_work(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/solve/q11")
async def solve_q11(request: Request):
    body = await request.json()
    try:
        ans = await solve_context_window_heist(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/solve/q12")
async def solve_q12(request: Request):
    body = await request.json()
    try:
        ans = await solve_spin_up_cli(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/solve/q13")
async def solve_q13(request: Request):
    body = await request.json()
    try:
        ans = await solve_embedding_trapdoors(body)
        return ans
    except RuntimeError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})



