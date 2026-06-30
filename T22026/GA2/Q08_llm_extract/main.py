from __future__ import annotations

"""
Q08: LLM Structured Output – Invoice Field Extractor
POST /extract  { text: str }
Returns: { vendor, currency, date, amount }
Uses priority-weighted regex — no network calls needed.
"""

import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["Q08 LLM Extract"])


class ExtractRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor:   Optional[str]
    currency: Optional[str]
    date:     Optional[str]
    amount:   Optional[float]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_CURRENCY_PAT = re.compile(r'\b(USD|EUR|GBP)\b', re.IGNORECASE)
_DATE_PAT     = re.compile(r'\b(20\d{2}-\d{2}-\d{2})\b')
# Amount — look near a currency keyword first, then standalone
_AMT_NEAR_PAT = re.compile(
    r'(?:USD|EUR|GBP|\$|€|£|amount|total|due|price|subtotal)\s*(?::|is)?\s*([0-9]+(?:\.[0-9]{1,2})?)',
    re.IGNORECASE,
)
_AMT_ANY_PAT  = re.compile(r'\b([0-9]+(?:\.[0-9]{1,2})?)\b')
_VENDOR_PATS  = [
    re.compile(r'(?:vendor|seller|merchant|billed\s+by|from|issued\s+by):\s*([^\n\r,]+)', re.IGNORECASE),
    re.compile(r'(?:invoice\s+from)\s+([^\n\r,]+)', re.IGNORECASE),
]


def _extract_amount(text: str) -> Optional[float]:
    # Priority 1: near currency/amount keyword
    m = _AMT_NEAR_PAT.search(text)
    if m:
        val = float(m.group(1))
        if 50.0 <= val <= 9050.0:
            return val
    # Priority 2: any bare number in range (skip 4-digit years)
    for m in _AMT_ANY_PAT.finditer(text):
        raw = m.group(1)
        val = float(raw)
        if val == int(val) and 1900 <= int(val) <= 2100:
            continue   # skip years
        if 50.0 <= val <= 9050.0:
            return val
    return None


def _extract_vendor(text: str) -> Optional[str]:
    for pat in _VENDOR_PATS:
        m = pat.search(text)
        if m:
            return m.group(1).strip()
    return None


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------

@router.post("/extract", response_model=InvoiceResponse)
async def extract_invoice(req: ExtractRequest):
    text = req.text or ""
    if not text.strip():
        raise HTTPException(status_code=422, detail="Empty input text")

    # Currency
    cm = _CURRENCY_PAT.search(text)
    currency = cm.group(1).upper() if cm else None

    # Date (first YYYY-MM-DD match)
    dm = _DATE_PAT.search(text)
    date = dm.group(1) if dm else None

    amount = _extract_amount(text)
    vendor = _extract_vendor(text)

    return {
        "vendor":   vendor,
        "currency": currency,
        "date":     date,
        "amount":   amount,
    }
