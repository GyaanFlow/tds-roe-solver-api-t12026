"""Tests for the GA6 live-API hub, mounted at /ga6/{email}/...

GA6 has 10 questions; only Q7 (Scrape Books to Scrape by Category and Value)
is served here. Q1 (rotated-image forensics), Q3 (DuckDB regression), Q8
(GitHub Action + Playwright), and Q10 (modem audio decode) genuinely need the
student's own live exam session, browser tab, or personal infrastructure --
no hosted API can produce or verify them, so this hub does not attempt them.

The seed-derivation port (T22026/GA6/solvers.py: Alea, _Mash, _shuffle,
derive_seed) was cross-checked against the REAL npm `seedrandom/lib/alea`
module for 18 different emails (3 by hand, 15 fuzzed) before being trusted --
see the session notes. These tests re-pin those exact verified values as a
permanent regression guard, since a wrong PRNG port would silently assign
every student the wrong categories/thresholds without ever raising an error.

Q7's own test makes a REAL network call to books.toscrape.com (there is
nothing to solve without one -- the whole point of this endpoint is a live
external scrape), so it is slower than the fully-mocked suites and will fail
if that site is briefly unreachable.
"""

from decimal import ROUND_HALF_UP, Decimal

from fastapi.testclient import TestClient

from hf_space.app import app
from T22026.GA6.solvers import canonical_json, derive_seed, digest_of

client = TestClient(app)


