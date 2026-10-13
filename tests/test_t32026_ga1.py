from __future__ import annotations

import hashlib
import asyncio
import tempfile
from pathlib import Path

from T32026.GA1.shared import tenant
from T32026.GA1.main import _quiz_sign_from_question_data_url
import httpx
from fastapi.testclient import TestClient
from T32026.GA1 import main
from T32026.GA1.app import app
from T32026.GA1.solvers import answer_ledger_question, assigned_config, challenge_digest, effective_config


def test_config_cli_precedence_alias_types_and_masking():
    config = effective_config([
        "port=8123", "workers=2", "num_workers=7", "debug=yes",
        "log_level=warning", "api_key=not-a-secret", "unknown=ignored", "port=9001",
    ])
    assert config == {"port": 9001, "workers": 7, "debug": True, "log_level": "warning", "api_key": "****"}
    assert effective_config(["debug=off", "workers=not-int"]) == {
        "port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "****"
    }


def test_mcp_digest_matches_sha256_and_normalizes_email():
    challenge = "0123456789abcdef0123456789abcdef"
    expected = hashlib.sha256(f"{challenge}:student@example.com".encode()).hexdigest()[:16]
    assert challenge_digest(challenge, " Student@Example.com ") == expected


def test_question_data_url_onboarding_extracts_signature_and_validates_tenant():
    url = (
        "https://exam.sanand.workers.dev/questionData?"
        "email=student%40example.com&quizSign=a%2Bb%2Fc%3D&"
        "questionId=q-ledger-agent-server&path=%2F"
    )
    assert _quiz_sign_from_question_data_url(url, "student@example.com") == "a+b/c="
    assert _quiz_sign_from_question_data_url(url, "other@example.com") is None
    assert _quiz_sign_from_question_data_url(url.replace("q-ledger-agent-server", "q-other"), "student@example.com") is None
    assert _quiz_sign_from_question_data_url(url.replace("exam.sanand.workers.dev", "evil.example"), "student@example.com") is None
    assert _quiz_sign_from_question_data_url(url + "&quizSign=second", "student@example.com") is None


def test_config_grader_regression_preserves_student_layers():
    email = "23f1000805@ds.study.iitm.ac.in"
    assert assigned_config(email) == {
        "port": 8172, "workers": 1, "debug": False, "log_level": "error", "api_key": "****"
    }
    with TestClient(app) as client:
        r = client.get(f"/{email}/effective-config?set=log_level=debug&set=workers=11")
        assert r.status_code == 200
        assert r.json() == {"port": 8172, "workers": 11, "debug": False, "log_level": "debug", "api_key": "****"}
        assert client.get("/effective-config").status_code == 400


def test_ledger_upstream_failure_is_diagnosable_without_leaking_signature(monkeypatch):
    client_type = httpx.AsyncClient
    transport = httpx.MockTransport(lambda request: httpx.Response(403, json={"error": "denied"}))
    monkeypatch.setattr(main, "get_config", lambda email: {"quiz_sign": "sentinel-private-signature"})
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: client_type(**{**kwargs, "transport": transport}))
    main._LEDGER_CACHE.clear()
    with TestClient(app) as client:
        r = client.post("/student@example.com/ledger/answer", json={"question": "Total revenue in East in March 2026?"})
    assert r.status_code == 502
    assert r.json()["upstream_status"] == 403
    assert "sentinel-private-signature" not in r.text


def test_onboarding_does_not_replace_tenant_with_rejected_signature(monkeypatch):
    client_type = httpx.AsyncClient
    transport = httpx.MockTransport(lambda request: httpx.Response(403))
    saved = []
    monkeypatch.setattr(main, "set_config", lambda *args: saved.append(args))
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: client_type(**{**kwargs, "transport": transport}))
    with TestClient(app) as client:
        r = client.post("/onboard", json={
            "email": "student@example.com",
            "question_data_url": "https://exam.sanand.workers.dev/questionData?email=student%40example.com&quizSign=private-sentinel&questionId=q-ledger-agent-server&path=/",
        })
    assert r.status_code == 502
    assert r.json()["upstream_status"] == 403
    assert "private-sentinel" not in r.text
    assert not saved


