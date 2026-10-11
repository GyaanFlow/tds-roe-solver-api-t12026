from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path

from T32026.GA1.shared import tenant
from T32026.GA1.solvers import answer_ledger_question, challenge_digest, effective_config


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


def test_tenant_store_atomic_merge_and_normalized_key(monkeypatch):
    monkeypatch.delenv("GA1_REDIS_URL", raising=False)
    with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
        monkeypatch.setenv("GA1_TENANT_DB_PATH", str(Path(folder) / "tenant.sqlite3"))
        tenant.set_config(" Student@Example.com ", {"quiz_sign": "first"})
        tenant.set_config("student@example.com", {"other": "kept"})
        assert tenant.get_config("STUDENT@example.com") == {"quiz_sign": "first", "other": "kept"}
