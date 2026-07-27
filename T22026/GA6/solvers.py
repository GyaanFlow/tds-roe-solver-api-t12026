from __future__ import annotations

"""
T22026/GA6/solvers.py — GA6 Q7 "Scrape Books to Scrape by Category and Value".

Only Q7 is implemented here. The other GA6 questions (Q1 rotated-image
forensics, Q3 DuckDB regression, Q8 GitHub Action + Playwright, Q10 modem
audio decode) genuinely require the student's own live exam session, browser
tab, or personal infrastructure (a real GitHub repo/PAT/Action run) -- no
hosted API can produce or verify them, so they are guide-only.

Q7 is the opposite case: books.toscrape.com is a real, static, external site
whose catalog does not change per student -- only the assigned categories and
the price/rating/availability thresholds are seeded from the student's email.
That is exactly the shape every other GA hub in this repo already serves well
(deterministic per-email derivation + a live external call the student's own
browser can't make due to CORS), so it gets a proper hosted solver.
"""

import hashlib
import re
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, List, Optional, Tuple

import httpx

# ---------------------------------------------------------------------------
# Seed derivation -- ported from the exam's own ft(email) function.
#
# The exam bundle imports seedrandom's ALEA algorithm directly (confirmed by
# reading the bundled vendor code: the module's own export is `this.alea=`
# the alea factory function itself, not the whole seedrandom package), seeded
# with the literal string "{email}#q-scrape-books-server". Every derived
# value (Fisher-Yates category shuffle, then four Math.floor(rng()*N) draws
# in order) depends on the exact sequence of PRNG calls, so this port must
# match the JS algorithm bit-for-bit, not just "look similar".
#
# Cross-checked against the REAL npm `seedrandom/lib/alea` module (not just
# this port) for multiple emails before trusting it -- see the session notes;
# this is not a guess, it is a verified reimplementation.
# ---------------------------------------------------------------------------
QUESTION_ID = "q-scrape-books-server"
CATEGORIES_TO_ASSIGN = 5

# name/slug table, verbatim from the exam bundle (order matters: it is the
# array the Fisher-Yates shuffle permutes).
CATEGORY_TABLE: List[Dict[str, str]] = [
    {"name": "Travel", "slug": "travel_2"},
    {"name": "Mystery", "slug": "mystery_3"},
    {"name": "Historical Fiction", "slug": "historical-fiction_4"},
    {"name": "Sequential Art", "slug": "sequential-art_5"},
    {"name": "Classics", "slug": "classics_6"},
    {"name": "Philosophy", "slug": "philosophy_7"},
    {"name": "Romance", "slug": "romance_8"},
    {"name": "Womens Fiction", "slug": "womens-fiction_9"},
    {"name": "Fiction", "slug": "fiction_10"},
    {"name": "Childrens", "slug": "childrens_11"},
    {"name": "Religion", "slug": "religion_12"},
    {"name": "Nonfiction", "slug": "nonfiction_13"},
    {"name": "Music", "slug": "music_14"},
    {"name": "Default", "slug": "default_15"},
    {"name": "Science Fiction", "slug": "science-fiction_16"},
    {"name": "Sports and Games", "slug": "sports-and-games_17"},
    {"name": "Add a comment", "slug": "add-a-comment_18"},
    {"name": "Fantasy", "slug": "fantasy_19"},
    {"name": "New Adult", "slug": "new-adult_20"},
    {"name": "Young Adult", "slug": "young-adult_21"},
    {"name": "Science", "slug": "science_22"},
    {"name": "Poetry", "slug": "poetry_23"},
    {"name": "Paranormal", "slug": "paranormal_24"},
    {"name": "Art", "slug": "art_25"},
    {"name": "Psychology", "slug": "psychology_26"},
    {"name": "Autobiography", "slug": "autobiography_27"},
    {"name": "Parenting", "slug": "parenting_28"},
    {"name": "Adult Fiction", "slug": "adult-fiction_29"},
    {"name": "Humor", "slug": "humor_30"},
    {"name": "Horror", "slug": "horror_31"},
    {"name": "History", "slug": "history_32"},
    {"name": "Food and Drink", "slug": "food-and-drink_33"},
    {"name": "Christian Fiction", "slug": "christian-fiction_34"},
    {"name": "Business", "slug": "business_35"},
    {"name": "Biography", "slug": "biography_36"},
    {"name": "Thriller", "slug": "thriller_37"},
    {"name": "Contemporary", "slug": "contemporary_38"},
    {"name": "Spirituality", "slug": "spirituality_39"},
    {"name": "Academic", "slug": "academic_40"},
    {"name": "Self Help", "slug": "self-help_41"},
    {"name": "Historical", "slug": "historical_42"},
    {"name": "Christian", "slug": "christian_43"},
    {"name": "Suspense", "slug": "suspense_44"},
    {"name": "Short Stories", "slug": "short-stories_45"},
    {"name": "Novels", "slug": "novels_46"},
    {"name": "Health", "slug": "health_47"},
    {"name": "Politics", "slug": "politics_48"},
    {"name": "Cultural", "slug": "cultural_49"},
    {"name": "Erotica", "slug": "erotica_50"},
    {"name": "Crime", "slug": "crime_51"},
]

