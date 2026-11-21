"""Per-student data generators for T3-2026 GA5, ported from the exam page
(``exam-tds-2026-09-ga5.js``) and verified against the real npm ``seedrandom``.

* Q1 ``q-rag-colosseum-server``: the student's 50-passage knowledge base.
* Q2 ``q-ollama-faiss-rank-correlation-server``: 50 sentences + 10 queries.

Templates/slot values/domains live in ``exam_data.json`` (extracted from the exam source).
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from T22026.shared.seedrandom_arc4 import SeedRandom

_DATA = Path(__file__).with_name("exam_data.json")
_SLOT_RE = re.compile(r"\{\{([A-Z_]+)\}\}")


@lru_cache(maxsize=1)
def exam_data() -> dict[str, Any]:
    return json.loads(_DATA.read_text(encoding="utf-8"))


def _norm_email(email: str) -> str:
    return str(email or "").strip().lower()


# ------------------------------------------------------------------------- Q1
def rag_knowledge_base(email: str) -> dict[str, Any]:
    """Return {"passages": [...50], "domains": [...50 domain names], "tokens": [...slot values per passage]}."""
    rag = exam_data()["rag"]
    rng = SeedRandom(f"{_norm_email(email)}#rag-colosseum-server")
    passages: list[str] = []
    domains: list[str] = []
    tokens: list[dict[str, str]] = []
    for domain in rag["domains"]:
        for template in rag["templates"][domain]:
            text = template
            used: dict[str, str] = {}
            for slot in _SLOT_RE.findall(template):  # one draw per occurrence, in order
                options = rag["slotValues"][slot]
                value = options[int(rng() * len(options))]
                text = text.replace("{{" + slot + "}}", value, 1)  # JS String.replace: first occurrence only
                used[slot] = value
            passages.append(text)
            domains.append(domain)
            tokens.append(used)
    return {"passages": passages, "domains": domains, "tokens": tokens}


# ------------------------------------------------------------------------- Q2
def ollama_dataset(email: str, version: str = "") -> dict[str, Any]:
    """The 50 shuffled corpus sentences and the 10 queries shown in the exam."""
    spec = exam_data()["ollama"]
    rng = SeedRandom(f"{spec['salt']}#{_norm_email(email)}#{version}")
    pool: list[dict[str, Any]] = []
    for index, domain in enumerate(spec["domains"]):
        order = [0, 1, 2, 3, 4, 5]
        for i in range(len(order) - 1, 0, -1):
            j = int(rng() * (i + 1))
            order[i], order[j] = order[j], order[i]
        for pick in order[:5]:
            pool.append({"domain": index, "text": domain["sentences"][pick]})
    for i in range(len(pool) - 1, 0, -1):
        j = int(rng() * (i + 1))
        pool[i], pool[j] = pool[j], pool[i]
    return {"sentences": [p["text"] for p in pool], "queries": [d["query"] for d in spec["domains"]],
            "sentenceDomains": [p["domain"] for p in pool]}
