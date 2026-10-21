import asyncio

from T22026.GA5 import incident_agent as ia


def _real_choose_effect():
    # verify_ga5_endpoints.py replaces ia.choose_effect with a fake at import time.
    return getattr(ia, "_real_choose_effect", ia.choose_effect)


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
    choose = _real_choose_effect()
    tools = ["scale_service", "page_owner"]
    catalog = [{"name": n, "inputSchema": {}} for n in tools]
    incident = {"service": "checkout", "transcript": "Load is high. checkout is already at its permitted scaling limit."}
    out = asyncio.run(choose("capacity saturation", tools, catalog, incident, "tok"))
    assert out["chosenEffect"] == "page_owner"
    incident["transcript"] = "Load is high. replicas 3/8."
    out = asyncio.run(choose("capacity saturation", tools, catalog, incident, "tok"))
    assert out["chosenEffect"] == "scale_service"


def test_pages_owner_when_model_unreachable(monkeypatch):
    async def broken_chat(*a, **k):
        raise RuntimeError("provider down")

    import T22026.GA4.solvers as solvers
    monkeypatch.setattr(solvers, "aipipe_chat", broken_chat)
    tools = ["scale_service", "page_owner"]
    catalog = [{"name": n, "inputSchema": {}} for n in tools]
    incident = {"service": "checkout", "transcript": "replicas 12/12, cpu saturated"}
    out = asyncio.run(_real_choose_effect()("traffic_capacity_exhaustion", tools, catalog, incident, "tok"))
    assert out["chosenEffect"] == "page_owner"