_UINT32_MOD = 2 ** 32


def _to_uint32(x: float) -> int:
    """JS `x >>> 0` (ToUint32), which the Mash hash relies on repeatedly."""
    if x != x or x in (float("inf"), float("-inf")):  # NaN / +-Inf
        return 0
    import math
    posint = math.floor(abs(x))
    if x < 0:
        posint = -posint
    return posint % _UINT32_MOD


def _to_int32(x: float) -> int:
    """JS `x | 0` (ToInt32), used once per Alea.next() call."""
    u = _to_uint32(x)
    return u - _UINT32_MOD if u >= 2 ** 31 else u


class _Mash:
    """Port of seedrandom's Johannes Baagøe Mash(), used to seed Alea's state.

    `n` is deliberately instance state that persists and mutates across
    calls -- alea() calls this SAME mash function six times in a row
    (three times with ' ', three times with the real seed) and each call
    continues from the last call's `n`, not a fresh one. Resetting `n`
    per-call would silently produce a different, wrong PRNG stream.
    """

    def __init__(self) -> None:
        self.n = 4022871197.0

    def __call__(self, data: Any) -> float:
        s = str(data)
        n = self.n
        for ch in s:
            n += ord(ch)
            r = 0.02519603282416938 * n
            n = float(_to_uint32(r))
            r -= n
            r *= n
            n = float(_to_uint32(r))
            r -= n
            n += r * 4294967296.0
        self.n = n
        return _to_uint32(n) * 2.3283064365386963e-10


class Alea:
    """Port of seedrandom's alea PRNG. `next()` matches the JS `rng()` call."""

    def __init__(self, seed: str) -> None:
        mash = _Mash()
        self.c = 1.0
        self.s0 = mash(" ")
        self.s1 = mash(" ")
        self.s2 = mash(" ")
        self.s0 -= mash(seed)
        if self.s0 < 0:
            self.s0 += 1
        self.s1 -= mash(seed)
        if self.s1 < 0:
            self.s1 += 1
        self.s2 -= mash(seed)
        if self.s2 < 0:
            self.s2 += 1

    def next(self) -> float:
        t = 2091639.0 * self.s0 + self.c * 2.3283064365386963e-10
        self.s0 = self.s1
        self.s1 = self.s2
        self.c = _to_int32(t)
        self.s2 = t - self.c
        return self.s2

    def __call__(self) -> float:
        return self.next()


