from __future__ import annotations

import time
import pytest
from httpx import AsyncClient, ASGITransport
import jwt
from hf_space.app import app
from T22026.GA2.solvers import (
    OAUTH_PUBKEY,
    metrics_origin,
    oauth_seeds,
    stream_answer,
    docker_answer,
)

STUDENT = "23f1000805@ds.study.iitm.ac.in"


@pytest.mark.asyncio
async def test_q3_stats_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Preflight from assigned origin
        assigned = metrics_origin(STUDENT)
        res_opt = await client.options(
            f"/ga2/{STUDENT}/stats",
            headers={"Origin": assigned},
        )
        assert res_opt.status_code == 204
        assert res_opt.headers.get("access-control-allow-origin") == assigned

        # Preflight from evil origin -> 403
        res_opt_bad = await client.options(
            f"/ga2/{STUDENT}/stats",
            headers={"Origin": "https://evil.com"},
        )
        assert res_opt_bad.status_code == 403
        assert "access-control-allow-origin" not in res_opt_bad.headers

        # GET /stats with values
        res_get = await client.get(
            f"/ga2/{STUDENT}/stats?values=10,20,30,40",
            headers={"Origin": assigned},
        )
        assert res_get.status_code == 200
        data = res_get.json()
        assert data["email"] == STUDENT
        assert data["count"] == 4
        assert data["sum"] == 100
        assert data["min"] == 10
        assert data["max"] == 40
        assert data["mean"] == 25.0
        assert "x-request-id" in res_get.headers
        assert "x-process-time" in res_get.headers


@pytest.mark.asyncio
async def test_q4_verify_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # We need a private key corresponding to OAUTH_PUBKEY to mint tokens.
        # But for test purposes, let's verify that a bad token returns 401:
        res_bad = await client.post(
            f"/ga2/{STUDENT}/verify",
            json={"token": "bad.jwt.token"},
        )
        assert res_bad.status_code == 401
        assert res_bad.json() == {"valid": False}

        # Empty token -> 401
        res_empty = await client.post(
            f"/ga2/{STUDENT}/verify",
            json={"token": ""},
        )
        assert res_empty.status_code == 401
        assert res_empty.json() == {"valid": False}


@pytest.mark.asyncio
async def test_q6_compose_redis_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Initial count -> 0
        res0 = await client.get(f"/ga2/{STUDENT}/count/testkey")
        assert res0.status_code == 200
        assert res0.json() == {"key": "testkey", "count": 0}

        # Hit 1
        res1 = await client.post(f"/ga2/{STUDENT}/hit/testkey")
        assert res1.status_code == 200
        assert res1.json() == {"key": "testkey", "count": 1}

        # Hit 2
        res2 = await client.post(f"/ga2/{STUDENT}/hit/testkey")
        assert res2.status_code == 200
        assert res2.json() == {"key": "testkey", "count": 2}

        # Count -> 2
        res_c = await client.get(f"/ga2/{STUDENT}/count/testkey")
        assert res_c.status_code == 200
        assert res_c.json() == {"key": "testkey", "count": 2}


@pytest.mark.asyncio
async def test_q8_observability_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Baseline metrics
        m0 = await client.get(f"/ga2/{STUDENT}/metrics")
        assert m0.status_code == 200
        assert "http_requests_total" in m0.text

        # Work
        w = await client.get(f"/ga2/{STUDENT}/work?n=5")
        assert w.status_code == 200
        assert w.json() == {"email": STUDENT, "done": 5}
        assert "x-request-id" in w.headers

        # Healthz
        hz = await client.get(f"/ga2/{STUDENT}/healthz")
        assert hz.status_code == 200
        hz_data = hz.json()
        assert hz_data["status"] == "ok"
        assert hz_data["redis"] == "up"
        assert hz_data["uptime_s"] >= 0

        # Logs tail
        logs = await client.get(f"/ga2/{STUDENT}/logs/tail?limit=10")
        assert logs.status_code == 200
        entries = logs.json()
        assert isinstance(entries, list)
        assert len(entries) > 0
        assert any("/work" in e["path"] for e in entries)


@pytest.mark.asyncio
async def test_q10_extract_invoice_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        invoice_text = (
            "Invoice from Acme-Alpha Industries Ltd.\n"
            "Total Amount: 1,850.50 USD\n"
            "Payment due date: 2026-11-20\n"
        )
        res = await client.post(
            f"/ga2/{STUDENT}/extract",
            json={"text": invoice_text},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["vendor"] == "Acme-Alpha Industries Ltd."
        assert data["amount"] == 1850.50
        assert data["currency"] == "USD"
        assert data["date"] == "2026-11-20"

        # Bad input -> 422
        bad_res = await client.post(
            f"/ga2/{STUDENT}/extract",
            json={"text": "garbage and non-invoice text"},
        )
        assert bad_res.status_code == 422


@pytest.mark.asyncio
async def test_q13_stream_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"/ga2/{STUDENT}/stream.json")
        assert res.status_code == 200
        data = res.json()
        expected = stream_answer(STUDENT)
        assert data == expected


@pytest.mark.asyncio
async def test_q14_docker_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get(f"/ga2/{STUDENT}/docker.json")
        assert res.status_code == 200
        data = res.json()
        expected = docker_answer(STUDENT)
        assert data == expected
