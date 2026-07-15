from __future__ import annotations

"""
T22026/GA4/q4data.py — In-memory Q4 dataset generator.

The Q4 grader posts ONLY a query (query_id, query_vector, filter, top_k,
rerank_top_n) and expects the deployed server to already hold the student's
500-document corpus. That corpus is deterministic per email, produced by the
exam's JS `seedrandom` (David Bau's ARC4 PRNG). This module is a verified Python
port of that PRNG plus the Q4 data generator, so we reproduce byte-identical
documents / embeddings / reranker_scores from just the email — no ZIP needed.
"""

from functools import lru_cache
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# seedrandom (David Bau ARC4 PRNG) — Python port, matches JS seedrandom output
# ---------------------------------------------------------------------------
def _mixkey(seed: str, key: list) -> None:
    smear = 0
    j = 0
    mask = 0xFF
    while j < len(seed):
        idx = j & mask
        cur = key[idx] if idx < len(key) else 0
        smear = (smear ^ (cur * 19)) & 0xFFFFFFFF
        val = (smear + ord(seed[j])) & mask
        if idx < len(key):
            key[idx] = val
        else:
            key.append(val)
        j += 1


class SeededRng:
    def __init__(self, seed: str):
        key: list = []
        _mixkey(str(seed), key)
        keylen = len(key) or 1
        s = list(range(256))
        j = 0
        for i in range(256):
            t = s[i]
            j = (j + t + key[i % keylen]) & 0xFF
            s[i] = s[j]
            s[j] = t
        self._s = s
        self._i = 0
        self._j = 0
        self._g(256)  # RC4-drop[256]

    def _g(self, count: int) -> int:
        s = self._s
        i = self._i
        j = self._j
        r = 0
        while count > 0:
            count -= 1
            i = (i + 1) & 0xFF
            t = s[i]
            j = (j + t) & 0xFF
            si_new = s[j]
            s[j] = t
            s[i] = si_new
            r = r * 256 + s[(si_new + t) & 0xFF]
        self._i = i
        self._j = j
        return r

    def __call__(self) -> float:
        significance = 2 ** 52
        overflow = significance * 2
        startdenom = 256 ** 6
        n = self._g(6)
        d = startdenom
        x = 0
        while n < significance:
            n = (n + x) * 256
            d *= 256
            x = self._g(1)
        while n >= overflow:
            n //= 2
            d //= 2
            x >>= 1
        return (n + x) / d


def seedrandom(seed: str) -> SeededRng:
    return SeededRng(seed)


# ---------------------------------------------------------------------------
# Q4 data generator — Python port of the exam's q4 data JS
# ---------------------------------------------------------------------------
_WE = "tds-ga4-q4-data-74b0cb0ad988a5d60aa486353b85d4ff816446657b041c85"
_CT = ["finance", "engineering", "marketing", "sales", "hr", "legal"]
_LT = ["north_america", "europe", "asia_pacific", "latin_america"]


def _generate(email: str) -> Tuple[List[dict], Dict[str, List[float]], Dict[str, Dict[str, float]]]:
    email = str(email or "").strip().lower()
    rng = seedrandom(f"{_WE}#{email}#q-vector-search-rerank-api#data")

    documents: List[dict] = []
    embeddings: Dict[str, List[float]] = {}
    for l in range(1, 501):
        doc_id = f"D{str(l).zfill(3)}"
        dept = _CT[int(rng() * len(_CT))]
        region = _LT[int(rng() * len(_LT))]
        year = 2020 + int(rng() * 7)
        documents.append({
            "doc_id": doc_id,
            "title": f"Document Title {doc_id} ({dept})",
            "department": dept,
            "year": year,
            "region": region,
            "text": f"This is the body text of document {doc_id} in department {dept} for region {region} and year {year}.",
        })
        doc_rng = seedrandom(f"{_WE}#{email}#q4#doc#{doc_id}")
        embeddings[doc_id] = [round(doc_rng() * 2 - 1, 4) for _ in range(100)]

    reranker_scores: Dict[str, Dict[str, float]] = {}
    for l in range(1, 11):
        q_id = f"Q{str(l).zfill(3)}"
        q_rng = seedrandom(f"{_WE}#{email}#q4#query#{q_id}")
        scores = {}
        for t in range(1, 501):
            d_id = f"D{str(t).zfill(3)}"
            scores[d_id] = round(q_rng(), 4)
        reranker_scores[q_id] = scores

    return documents, embeddings, reranker_scores


@lru_cache(maxsize=64)
def get_q4_dataset(email: str) -> Tuple[List[dict], Dict[str, List[float]], Dict[str, Dict[str, float]]]:
    """Per-email cached Q4 corpus (documents, embeddings, reranker_scores)."""
    return _generate(email)
