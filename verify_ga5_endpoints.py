"""Smoke tests for the GA5 agent-safety/infra hub, mounted at /ga5/{email}/...

Covers the GA5 questions implemented as live endpoints: Q2 (proration), Q3
(pre-tool-call guardrail), Q4 (skill safety audit), Q5 (budget/loop guard),
Q6 (MCP server), Q8 (guardrail red-team, real execution), Q9 (durable mailroom
action gate), Q10 (A2A invoice agent). All are deterministic and seeded
per-student email except Q4, Q9, Q10, which call an LLM using a caller-supplied
AIPipe token (Q9/Q10's triage is mocked here to keep the suite network-free).
"""

from urllib.parse import quote

from fastapi.testclient import TestClient

import T22026.GA5.a2a_agent as a2a_agent
import T22026.GA5.mailroom as mailroom
from hf_space.app import app

client = TestClient(app)
EMAIL = "23f1000805@ds.study.iitm.ac.in"
BASE = f"/ga5/{EMAIL}"


async def _fake_triage(dossier, token):
    call_id = mailroom.call_id_for(dossier["dossierId"], mailroom.dossier_fingerprint(dossier))
    return {
        "dossierId": dossier["dossierId"], "callId": call_id, "action": "no_action",
        "target": None, "payload": {"reasonCode": "INFORMATIONAL", "referenceId": dossier["dossierId"]},
        "evidence": [],
    }


mailroom.triage_dossier_llm = _fake_triage  # module-level patch: main.py calls mailroom.propose -> mailroom.triage_dossier_llm


async def _fake_invoice_triage(package, token):
    return {
        "action": "settle_invoice",
        "facts": {"vendorName": "Acme", "invoiceNumber": package.get("packageId", "P"), "amountMinor": 1000, "currency": "INR"},
        "evidenceRefs": ["L1"],
        "rationale": "Invoice matches the purchase order and is within the standard autonomous settlement threshold for this vendor.",
    }


a2a_agent.triage_package_llm = _fake_invoice_triage  # module-level patch: main.py calls a2a_agent.message_send -> ...triage_package_llm


def test_health():
    r = client.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_onboard_and_status():
    r = client.post("/ga5/onboard", json={"email": EMAIL})
    assert r.status_code == 200
    assert r.json()["configured"] is True

    r = client.get(f"{BASE}/status")
    assert r.status_code == 200
    assert len(r.json()["ready_routes"]) == 7


def test_q2_proration():
    r = client.post(f"{BASE}/proration", json={
        "old_price": 10, "new_price": 20, "days_remaining": 15,
        "days_in_actual_month": 30, "spec": "v1",
    })
    assert r.status_code == 200
    assert r.json()["charge"] == 5.0

    r = client.post(f"{BASE}/proration", json={
        "old_price": 10, "new_price": 20, "days_remaining": 15,
        "days_in_actual_month": 28, "spec": "v2",
    })
    assert r.status_code == 200
    assert abs(r.json()["charge"] - (10 * 15 / 28)) < 0.001


def test_q3_guardrail_seeded_per_email():
    from T22026.GA5.seedgen import derive_q3_policy
    policy = derive_q3_policy(EMAIL)

    # direct read of the seeded secret -> block
    r = client.post(f"{BASE}/guardrail", json={"tool": "bash", "command": f"cat {policy['secret_file']}"})
    assert r.json()["decision"] == "block"

    # tilde-expansion bypass -> still blocked
    r = client.post(f"{BASE}/guardrail", json={"tool": "bash", "command": f"cat ~/{policy['secret_rel']}"})
    assert r.json()["decision"] == "block"

    # unrelated read -> allowed
    r = client.post(f"{BASE}/guardrail", json={"tool": "bash", "command": "cat /var/log/syslog"})
    assert r.json()["decision"] == "allow"

    # write inside allowed dir -> allowed; traversal escape -> blocked
    r = client.post(f"{BASE}/guardrail", json={"tool": "write_file", "path": policy["write_dir"] + "out.txt", "content": "x"})
    assert r.json()["decision"] == "allow"
    r = client.post(f"{BASE}/guardrail", json={"tool": "write_file", "path": policy["write_dir"] + "../../etc/passwd", "content": "x"})
    assert r.json()["decision"] == "block"

    # allowed host vs domain-confusion
    r = client.post(f"{BASE}/guardrail", json={"tool": "http_request", "method": "GET", "url": f"https://{policy['allowed_domains'][0]}/x"})
    assert r.json()["decision"] == "allow"
    r = client.post(f"{BASE}/guardrail", json={"tool": "http_request", "method": "GET", "url": f"https://{policy['allowed_domains'][0]}.attacker-relay.net/x"})
    assert r.json()["decision"] == "block"

    # different email -> different seeded secret (isolation)
    other_policy = derive_q3_policy("someone.else@ds.study.iitm.ac.in")
    assert other_policy["secret_file"] != policy["secret_file"] or other_policy["allowed_domains"] != policy["allowed_domains"]


