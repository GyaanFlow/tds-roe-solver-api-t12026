"""Tests for the GA6 live-API hub, mounted at /ga6/{email}/...

GA6 has 10 questions; only Q7 (Scrape Books to Scrape by Category and Value)
is served here. Q1 (rotated-image forensics), Q3 (DuckDB regression), Q8
(GitHub Action + Playwright), and Q10 (modem audio decode) genuinely need the
student's own live exam session, browser tab, or personal infrastructure --
no hosted API can produce or verify them, so this hub does not attempt them.

The seed-derivation port (T22026/GA6/solvers.py: SeedRandom/_ARC4/_mixkey,
_shuffle, derive_seed) uses the npm `seedrandom` package's DEFAULT export
(David Bau's ARC4-based Math.seedrandom) -- NOT Alea. An earlier version of
this file used Alea, based on a mistaken static-analysis inference (finding
"this.alea=" text elsewhere in the exam bundle's vendor chunk and wrongly
assuming that's what this call site resolved to); that shipped to production
and gave every student the wrong assigned categories/thresholds/digest,
silently -- no exception, just a plausible-looking wrong answer. Caught by
actually executing the exam bundle's own minified code in Node (CDN imports
stubbed, since this function needs none of them) and finding its real output
didn't match this port's Alea-based values.

The corrected ARC4 port was verified two ways before trusting it: ran the
exam bundle's own code directly and compared output for 10 emails/edge cases,
and separately ported seedrandom.js line-for-line and verified its raw PRNG
output against the real npm package across empty/very-long/mixed-case/
spaced seed strings. These tests re-pin those exact verified values as a
permanent regression guard, since a wrong PRNG port fails silently, not
loudly.

Q7's own test makes a REAL network call to books.toscrape.com (there is
nothing to solve without one -- the whole point of this endpoint is a live
external scrape), so it is slower than the fully-mocked suites and will fail
if that site is briefly unreachable.
"""

from decimal import ROUND_HALF_UP, Decimal
import pytest
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
# Seed derivation -- pinned against the REAL npm `seedrandom` default (ARC4)
# export, and separately against the exam bundle's own executed code.
# ---------------------------------------------------------------------------
def test_seed_derivation_matches_the_real_npm_seedrandom_default_arc4_export():
    cases = {
        "test@example.com": {
            "categories": ["academic_40", "art_25", "biography_36", "humor_30", "religion_12"],
            "categoryNames": ["Academic", "Art", "Biography", "Humor", "Religion"],
            "minRating": 3, "minPrice": 21, "maxPrice": 60, "minAvailability": 8,
        },
        "23f1000805@ds.study.iitm.ac.in": {
            "categories": ["music_14", "poetry_23", "self-help_41", "sports-and-games_17", "suspense_44"],
            "categoryNames": ["Music", "Poetry", "Self Help", "Sports and Games", "Suspense"],
            "minRating": 3, "minPrice": 11, "maxPrice": 38, "minAvailability": 13,
        },
        "student@x.com": {
            "categories": ["academic_40", "cultural_49", "novels_46", "politics_48", "romance_8"],
            "categoryNames": ["Academic", "Cultural", "Novels", "Politics", "Romance"],
            "minRating": 4, "minPrice": 15, "maxPrice": 46, "minAvailability": 6,
        },
        # 7 more emails/edge cases, cross-checked directly against
        # `node -e "require('seedrandom')(...)"` with each email passed as its
        # own isolated argv entry (no file-piping -- an earlier round of this
        # exact mistake, with the WRONG algorithm, silently corrupted values
        # via a mapfile/tr shell pipeline; this time verified straight from
        # direct node invocations only).
        "aji0@example.com": {
            "categories": ["cultural_49", "erotica_50", "historical-fiction_4", "history_32", "paranormal_24"],
            "categoryNames": ["Cultural", "Erotica", "Historical Fiction", "History", "Paranormal"],
            "minRating": 3, "minPrice": 29, "maxPrice": 49, "minAvailability": 7,
        },
        "dpbhsahxthv@example.com": {
            "categories": ["default_15", "erotica_50", "historical_42", "self-help_41", "thriller_37"],
            "categoryNames": ["Default", "Erotica", "Historical", "Self Help", "Thriller"],
            "minRating": 4, "minPrice": 21, "maxPrice": 60, "minAvailability": 9,
        },
        "1fp@example.com": {
            "categories": ["erotica_50", "horror_31", "parenting_28", "politics_48", "travel_2"],
            "categoryNames": ["Erotica", "Horror", "Parenting", "Politics", "Travel"],
            "minRating": 2, "minPrice": 37, "maxPrice": 60, "minAvailability": 8,
        },
        "ff0t0pvn9e@example.com": {
            "categories": ["biography_36", "default_15", "health_47", "poetry_23", "thriller_37"],
            "categoryNames": ["Biography", "Default", "Health", "Poetry", "Thriller"],
            "minRating": 2, "minPrice": 34, "maxPrice": 52, "minAvailability": 9,
        },
        "4azytjxepq8@example.com": {
            "categories": ["adult-fiction_29", "cultural_49", "music_14", "novels_46", "parenting_28"],
            "categoryNames": ["Adult Fiction", "Cultural", "Music", "Novels", "Parenting"],
            "minRating": 4, "minPrice": 19, "maxPrice": 54, "minAvailability": 5,
        },
        "x@y.com": {
            "categories": ["classics_6", "cultural_49", "new-adult_20", "sequential-art_5", "thriller_37"],
            "categoryNames": ["Classics", "Cultural", "New Adult", "Sequential Art", "Thriller"],
            "minRating": 2, "minPrice": 29, "maxPrice": 59, "minAvailability": 14,
        },
        "a-very-long-email-address-for-testing@example-domain.co.in": {
            "categories": ["childrens_11", "default_15", "sports-and-games_17", "travel_2", "young-adult_21"],
            "categoryNames": ["Childrens", "Default", "Sports and Games", "Travel", "Young Adult"],
            "minRating": 3, "minPrice": 26, "maxPrice": 52, "minAvailability": 6,
        },
    }
    for email, expected in cases.items():
        got = derive_seed(email)
        got_cmp = {k: got[k] for k in expected}
        assert got_cmp == expected, f"seed mismatch for {email}: expected {expected}, got {got_cmp}"