def test_health():
    r = client.get("/ga6/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_home_page():
    r = client.get("/ga6/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]


# ---------------------------------------------------------------------------
# Seed derivation -- pinned against the REAL npm seedrandom/lib/alea module.
# ---------------------------------------------------------------------------
def test_seed_derivation_matches_the_real_npm_seedrandom_alea_module():
    cases = {
        "23f1000805@ds.study.iitm.ac.in": {
            "categories": ["cultural_49", "erotica_50", "nonfiction_13", "novels_46", "sports-and-games_17"],
            "categoryNames": ["Cultural", "Erotica", "Nonfiction", "Novels", "Sports and Games"],
            "minRating": 5, "minPrice": 28, "maxPrice": 58, "minAvailability": 11,
        },
        "test@example.com": {
            "categories": ["adult-fiction_29", "fantasy_19", "food-and-drink_33", "horror_31", "mystery_3"],
            "categoryNames": ["Adult Fiction", "Fantasy", "Food and Drink", "Horror", "Mystery"],
            "minRating": 2, "minPrice": 10, "maxPrice": 32, "minAvailability": 2,
        },
        "student@x.com": {
            "categories": ["fiction_10", "humor_30", "novels_46", "parenting_28", "travel_2"],
            "categoryNames": ["Fiction", "Humor", "Novels", "Parenting", "Travel"],
            "minRating": 5, "minPrice": 11, "maxPrice": 40, "minAvailability": 7,
        },
        # 5 more emails, cross-checked directly against `node -e
        # "require('seedrandom/lib/alea')"` with each email passed as its own
        # isolated argument (an earlier shell pipeline that piped a file
        # through `mapfile`/`tr` produced silently corrupted values here once
        # -- these are re-verified straight from a fresh, direct node
        # invocation, not copied from that intermediate file).
        "aji0@example.com": {
            "categories": ["adult-fiction_29", "historical_42", "poetry_23", "short-stories_45", "womens-fiction_9"],
            "categoryNames": ["Adult Fiction", "Historical", "Poetry", "Short Stories", "Womens Fiction"],
            "minRating": 3, "minPrice": 36, "maxPrice": 54, "minAvailability": 12,
        },
        "dpbhsahxthv@example.com": {
            "categories": ["art_25", "food-and-drink_33", "health_47", "romance_8", "travel_2"],
            "categoryNames": ["Art", "Food and Drink", "Health", "Romance", "Travel"],
            "minRating": 3, "minPrice": 29, "maxPrice": 61, "minAvailability": 8,
        },
        "1fp@example.com": {
            "categories": ["art_25", "classics_6", "fiction_10", "paranormal_24", "womens-fiction_9"],
            "categoryNames": ["Art", "Classics", "Fiction", "Paranormal", "Womens Fiction"],
            "minRating": 2, "minPrice": 36, "maxPrice": 56, "minAvailability": 8,
        },
        "ff0t0pvn9e@example.com": {
            "categories": ["contemporary_38", "cultural_49", "erotica_50", "humor_30", "young-adult_21"],
            "categoryNames": ["Contemporary", "Cultural", "Erotica", "Humor", "Young Adult"],
            "minRating": 2, "minPrice": 15, "maxPrice": 40, "minAvailability": 4,
        },
        "4azytjxepq8@example.com": {
            "categories": ["historical-fiction_4", "novels_46", "poetry_23", "romance_8", "womens-fiction_9"],
            "categoryNames": ["Historical Fiction", "Novels", "Poetry", "Romance", "Womens Fiction"],
            "minRating": 2, "minPrice": 39, "maxPrice": 77, "minAvailability": 9,
        },
    }
    for email, expected in cases.items():
        got = derive_seed(email)
        got_cmp = {k: got[k] for k in expected}
        assert got_cmp == expected, f"seed mismatch for {email}: expected {expected}, got {got_cmp}"


def test_derive_seed_is_deterministic_across_repeated_calls():
    """The global CATEGORY_TABLE must never be mutated by the shuffle --
    otherwise a second call for the same email (or any call after it) would
    silently drift from the first."""
    a = derive_seed("repeat-check@example.com")
    b = derive_seed("repeat-check@example.com")
    assert a == b
    # A different email afterward must not have been affected by the first call.
    c = derive_seed("test@example.com")
    assert c["categories"] == ["adult-fiction_29", "fantasy_19", "food-and-drink_33", "horror_31", "mystery_3"]


# ---------------------------------------------------------------------------
# Canonical JSON + digest formatting
# ---------------------------------------------------------------------------
def test_canonical_json_exact_key_order_and_fixed_decimals():
    rating, price = 3, 51.77
    value_score = float(
        (Decimal(str(rating)) / Decimal(str(price))).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    )
    row = {
        "id": "a-light-in-the-attic_1000", "title": "A Light in the Attic",
        "price": price, "rating": rating, "availability": 22, "value_score": value_score,
    }
    cj = canonical_json([row])
    assert cj == (
        '[{"id":"a-light-in-the-attic_1000","title":"A Light in the Attic",'
        '"price":51.77,"rating":3,"availability":22,"value_score":0.0579}]'
    )
    # No structural whitespace (no space after ':' or ',').
    assert '": "' not in cj
    assert cj.startswith("[") and cj.endswith("]")

    digest = digest_of([row])
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)


def test_canonical_json_price_always_has_two_decimals():
    row = {"id": "x_1", "title": "T", "price": 12.0, "rating": 4, "availability": 5, "value_score": 0.3333}
    cj = canonical_json([row])
    assert '"price":12.00' in cj


# ---------------------------------------------------------------------------
# Live endpoint (real network call to books.toscrape.com)
# ---------------------------------------------------------------------------
def test_q7_scrape_books_live_endpoint():
    r = client.get("/ga6/test@example.com/scrape-books")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["email"] == "test@example.com"
    assert body["assignedCategories"] == ["Adult Fiction", "Fantasy", "Food and Drink", "Horror", "Mystery"]
    assert body["minRating"] == 2 and body["minPrice"] == 10 and body["maxPrice"] == 32 and body["minAvailability"] == 2
    assert isinstance(body["matchCount"], int) and body["matchCount"] > 0
    digest = body["digest"]
    assert len(digest) == 64 and all(c in "0123456789abcdef" for c in digest)

    # Same email, same live site -> same digest (determinism check).
    r2 = client.get("/ga6/test@example.com/scrape-books")
    assert r2.json()["digest"] == digest


def test_q7_percent_encoded_email_matches_plain_email():
    r1 = client.get("/ga6/test@example.com/scrape-books")
    r2 = client.get("/ga6/test%40example.com/scrape-books")
    assert r1.json()["digest"] == r2.json()["digest"]


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