def test_q4_skill_scan():
    skill = "---\nname: notes-digest\n---\n\nUse api_key: sk-abc123def456ghijk to call the summarizer."
    r = client.post(f"{BASE}/skill-scan", json={"skill": skill})
    assert r.status_code == 200
    categories = r.json()["categories"]
    assert "hardcoded_secret" in categories
    assert "unclear_provenance" in categories

    # a clean, well-attributed file should get zero categories
    clean = "---\nname: echo\nauthor: dev\nversion: 1.0.0\n---\n\nEcho the input text back unchanged."
    r2 = client.post(f"{BASE}/skill-scan", json={"skill": clean})
    assert r2.json()["categories"] == []


def test_q5_budget_and_loop_guard():
    from T22026.GA5.seedgen import derive_q5_policy
    policy = derive_q5_policy(EMAIL)

    # budget exhausted -> halt
    r = client.post(f"{BASE}/budget-guard", json={
        "budget_tokens": 20000,
        "steps": [
            {"step_number": 1, "tool": "fetch_page", "args": {"url": "https://example.com/1"}, "tokens_used": 9000},
            {"step_number": 2, "tool": "summarize", "args": {"text": "..."}, "tokens_used": 7000},
            {"step_number": 3, "tool": "fetch_page", "args": {"url": "https://example.com/2"}, "tokens_used": 5000},
        ],
    })
    assert r.json()["decision"] == "halt"

    # legitimate pagination -> continue
    r = client.post(f"{BASE}/budget-guard", json={
        "budget_tokens": 20000,
        "steps": [
            {"step_number": 1, "tool": "list_items", "args": {"page": 1}, "tokens_used": 1000},
            {"step_number": 2, "tool": "list_items", "args": {"page": 2}, "tokens_used": 1000},
            {"step_number": 3, "tool": "list_items", "args": {"page": 3}, "tokens_used": 1000},
        ],
    })
    assert r.json()["decision"] == "continue"

    # 3x identical repeat (ignoring the seeded tracing field) -> halt
    r = client.post(f"{BASE}/budget-guard", json={
        "budget_tokens": 50000,
        "steps": [
            {"step_number": i, "tool": "query_db", "args": {"query": "x", policy["irrelevant_field"]: f"trace-{i}"}, "tokens_used": 100}
            for i in range(1, 4)
        ],
    })
    assert r.json()["decision"] == "halt"

    # only 2 repeats -> must NOT halt
    r = client.post(f"{BASE}/budget-guard", json={
        "budget_tokens": 50000,
        "steps": [
            {"step_number": i, "tool": "query_db", "args": {"query": "x"}, "tokens_used": 100}
            for i in range(1, 3)
        ],
    })
    assert r.json()["decision"] == "continue"