def test_simultaneous_ledger_questions_share_discovery(monkeypatch):
    client_type = httpx.AsyncClient
    requests = []

    async def upstream(request):
        requests.append(request.url.params.get("path"))
        await asyncio.sleep(0.01)
        if request.url.params.get("path") == "/":
            return httpx.Response(200, json={"orders": [{"id": "o1", "region": "East", "date": "2026-03-01", "total": 25}]})
        return httpx.Response(404)

    monkeypatch.setattr(main, "get_config", lambda email: {"quiz_sign": "test-signature"})
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: client_type(**{**kwargs, "transport": httpx.MockTransport(upstream)}))
    main._LEDGER_CACHE.clear()

    async def run():
        results = await asyncio.gather(*(main._ledger_resources("student@example.com") for _ in range(12)))
        assert all(error is None for data, error in results)
        assert all(answer_ledger_question("Total revenue in East in March 2026?", data) == 25 for data, error in results)

    asyncio.run(run())
    assert requests.count("/") == 1
    assert not main._LEDGER_INFLIGHT


def test_named_links_and_next_pages_are_discovered_without_signed_url_leaks(monkeypatch):
    client_type = httpx.AsyncClient
    payloads = {
        "/": {"links": {"orders": "/orders?page=1", "rates": "/rates", "export": "/export.csv"}},
        "/orders?page=1": {"orders": [{"id": "1", "region": "North", "date": "2026-05-01", "total": 25}],
                           "links": {"next": "https://exam.sanand.workers.dev/questionData?quizSign=private-sentinel&path=%2Forders%3Fpage%3D2"}},
        "/orders?page=2": {"orders": [{"id": "2", "region": "North", "date": "2026-05-02", "total": 35}]},
        "/rates": {"rates": {"USD": 1}},
    }

    def upstream(request):
        path = request.url.params.get("path")
        if "page" in request.url.params:
            path += "?page=" + request.url.params["page"]
        if path == "/export.csv":
            return httpx.Response(200, text="id,region,date,total\n1,North,2026-05-01,25\n2,North,2026-05-02,35\n", headers={"content-type": "text/csv"})
        return httpx.Response(200, json=payloads[path]) if path in payloads else httpx.Response(404)

    monkeypatch.setattr(main, "get_config", lambda email: {"quiz_sign": "test-signature"})
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: client_type(**{**kwargs, "transport": httpx.MockTransport(upstream)}))
    main._LEDGER_CACHE.clear()
    data, error = asyncio.run(main._ledger_resources("student@example.com"))
    assert error is None
    assert "/orders?page=2" in data
    assert "/export.csv" in data
    assert "private-sentinel" not in str(main._resource_manifest(data))
    assert answer_ledger_question("How much did North earn in May 2026, in US dollars?", data) == 60


def test_ledger_revenue_uses_order_rows_not_nested_line_items_and_no_filter_fallback():
    data = {"/": {"orders": [
        {"id": "o1", "date": "2026-03-04", "region": "North", "total": 100,
         "items": [{"product": "Fan", "quantity": 2, "price": 50}]},
        {"id": "o2", "date": "2026-04-04", "region": "South", "total": 200,
         "items": [{"product": "Lamp", "quantity": 4, "price": 50}]},
    ]}}
    assert answer_ledger_question("What was total revenue in the North region in March 2026?", data) == 100
    assert answer_ledger_question("What was total revenue in the North region in May 2026?", data) == 0


def test_ledger_refunds_products_and_customers():
    data = {
        "/refunds": {"refunds": [
            {"refund_id": "r1", "refund_amount": -12.5, "date": "2026-03-01", "region": "North"},
            {"refund_id": "r2", "refund_amount": 4, "date": "2026-03-02", "region": "North"},
        ]},
        "/orders": {"orders": [
            {"id": "1", "customer": "A", "items": [{"product": "Fan"}, {"product": "Fan"}]},
            {"id": "2", "customer": "B", "items": [{"product": "Lamp"}]},
        ]},
    }
    assert answer_ledger_question("How much was refunded in North in March 2026?", data) == 16.5
    assert answer_ledger_question("How many unique customers?", data) == 2
    assert answer_ledger_question("Which product sold the most?", data) == "Fan"


def test_refunded_order_count_is_not_refund_amount():
    data = {"/refunds": {"refunds": [
        {"refund_id": "r1", "order_id": "o1", "amount": 25, "region": "North", "date": "2026-04-02"},
        {"refund_id": "r2", "order_id": "o1", "amount": 10, "region": "North", "date": "2026-04-03"},
        {"refund_id": "r3", "order_id": "o2", "amount": 45, "region": "North", "date": "2026-04-04"},
        {"refund_id": "r4", "order_id": "o3", "amount": 30, "region": "East", "date": "2026-04-04"},
    ]}}
    assert answer_ledger_question("How many orders from North were refunded in April 2026?", data) == 2


