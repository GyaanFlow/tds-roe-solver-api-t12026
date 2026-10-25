"""T3-2026 GA3 regressions for the shared GA5 agent servers (A2A, incidents, recorder)."""
import asyncio
import json
import uuid

import httpx
import pytest

from T22026.GA5 import a2a_agent, capture

EMAIL = "ga3.tester@example.com"
TOKEN = "tok_" + "a" * 24
BASE = f"/ga5/{EMAIL.replace('@', '%40')}/{TOKEN}/a2a"


def _headers(bearer="grader-principal-1"):
    return {"A2A-Version": "1.0", "Content-Type": "application/a2a+json", "Authorization": f"Bearer {bearer}"}


@pytest.fixture
def gateway(monkeypatch):
    async def fake_triage(package, token):
        return {"action": "settle_invoice",
                "facts": {"vendorName": "Acme", "invoiceNumber": "INV-1", "amountMinor": 100, "currency": "INR"},
                "evidenceRefs": ["r1", "r2", "r3"],
                "rationale": "settle_invoice because r1 and r2 show a reconciled invoice within authority, r3 confirms."}
    monkeypatch.setattr(a2a_agent, "triage_package_llm", fake_triage)
    monkeypatch.setattr(a2a_agent, "deterministic_package_triage", lambda pkg: None)
    from hf_space.app import app
    return app


def _initial(batch, message_id=None):
    return {"message": {"messageId": message_id or "m-" + uuid.uuid4().hex, "role": "ROLE_USER", "parts": [{
        "mediaType": "application/vnd.ga5.invoice-claim-batch+json",
        "data": {"batchId": batch, "policyRevision": "p1",
                 "packages": [{"packageId": f"{batch}-p{i}", "documents": [{"text": f"doc {i}"}]} for i in range(3)]}}]},
        "configuration": {"returnImmediately": False, "historyLength": 20}}


def _results(task, outcome="ACCEPTED"):
    proposals = task["artifacts"][0]["parts"][0]["data"]["proposals"]
    return {"message": {"messageId": "r-" + uuid.uuid4().hex, "taskId": task["id"], "contextId": task["contextId"],
                        "role": "ROLE_USER", "parts": [{"mediaType": "application/vnd.ga5.invoice-action-results+json",
                        "data": {"batchId": task["artifacts"][0]["parts"][0]["data"]["batchId"], "results": [
                            {"packageId": p["packageId"], "actionId": p["actionId"], "action": p["action"],
                             "outcome": outcome, "receiptNonce": uuid.uuid4().hex} for p in proposals]}}]}}


def test_replay_after_completion_returns_stored_terminal_task_and_cancel_is_a_bare_task(gateway):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway), base_url="https://h") as c:
            first = _initial("b-" + uuid.uuid4().hex[:8])
            r = await c.post(BASE + "/message:send", json=first, headers=_headers())
            assert r.status_code == 200 and r.headers["content-type"].startswith("application/a2a+json")
            task = r.json()["task"]
            assert task["status"]["state"] == "TASK_STATE_INPUT_REQUIRED"
            assert all(a.get("artifactId") for a in task["artifacts"])
            done = (await c.post(BASE + "/message:send", json=_results(task), headers=_headers())).json()["task"]
            assert done["status"]["state"] == "TASK_STATE_COMPLETED"
            # Replay of the ORIGINAL message, keys reordered and returnImmediately changed.
            replay = {"configuration": {"historyLength": 20, "returnImmediately": True}, "message": first["message"]}
            again = (await c.post(BASE + "/message:send", json=replay, headers=_headers())).json()["task"]
            assert again["status"]["state"] == "TASK_STATE_COMPLETED" and again == done
            # Cancel a terminal task -> 409; cancel a live one -> bare Task.
            assert (await c.post(BASE + f"/tasks/{task['id']}:cancel", headers=_headers())).status_code == 409
            live = (await c.post(BASE + "/message:send", json=_initial("b-" + uuid.uuid4().hex[:8]), headers=_headers())).json()["task"]
            r = await c.post(BASE + f"/tasks/{live['id']}:cancel", headers=_headers())
            assert r.status_code == 200 and "task" not in r.json()
            assert r.json()["id"] == live["id"] and r.json()["status"]["state"] == "TASK_STATE_CANCELED"
            # Rejected-only continuation after cancel must not also "win".
            assert (await c.post(BASE + "/message:send", json=_results(live, "REJECTED"), headers=_headers())).status_code == 409
    asyncio.run(run())