def _shuffle(items: List[Dict[str, str]], rng: Alea) -> List[Dict[str, str]]:
    """Fisher-Yates, exactly as the exam bundle's own shuffle helper does it
    (descending index, `Math.floor(rng() * (i + 1))`)."""
    import math
    out = list(items)
    for i in range(len(out) - 1, 0, -1):
        j = math.floor(rng.next() * (i + 1))
        out[i], out[j] = out[j], out[i]
    return out


def derive_seed(email: str) -> Dict[str, Any]:
    """Reproduce ft(email) from the exam bundle exactly: one Alea instance,
    a shuffle (which consumes len(CATEGORY_TABLE)-1 draws), then four more
    draws IN THIS ORDER -- minRating, minPrice, maxPrice, minAvailability.
    Getting the draw order wrong desyncs every value after the first."""
    rng = Alea(f"{email}#{QUESTION_ID}")
    shuffled = _shuffle(CATEGORY_TABLE, rng)
    picked = sorted(c["slug"] for c in shuffled[:CATEGORIES_TO_ASSIGN])
    import math
    min_rating = 2 + math.floor(rng.next() * 4)
    min_price = 10 + math.floor(rng.next() * 30)
    max_price = min_price + 15 + math.floor(rng.next() * 25)
    min_availability = 2 + math.floor(rng.next() * 13)
    by_slug = {c["slug"]: c["name"] for c in CATEGORY_TABLE}
    category_names = [by_slug[s] for s in picked]
    return {
        "categories": picked,
        "categoryNames": category_names,
        "minRating": min_rating,
        "minPrice": min_price,
        "maxPrice": max_price,
        "minAvailability": min_availability,
    }


# ---------------------------------------------------------------------------
# Live scrape of books.toscrape.com
# ---------------------------------------------------------------------------
BASE_SITE = "https://books.toscrape.com/"

_RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
_AVAILABILITY_RE = re.compile(r"(\d+)\s+available", re.I)
_DETAIL_ID_RE = re.compile(r"/catalogue/([a-z0-9-]+_\d+)/index\.html", re.I)
_PRICE_RE = re.compile(r"[\d.]+")


def _extract_book_links_from_listing(html: str, base_url: str) -> List[str]:
    """Every product-detail link on one catalogue listing page."""
    import urllib.parse as up

    hrefs = re.findall(r'<h3>\s*<a[^>]+href="([^"]+)"', html)
    return [up.urljoin(base_url, h) for h in hrefs]


def _find_next_page(html: str, base_url: str) -> Optional[str]:
    import urllib.parse as up

    m = re.search(r'<li class="next">\s*<a href="([^"]+)"', html)
    return up.urljoin(base_url, m.group(1)) if m else None


def _find_category_url(home_html: str, slug: str) -> Optional[str]:
    """Parse the sidebar nav for the link whose href contains this category
    slug, per the spec's own instruction to discover the link rather than
    construct the URL blind."""
    import urllib.parse as up

    for href in re.findall(r'<a href="([^"]+)"[^>]*>\s*[^<]*</a>', home_html):
        if slug in href:
            return up.urljoin(BASE_SITE, href)
    return None


def _parse_detail_page(html: str, url: str) -> Optional[Dict[str, Any]]:
    m_id = _DETAIL_ID_RE.search(url)
    if not m_id:
        return None
    title_m = re.search(r"<h1>([^<]+)</h1>", html)
    if not title_m:
        return None
    title = title_m.group(1).strip()

    price_m = re.search(r'<p class="price_color">\s*[^\d]*([\d.]+)', html)
    if not price_m:
        return None
    price = float(price_m.group(1))

    rating_m = re.search(r'<p class="star-rating (\w+)"', html)
    if not rating_m or rating_m.group(1) not in _RATING_WORDS:
        return None
    rating = _RATING_WORDS[rating_m.group(1)]

    avail_m = _AVAILABILITY_RE.search(html)
    if not avail_m:
        return None
    availability = int(avail_m.group(1))

    return {
        "id": m_id.group(1),
        "title": title,
        "price": price,
        "rating": rating,
        "availability": availability,
    }


