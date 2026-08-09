from __future__ import annotations

"""
T22026/GA6/main.py — GA6 router.

Only Q7 ("Scrape Books to Scrape by Category and Value") is implemented as a
live endpoint. Q1, Q3, Q8, Q10 genuinely need the student's own live exam
session, browser tab, or personal infrastructure (see solvers.py's module
docstring) -- no hosted API can produce or verify them, so they are
intentionally absent here rather than faked.
"""

import logging
import time
from typing import Any, Awaitable, Callable, TypeVar

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from T22026.GA6.solvers import derive_seed, digest_of, scrape_books

logger = logging.getLogger("ga6_router")
router = APIRouter()
T = TypeVar("T")


async def _run_solver(handler: Callable[[], Awaitable[T]], label: str, email: str) -> T | JSONResponse:
    start = time.time()
    try:
        result = await handler()
        logger.info("GA6 %s by %s completed in %.2fs", label, email, time.time() - start)
        return result
    except Exception:
        logger.exception("GA6 %s failed for %s after %.2fs", label, email, time.time() - start)
        return JSONResponse(status_code=502, content={
            "error": "Could not complete the live scrape of books.toscrape.com. "
                     "The site may be temporarily unreachable -- try again."
        })


@router.get("/scrape-books")
@router.get("/q7/scrape-books")
@router.get("/q7")
@router.get("/{email}/scrape-books")
@router.get("/{email}/q7/scrape-books")
@router.get("/{email}/q7")
async def scrape_books_endpoint(request: Request, email: str | None = None):
    email = email or request.scope.get("tenant_email") or "student@example.com"
    async def _handle():
        seed = derive_seed(email)
        rows = await scrape_books(seed)
        return {
            "email": email,
            "assignedCategories": seed["categoryNames"],
            "minRating": seed["minRating"],
            "minPrice": seed["minPrice"],
            "maxPrice": seed["maxPrice"],
            "minAvailability": seed["minAvailability"],
            "matchCount": len(rows),
            "digest": digest_of(rows),
            "hint": "Submit only the 'digest' value (64 lowercase hex characters) to the exam question.",
        }
    return await _run_solver(_handle, "Q7/scrape-books", email)


@router.get("/health")
async def health() -> dict:
    return {"status": "ok"}