def test_acme_revisions_kolkata_dates_paid_status_and_usd_rates():
    def order(id, **kwargs):
        return {"id": id, "customer": "C1", "region": "North", "product": "Mixer", "qty": 2,
                "amount": 100, "currency": "EUR", "status": "paid",
                "created_at": "2026-04-30T20:00:00Z", "updated_at": "2026-05-02T00:00:00Z", **kwargs}
    data = {
        "/export": {"orders": [
            order("o1", status="void", updated_at="2026-05-01T00:00:00Z"), order("o1"),
            order("o2", status="refunded", currency="USD", amount=25),
            order("o3", product="Fan", qty=5, amount=1000, currency="INR", customer="C2"),
            order("o4", status="void", amount=9999),
        ]},
        "/rates": {"usd_per_unit": {"USD": 1, "EUR": 1.13, "INR": 0.01216}},
    }
    assert answer_ledger_question("How much did North earn in May 2026, in US dollars?", data) == 125.16
    assert answer_ledger_question("Total revenue in North in April 2026?", data) == 0
    assert answer_ledger_question("How many orders from North were refunded in May 2026?", data) == 1
    assert answer_ledger_question("How much was refunded in North in May 2026 in USD?", data) == 25
    assert answer_ledger_question("Which product sold the most units in North in May 2026?", data) == "Fan"
    assert answer_ledger_question("Which product earned the most revenue in North in May 2026?", data) == "Mixer"
    assert answer_ledger_question("How many unique paying customers in North in May 2026?", data) == 2


def test_acme_bulk_ndjson_skips_the_85_page_chain(monkeypatch):
    client_type = httpx.AsyncClient
    visited = []
    row = {"id": "o1", "customer": "C1", "region": "North", "product": "Mixer", "qty": 1,
           "amount": 100, "currency": "EUR", "status": "paid",
           "created_at": "2026-05-01T00:00:00Z", "updated_at": "2026-05-02T00:00:00Z"}

    def upstream(request):
        path = request.url.params["path"]
        visited.append(path)
        if path == "/":
            return httpx.Response(200, json={"links": {
                "orders": "https://exam.sanand.workers.dev/questionData?path=%2Forders&page=1&quizSign=private-sentinel",
                "rates": "/rates", "export": "/export"}})
        if path == "/orders":
            assert request.url.params["page"] == "1"
            return httpx.Response(200, json={"page": 1, "pages": 85, "orders": [row], "next": "/orders?page=2"})
        if path == "/rates":
            return httpx.Response(200, json={"usd_per_unit": {"EUR": 1.13}})
        if path == "/export":
            import json
            return httpx.Response(200, text=json.dumps(row) + "\n", headers={"content-type": "application/x-ndjson"})
        return httpx.Response(404)

    monkeypatch.setattr(main, "get_config", lambda email: {"quiz_sign": "test-signature"})
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: client_type(**{**kwargs, "transport": httpx.MockTransport(upstream)}))
    main._LEDGER_CACHE.clear()
    data, error = asyncio.run(main._ledger_resources("student@example.com"))
    assert error is None
    assert visited.count("/orders") == 1
    assert answer_ledger_question("How much did North earn in May 2026, in US dollars?", data) == 113


def test_named_product_filters_apply_before_distinct_customer_count():
    def order(id, customer, product, **kwargs):
        return {"id": id, "customer": customer, "region": "North", "product": product, "qty": 1,
                "amount": 100, "currency": "USD", "status": "paid",
                "created_at": "2026-05-02T00:00:00Z", "updated_at": "2026-05-03T00:00:00Z", **kwargs}
    data = {"/export": {"orders": [
        order("1", "A", "Juicer", qty=3), order("2", "A", "Juicer"), order("3", "B", "Juicer"),
        order("4", "C", "Mixer"), order("5", "D", "Juicer"),
        order("5", "D", "Juicer", status="void", updated_at="2026-05-04T00:00:00Z"),
        order("6", "E", "Juicer", region="East"), order("7", "A", "Mixer"),
    ]}}
    assert answer_ledger_question("How many distinct customers have bought a Juicer (paid orders only)?", data) == 3
    assert answer_ledger_question("How many unique customers bought the product Juicer in North in May 2026?", data) == 2
    assert answer_ledger_question("How many distinct buyers purchased Juicers in North in May 2026?", data) == 2
    assert answer_ledger_question("How many distinct customers bought both a Juicer and a Mixer?", data) == 1
    assert answer_ledger_question("How many distinct customers bought a Juicer in North in April 2026?", data) == 0
    assert answer_ledger_question("Total revenue in North in May 2026 from Juicer in USD?", data) == 300
    assert answer_ledger_question("How many paid orders for Juicer in North in May 2026?", data) == 3
    assert answer_ledger_question("How many Juicers sold in North in May 2026 (paid orders only)?", data) == 5