def test_seedrandom_arc4_raw_output_matches_npm_across_edge_cases():
    """Regression for the specific bug found: the ARC4 port initially omitted
    RC4-drop[256] (the real source discards the first 256 generator outputs
    immediately after key scheduling, `(me.g=function(){...})(width)`),
    which silently desynced every subsequent value from the real generator's
    internal i/j state without ever raising an error. Pins raw PRNG output
    (not the higher-level derive_seed) against real `node -e
    "require('seedrandom')(seed)"` output for seeds most likely to expose a
    mixkey/ARC4 edge case: empty string, very long string, embedded space,
    and mixed case."""
    from T22026.GA6.solvers import SeedRandom

    cases = {
        "hello": [0.5463663768140734, 0.4397379377059223, 0.554769432473455],
        "": [0.23144008215179881, 0.27404636548159655],
        "test@example.com#q-scrape-books-server": [0.8205332964303583, 0.7656229521437286, 0.30121421344748867],
        "with spaces @example.com#q-scrape-books-server": [0.9464034853778767, 0.546637207810008, 0.022664450835335165],
        "UPPER@EXAMPLE.COM#q-scrape-books-server": [0.5148203109858379, 0.39620941419990185, 0.5788821211017916],
    }
    for seed, expected in cases.items():
        rng = SeedRandom(seed)
        got = [rng.next() for _ in expected]
        assert got == expected, f"raw PRNG mismatch for seed {seed!r}: expected {expected}, got {got}"


def test_derive_seed_is_deterministic_across_repeated_calls():
    """The global CATEGORY_TABLE must never be mutated by the shuffle --
    otherwise a second call for the same email (or any call after it) would
    silently drift from the first."""
    a = derive_seed("repeat-check@example.com")
    b = derive_seed("repeat-check@example.com")
    assert a == b
    # A different email afterward must not have been affected by the first call.
    c = derive_seed("test@example.com")
    assert c["categories"] == ["academic_40", "art_25", "biography_36", "humor_30", "religion_12"]


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
    assert body["assignedCategories"] == ["Academic", "Art", "Biography", "Humor", "Religion"]
    assert body["minRating"] == 3 and body["minPrice"] == 21 and body["maxPrice"] == 60 and body["minAvailability"] == 8
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


@pytest.mark.parametrize("path", [
    "/ga6/test@example.com/scrape-books",
    "/ga6/test@example.com/q7",
    "/ga6/test@example.com/q7/scrape-books",
])
def test_q7_aliases_are_json_routes(path):
    r = client.get(path, headers={"Accept": "application/json"})
    assert r.status_code == 200, r.text
    assert r.headers["content-type"].lower().startswith("application/json")
    body = r.json()
    assert set(("email", "assignedCategories", "minRating", "minPrice",
                "maxPrice", "minAvailability", "matchCount", "digest")) <= body.keys()
    assert not r.text.lstrip().lower().startswith("<!doctype")


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
