"""Smoke tests for the GA5 agent-safety/infra hub, mounted at /ga5/{email}/...

Covers the 5 GA5 questions implemented as live endpoints: Q2 (proration), Q3
(pre-tool-call guardrail), Q4 (skill safety audit), Q5 (budget/loop guard),
Q6 (MCP server). All are deterministic and seeded per-student email except Q4,
which optionally upgrades to an LLM pass with a caller-supplied AIPipe token.
"""

from fastapi.testclient import TestClient

from hf_space.app import app

client = TestClient(app)
EMAIL = "23f1000805@ds.study.iitm.ac.in"
BASE = f"/ga5/{EMAIL}"


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
    assert len(r.json()["ready_routes"]) == 5


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


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