def test_tenant_store_atomic_merge_and_normalized_key(monkeypatch):
    monkeypatch.delenv("GA1_REDIS_URL", raising=False)
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
        monkeypatch.setenv("GA1_TENANT_DB_PATH", str(Path(folder) / "tenant.sqlite3"))
        tenant.set_config(" Student@Example.com ", {"quiz_sign": "first"})
        tenant.set_config("student@example.com", {"other": "kept"})
        assert tenant.get_config("STUDENT@example.com") == {"quiz_sign": "first", "other": "kept"}


def _acme(id, **kwargs):
    return {"id": id, "customer": "C1001", "region": "North", "product": "Rice Cooker", "qty": 1,
            "unit_price": 100, "amount": 100, "currency": "USD", "status": "paid",
            "created_at": "2026-03-10T10:00:00Z", "updated_at": "2026-03-11T10:00:00Z", **kwargs}


def test_acme_engine_revisions_compare_instants_across_offsets_and_ist_month_edges():
    data = {"/export": {"orders": [
        # Same instant family: +05:30 revision is LATER than the Z row, so it wins.
        _acme("o1", qty=2, amount=200, updated_at="2026-03-12T17:20:39.648Z"),
        _acme("o1", qty=1, amount=100, updated_at="2026-03-17T06:04:32.758+05:30"),
        # 2026-03-31T20:00Z is 1 April in Asia/Kolkata.
        _acme("o2", created_at="2026-03-31T20:00:00Z", amount=50),
        # 2025-12-31T21:00Z is 1 January 2026 in Asia/Kolkata.
        _acme("o3", created_at="2025-12-31T21:00:00Z", amount=7, currency="EUR"),
        _acme("o4", status="refunded", amount=30, product="Air Fryer", region="West"),
    ]}, "/rates": {"usd_per_unit": {"USD": 1, "EUR": 1.13}}}
    assert answer_ledger_question("What was the total revenue in USD from the North region in March 2026?", data) == 100
    assert answer_ledger_question("Revenue in April 2026?", data) == 50
    assert answer_ledger_question("How much revenue did we make in January 2026 from EUR orders?", data) == 7.91
    assert answer_ledger_question("How many air fryers were refunded?", data) == 1
    assert answer_ledger_question("What was the total refund amount in USD for the West?", data) == 30
    assert answer_ledger_question("Which product generated the most revenue in Q1 2026?", data) == "Rice Cooker"
    assert answer_ledger_question("Which customer spent the most?", data) == "C1001"


def test_stateless_ledger_key_round_trips_and_routes_through_gateway(monkeypatch):
    from hf_space.app import app as gateway

    sign = "lJj+qL/cGw=="
    assert main.decode_ledger_key(main.encode_ledger_key(sign)) == sign
    assert main.decode_ledger_key("bad key!") is None
    seen = []

    def upstream(request):
        seen.append(request.url.params.get("quizSign"))
        path = request.url.params["path"]
        if path == "/":
            return httpx.Response(200, json={"links": {"export": "/export"}})
        if path == "/export":
            import json
            return httpx.Response(200, text=json.dumps(_acme("o1")) + "\n", headers={"content-type": "application/x-ndjson"})
        return httpx.Response(404)

    client_type = httpx.AsyncClient
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: client_type(**{**kwargs, "transport": httpx.MockTransport(upstream)}))
    monkeypatch.setattr(main, "get_config", lambda email: (_ for _ in ()).throw(AssertionError("store must not be needed")))
    main._LEDGER_CACHE.clear()
    with TestClient(gateway) as client:
        key = main.encode_ledger_key(sign)
        r = client.post(f"/ga1/student%40example.com/ledger/{key}/answer", json={"question": "Total revenue in March 2026?"})
        assert r.status_code == 200, r.text
        assert r.json() == {"answer": 100.0}
        # Unknown GA1 segments must not crash the gateway (previously NameError -> 500).
        assert client.post("/ga1/student%40example.com/not-a-route", json={}).status_code in (404, 405)
    assert set(seen) == {sign}