def test_cancel_versus_result_race_has_exactly_one_winner(gateway):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway), base_url="https://h") as c:
            for _ in range(6):
                task = (await c.post(BASE + "/message:send", json=_initial("race-" + uuid.uuid4().hex[:8]), headers=_headers())).json()["task"]
                result, cancel = await asyncio.gather(
                    c.post(BASE + "/message:send", json=_results(task), headers=_headers()),
                    c.post(BASE + f"/tasks/{task['id']}:cancel", headers=_headers()))
                assert sorted([result.status_code, cancel.status_code]) == [200, 409]
                final = (await c.get(BASE + f"/tasks/{task['id']}", headers=_headers())).json()
                receipts = [a for a in final["artifacts"] if "receipts" in a["parts"][0]["mediaType"]]
                if final["status"]["state"] == "TASK_STATE_COMPLETED":
                    assert result.status_code == 200 and len(receipts) == 1
                else:
                    assert final["status"]["state"] == "TASK_STATE_CANCELED" and cancel.status_code == 200 and not receipts
    asyncio.run(run())


def test_outsider_cannot_see_or_touch_tasks(gateway):
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=gateway), base_url="https://h") as c:
            task = (await c.post(BASE + "/message:send", json=_initial("iso-" + uuid.uuid4().hex[:8]), headers=_headers())).json()["task"]
            outsider = _headers("outsider-" + uuid.uuid4().hex)
            r = await c.get(BASE + f"/tasks/{task['id']}", headers=outsider)
            assert r.status_code in (403, 404) and task["id"] not in r.text
            assert (await c.post(BASE + f"/tasks/{task['id']}:cancel", headers=outsider)).status_code in (403, 404)
            assert (await c.get(BASE + "/tasks", headers=outsider)).json() == {"tasks": []}
    asyncio.run(run())


def test_recorder_redacts_and_is_private_to_the_tenant_url():
    email, token = "rec@example.com", "tok_" + uuid.uuid4().hex
    capture.clear(email, token)
    body = json.dumps({"runId": "r1", "sensitive": {"accessToken": "SECRET-ACCESS-123"},
                       "incident": {"transcript": "note SECRET-ACCESS-123 here"}}).encode()
    capture.record(email, token, "POST", f"/ga5/v2/incidents/{token}", {"authorization": "Bearer grader-xyz"},
                   body, 200, b'{"ok":true}', 0.1)
    rows = capture.read(email, token)
    assert len(rows) == 1
    dumped = json.dumps(rows)
    assert "SECRET-ACCESS-123" not in dumped and token not in dumped and "grader-xyz" not in dumped
    assert rows[0]["request"]["sensitive"] == "[REDACTED]"
    assert capture.read(email, "other-token") == []
    capture.clear(email, token)


def test_recorder_survives_unicode_line_separators():
    email, token = "rec2@example.com", "tok_" + uuid.uuid4().hex
    capture.clear(email, token)
    tricky = "a" + chr(0x2028) + "b" + chr(0x2029) + "c" + chr(0x85) + "d"
    capture.record(email, token, "POST", "/ga5/mailroom", {}, json.dumps({"t": tricky}, ensure_ascii=False).encode(), 200, b"{}", 0.0)
    capture.record(email, token, "POST", "/ga5/mailroom", {}, b'{"n":2}', 200, b"{}", 0.0)
    rows = capture.read(email, token)
    assert [r["request"].get("n") for r in rows] == [2, None] and rows[1]["request"]["t"] == tricky
    capture.clear(email, token)



def test_distributed_audit_packages_decide_from_relationships_not_order():
    """Fixtures mirror the fresh-audit layout (HypeMonk/TDS-GA5 regression cases).
    A ledger payment for a DIFFERENT order is not a duplicate; missing identities stay unknown."""
    from pathlib import Path
    cases = json.loads((Path(__file__).parent / "fixtures" / "t3ga3_a2a_distributed_cases.json").read_text(encoding="utf8"))
    for case in cases:
        pkg = case["package"]
        assert a2a_agent.deterministic_package_triage(pkg) is None  # our core decoder declines these
        got = a2a_agent.reference_rules_triage(pkg)
        assert got is not None and got["action"] == case["expected"], case["name"]
        assert len(got["evidenceRefs"]) == 3 and all(r.startswith("R_") for r in got["evidenceRefs"])
        assert set(got["facts"]) == {"vendorName", "invoiceNumber", "amountMinor", "currency"}
        assert 60 <= len(got["rationale"]) <= 1500 and got["action"] in got["rationale"]
        assert sum(r in got["rationale"] for r in got["evidenceRefs"]) >= 2
        shuffled = dict(pkg, documents=list(reversed(pkg["documents"])))
        assert a2a_agent.reference_rules_triage(shuffled) == got
    by_name = {c["name"]: c for c in cases}
    settle = a2a_agent.reference_rules_triage(by_name["settle_missing_invoice"]["package"])
    assert settle["facts"]["invoiceNumber"] == "unknown"
