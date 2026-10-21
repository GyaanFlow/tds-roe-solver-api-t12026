import asyncio

from T22026.GA5 import incident_agent as ia


def test_detects_scaling_limit_phrases():
    assert ia.at_scaling_limit("checkout is already at its permitted scaling limit")
    assert ia.at_scaling_limit("replicas 8/8")
    assert ia.at_scaling_limit("Cannot scale further")
    assert not ia.at_scaling_limit("replicas 3/8, cpu saturated")
    assert not ia.at_scaling_limit("replicas 8/88")
    assert not ia.at_scaling_limit(None, "")


def test_pages_owner_instead_of_scaling(monkeypatch):
    async def fake_chat(*a, **k):
        return '{"chosenEffect": "scale_service", "arguments": {}}'

    import T22026.GA4.solvers as solvers
    monkeypatch.setattr(solvers, "aipipe_chat", fake_chat)
    tools = ["scale_service", "page_owner"]
    catalog = [{"name": n, "inputSchema": {}} for n in tools]
    incident = {"service": "checkout", "transcript": "Load is high. checkout is already at its permitted scaling limit."}
    out = asyncio.run(ia.choose_effect("capacity saturation", tools, catalog, incident, "tok"))
    assert out["chosenEffect"] == "page_owner"
    incident["transcript"] = "Load is high. replicas 3/8."
    out = asyncio.run(ia.choose_effect("capacity saturation", tools, catalog, incident, "tok"))
    assert out["chosenEffect"] == "scale_service"