async def _fetch(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url, timeout=20.0)
    r.raise_for_status()
    return r.text


async def scrape_category(client: httpx.AsyncClient, category_url: str) -> List[str]:
    """All detail-page URLs across a category's paginated listing."""
    urls: List[str] = []
    page_url: Optional[str] = category_url
    seen_pages = set()
    while page_url and page_url not in seen_pages:
        seen_pages.add(page_url)
        html = await _fetch(client, page_url)
        urls.extend(_extract_book_links_from_listing(html, page_url))
        page_url = _find_next_page(html, page_url)
    return urls


async def scrape_books(seed: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Full Q7 pipeline: discover assigned category pages from the home page's
    sidebar, crawl each with pagination, fetch every book's detail page, and
    filter to the seeded thresholds."""
    import asyncio

    async with httpx.AsyncClient(follow_redirects=True) as client:
        home_html = await _fetch(client, BASE_SITE)
        category_urls: List[str] = []
        for slug in seed["categories"]:
            url = _find_category_url(home_html, slug)
            if url:
                category_urls.append(url)

        detail_url_lists = await asyncio.gather(*[scrape_category(client, u) for u in category_urls])
        all_detail_urls = [u for lst in detail_url_lists for u in lst]

        sem = asyncio.Semaphore(16)

        async def _one(url: str) -> Optional[Dict[str, Any]]:
            async with sem:
                try:
                    html = await _fetch(client, url)
                    return _parse_detail_page(html, url)
                except Exception:
                    return None

        parsed = await asyncio.gather(*[_one(u) for u in all_detail_urls])

    books = [b for b in parsed if b is not None]
    kept = []
    for b in books:
        if not (seed["minPrice"] <= b["price"] <= seed["maxPrice"]):
            continue
        if b["rating"] < seed["minRating"]:
            continue
        if b["availability"] < seed["minAvailability"]:
            continue
        value_score = float(
            (Decimal(str(b["rating"])) / Decimal(str(b["price"])))
            .quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
        )
        kept.append({**b, "value_score": value_score})

    kept.sort(key=lambda r: (-r["value_score"], r["id"]))
    return kept


# ---------------------------------------------------------------------------
# Canonical JSON + SHA-256, built by hand (not json.dumps) to match the
# spec's exact fixed-decimal formatting -- json.dumps would print 12.3 as
# "12.3", not "12.30", and would print 0.058 as "0.058", not "0.0580".
# ---------------------------------------------------------------------------
def canonical_json(rows: List[Dict[str, Any]]) -> str:
    parts = []
    for r in rows:
        parts.append(
            '{"id":"%s","title":"%s","price":%.2f,"rating":%d,"availability":%d,"value_score":%.4f}'
            % (
                _escape(r["id"]),
                _escape(r["title"]),
                r["price"],
                r["rating"],
                r["availability"],
                r["value_score"],
            )
        )
    return "[" + ",".join(parts) + "]"


def _escape(s: str) -> str:
    """Minimal JSON string escaping for values embedded via %-formatting
    (titles can contain quotes/backslashes; ids never do)."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def digest_of(rows: List[Dict[str, Any]]) -> str:
    canonical = canonical_json(rows)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


async def solve(email: str) -> Dict[str, Any]:
    seed = derive_seed(email)
    rows = await scrape_books(seed)
    canonical = canonical_json(rows)
    return {
        "email": email,
        "assignedCategories": seed["categoryNames"],
        "minRating": seed["minRating"],
        "minPrice": seed["minPrice"],
        "maxPrice": seed["maxPrice"],
        "minAvailability": seed["minAvailability"],
        "matchCount": len(rows),
        "books": rows,
        "canonicalJson": canonical,
        "digest": digest_of(rows),
    }