def test_q6_mcp_server():
    r = client.post(f"{BASE}/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert r.status_code == 200
    assert r.json()["result"]["capabilities"] == {"tools": {}}

    r = client.post(f"{BASE}/mcp", json={"jsonrpc": "2.0", "method": "notifications/initialized"})
    assert r.status_code == 202

    r = client.post(f"{BASE}/mcp", json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
    tools = r.json()["result"]["tools"]
    assert any(t["name"] == "solve_challenge" for t in tools)
    assert tools[0]["inputSchema"]["required"] == []

    challenge = "0123456789abcdef0123456789abcdef"
    r = client.post(
        f"{BASE}/mcp",
        json={"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "solve_challenge", "arguments": {}}},
        headers={"X-Exam-Challenge": challenge},
    )
    text = r.json()["result"]["content"][0]["text"]
    import hashlib
    expected = hashlib.sha256(f"{challenge}:{EMAIL}".encode()).hexdigest()[:16]
    assert text == expected
    assert len(text) == 16


def test_q8_guardrail_redteam_executes_real_calls():
    from T22026.GA5.seedgen import derive_q8_scenario
    scenario = derive_q8_scenario(EMAIL)

    # in-sandbox read actually returns the seeded file content
    r = client.post(f"{BASE}/guardrail-redteam", json={
        "tool": "read_file", "arguments": {"path": scenario["sandbox_root"] + "/notes/report.txt"},
    })
    assert r.status_code == 200
    assert r.json() == {"action": "allow", "reason": "Path is inside the sandbox.", "result": scenario["safe_report_token"]}

    # filename that merely looks like a traversal but is a safe literal name -> allowed
    r = client.post(f"{BASE}/guardrail-redteam", json={
        "tool": "read_file", "arguments": {"path": scenario["sandbox_root"] + "/notes/looks-like-..-but-safe.txt"},
    })
    assert r.json()["result"] == scenario["safe_weird_token"]

    # literal %2e%2e in a filename must not be decoded as traversal
    r = client.post(f"{BASE}/guardrail-redteam", json={
        "tool": "read_file", "arguments": {"path": scenario["sandbox_root"] + "/encoded/%2e%2e-literal.txt"},
    })
    assert r.json()["result"] == scenario["safe_encoded_token"]

    # the canary, outside the sandbox, must never be readable -- and never leaked
    r = client.post(f"{BASE}/guardrail-redteam", json={"tool": "read_file", "arguments": {"path": scenario["canary_path"]}})
    assert r.json()["action"] == "block"
    assert scenario["canary_token"] not in r.text

    # traversal escape from inside the sandbox to the canary must also block
    outside_name = scenario["outside_dir"].rsplit("/", 1)[-1]
    r = client.post(f"{BASE}/guardrail-redteam", json={
        "tool": "read_file", "arguments": {"path": scenario["sandbox_root"] + f"/../{outside_name}/canary.txt"},
    })
    assert r.json()["action"] == "block"

    # arbitrary unrelated path is blocked (only the sandbox is readable at all)
    r = client.post(f"{BASE}/guardrail-redteam", json={"tool": "read_file", "arguments": {"path": "/etc/passwd"}})
    assert r.json()["action"] == "block"

    # fetch_url: disallowed host, userinfo confusion, and loopback are all blocked
    r = client.post(f"{BASE}/guardrail-redteam", json={"tool": "fetch_url", "arguments": {"url": "https://evil.example.org/"}})
    assert r.json()["action"] == "block"
    r = client.post(f"{BASE}/guardrail-redteam", json={"tool": "fetch_url", "arguments": {"url": "https://example.com@evil.example.org/"}})
    assert r.json()["action"] == "block"
    r = client.post(f"{BASE}/guardrail-redteam", json={"tool": "fetch_url", "arguments": {"url": "http://127.0.0.1/"}})
    assert r.json()["action"] == "block"


def _mailroom_dossier(dossier_id: str) -> dict:
    return {
        "dossierId": dossier_id, "partition": "stable_core", "receivedAt": "2026-01-01T00:00:00Z",
        "mailbox": "support@example.com", "objective": "test",
        "sources": [{"sourceId": "S1", "kind": "email", "provenance": "customer", "title": "t",
                     "lines": [{"lineId": "L1", "text": "hello"}]}],
    }


def test_q9_mailroom_propose_commit_lifecycle():
    mailroom.MailroomStore(EMAIL).path.unlink(missing_ok=True)
    token_base = f"/ga5/{EMAIL}/faketoken"
    eval_id = "TEST_EVAL_" + EMAIL

    propose_body = {
        "profile": mailroom.PROFILE, "operation": "propose", "evaluationId": eval_id,
        "corpus": {"coreId": "c", "auditId": "a", "stableCount": 1, "freshCount": 0},
        "allowedActions": list(mailroom.ALLOWED_ACTIONS),
        "dossiers": [_mailroom_dossier("MD1")],
    }

    # no token -> clean 400, not a crash
    r = client.post(f"/ga5/{EMAIL}/mailroom", json={**propose_body, "evaluationId": eval_id + "-notoken"})
    assert r.status_code == 400

    # propose with token -> one proposal, valid schema
    r1 = client.post(f"{token_base}/mailroom", json=propose_body)
    assert r1.status_code == 200, r1.text
    body1 = r1.json()
    assert body1["status"] == "awaiting_receipts"
    assert len(body1["proposals"]) == 1
    proposal = body1["proposals"][0]
    ok, reason = mailroom.validate_proposal_shape(proposal["action"], proposal["target"], proposal["payload"])
    assert ok, reason

    # exact replay -> byte-identical, no re-run
    r2 = client.post(f"{token_base}/mailroom", json=propose_body)
    assert r2.json() == body1

    # same evaluationId, different content -> 409
    r3 = client.post(f"{token_base}/mailroom", json={**propose_body, "dossiers": [_mailroom_dossier("MD2")]})
    assert r3.status_code == 409

    # commit with a valid receipt -> executed
    receipt = {
        "dossierId": proposal["dossierId"], "callId": proposal["callId"], "action": proposal["action"],
        "accepted": True, "proposalDigest": mailroom.compute_proposal_digest(proposal), "receiptId": "R1",
    }
    commit_body = {"profile": mailroom.PROFILE, "operation": "commit", "evaluationId": eval_id,
                   "inputDigest": body1["inputDigest"], "receipts": [receipt]}
    r4 = client.post(f"{token_base}/mailroom", json=commit_body)
    assert r4.status_code == 200
    assert r4.json()["outcomes"][0]["status"] == "executed"

    # commit replay -> identical
    r5 = client.post(f"{token_base}/mailroom", json=commit_body)
    assert r5.json() == r4.json()

    # tampered receipt after a legitimate commit -> rejected as a conflict
    tampered = {**receipt, "proposalDigest": "deadbeef"}
    r6 = client.post(f"{token_base}/mailroom", json={**commit_body, "receipts": [tampered]})
    assert r6.status_code == 409

    # unknown evaluationId on commit -> 404
    r7 = client.post(f"{token_base}/mailroom", json={**commit_body, "evaluationId": "NEVER_PROPOSED"})
    assert r7.status_code == 404

    # malformed operation -> 400
    r8 = client.post(f"{token_base}/mailroom", json={"profile": mailroom.PROFILE, "operation": "bogus"})
    assert r8.status_code == 400


def test_q10_agent_card_is_origin_level_and_accumulates_bases():
    email, token = "a2a-test@x.com", "a2atoken1"
    r = client.post("/ga5/onboard", json={"email": email, "aipipe_token": token})
    assert r.status_code == 200

    card = client.get("/.well-known/agent-card.json")
    assert card.status_code == 200
    body = card.json()
    assert body["name"] and body["description"] and body["version"]
    assert isinstance(body["capabilities"], dict)
    skill = body["skills"][0]
    assert skill["id"] == "invoice_action_agent" and skill["name"] and skill["description"] and skill["tags"]
    assert a2a_agent.PROFILE_INPUT_MODE in body["defaultInputModes"]
    assert a2a_agent.PROPOSALS_MODE in body["defaultOutputModes"] and a2a_agent.RECEIPTS_MODE in body["defaultOutputModes"]

    expected_base = f"http://testserver/ga5/{quote(email, safe='')}/{token}/a2a/"
    matches = [i for i in body["supportedInterfaces"] if i["url"] == expected_base]
    assert len(matches) == 1
    assert matches[0] == {"url": expected_base, "protocolBinding": "HTTP+JSON", "protocolVersion": "1.0"}


def test_q10_a2a_message_lifecycle_and_tenant_isolation():
    email, token = "a2a-lifecycle@x.com", "a2atoken2"
    principal = f"{email}:{token}"
    a2a_agent.A2AStore(principal).path.unlink(missing_ok=True)

    base = f"/ga5/{email}/{token}/a2a"
    headers = {"A2A-Version": "1.0", "Content-Type": "application/a2a+json", "Authorization": f"Bearer {token}"}

    # auth failures
    assert client.post(base + "/message:send", json={"message": {}}).status_code in (401, 403)
    assert client.post(base + "/message:send", json={"message": {}}, headers={**headers, "Authorization": "Bearer wrong"}).status_code == 403
    assert client.post(base + "/message:send", json={"message": {}}, headers={**headers, "A2A-Version": "9.9"}).status_code == 400

    initial_msg = {
        "messageId": "AM1", "role": "ROLE_USER",
        "parts": [{"mediaType": a2a_agent.PROFILE_INPUT_MODE, "data": {
            "batchId": "AB1", "policyRevision": "r1", "packages": [{"packageId": "AP1", "docs": ["invoice text"]}],
        }}],
    }
    r1 = client.post(base + "/message:send", json={"message": initial_msg}, headers=headers)
    assert r1.status_code == 200
    task = r1.json()["task"]
    assert task["state"] == "TASK_STATE_INPUT_REQUIRED"
    proposal = task["artifacts"][0]["parts"][0]["data"]["proposals"][0]

    # exact replay -> byte-identical
    r1b = client.post(base + "/message:send", json={"message": initial_msg}, headers=headers)
    assert r1b.json() == r1.json()

    # same messageId, different content -> 409 idempotency conflict
    tampered = {**initial_msg, "parts": [{"mediaType": a2a_agent.PROFILE_INPUT_MODE, "data": {"batchId": "AB1", "policyRevision": "r2", "packages": [{"packageId": "AP1", "docs": ["different"]}]}}]}
    r2 = client.post(base + "/message:send", json={"message": tampered}, headers=headers)
    assert r2.status_code == 409

    # continuation -> completed, with an execution for the accepted result
    cont_msg = {
        "messageId": "AM2", "taskId": task["id"], "contextId": task["contextId"], "role": "ROLE_USER",
        "parts": [{"mediaType": a2a_agent.PROFILE_RESULTS_MODE, "data": {"batchId": "AB1", "results": [
            {"packageId": "AP1", "actionId": proposal["actionId"], "action": "settle_invoice", "outcome": "ACCEPTED", "receiptNonce": "n1"},
        ]}}],
    }
    r3 = client.post(base + "/message:send", json={"message": cont_msg}, headers=headers)
    assert r3.status_code == 200
    task2 = r3.json()["task"]
    assert task2["state"] == "TASK_STATE_COMPLETED"
    executions = task2["artifacts"][1]["parts"][0]["data"]["executions"]
    assert len(executions) == 1 and executions[0]["actionId"] == proposal["actionId"]

    # get / list for the right principal
    assert client.get(base + f"/tasks/{task['id']}", headers=headers).json()["state"] == "TASK_STATE_COMPLETED"
    assert len(client.get(base + "/tasks", headers=headers).json()["tasks"]) == 1

    # cross-tenant isolation: a different email+token combo gets 404, not the task
    other_headers = {"A2A-Version": "1.0", "Authorization": "Bearer othertoken"}
    other = client.get(f"/ga5/nobody@x.com/othertoken/a2a/tasks/{task['id']}", headers=other_headers)
    assert other.status_code == 404

    # cancel on an already-terminal task is a no-op (never both COMPLETED and CANCELED)
    cancel = client.post(base + f"/tasks/{task['id']}:cancel", headers=headers)
    assert cancel.json()["state"] == "TASK_STATE_COMPLETED"


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
