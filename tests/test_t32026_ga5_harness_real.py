"""T3-2026 GA5 Q4: the 96 REAL grader cases captured on 2026-11-27.

The grader does not return per-case labels, so ``expected`` records the policy reading reviewed case by case
(see harness_structured.py). This file pins those decisions so later edits cannot silently change them, and
checks the cross-axis rules the policy states outright."""
import json
from pathlib import Path

import pytest

from T32026.GA5 import harness

ROWS = json.loads((Path(__file__).parent / "fixtures" / "t3ga5_harness_real_cases.json").read_text(encoding="utf-8"))


@pytest.mark.parametrize("i", range(len(ROWS)))
def test_real_case_decision_is_pinned(i):
    assert harness.decide_case(ROWS[i]["case"]) == ROWS[i]["expected"]


def test_policy_cross_axis_rules_on_real_cases():
    for row in ROWS:
        case, d = row["case"], harness.decide_case(row["case"])
        has_tool = bool(case.get("proposedTool"))
        assert (d["toolDecision"] == "none") == (not has_tool)
        if d["requestDecision"] == "block":
            assert d["route"] == "none" and d["toolDecision"] in ("block", "none") and d["trajectory"] == "intervene"
        if d["requestDecision"] == "review" and has_tool:
            assert d["toolDecision"] in ("review", "block")
        if "block" in (d["requestDecision"], d["toolDecision"]):
            assert d["trajectory"] == "intervene"
        elif "review" in (d["requestDecision"], d["toolDecision"]):
            assert d["trajectory"] == "watch"
        if any(tr.get("origin") == "untrusted" for tr in case.get("toolResults", [])):
            assert d["trajectory"] in ("watch", "intervene")  # untrusted content tried to redirect the session


def test_real_batch_envelope_round_trips():
    cases = [row["case"] for row in ROWS[:24]]
    out = harness.decide_batch({"profile": "agent-harness-2026-09", "batchId": "case_x/batch-0", "policy": {"profile": "agent-harness-2026-09"}, "cases": cases})
    assert out["profile"] == "agent-harness-2026-09" and out["batchId"] == "case_x/batch-0"
    assert sorted(r["caseId"] for r in out["results"]) == sorted(c["caseId"] for c in cases)
