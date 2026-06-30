from __future__ import annotations

import sys
import time
import uuid
import jwt
from fastapi.testclient import TestClient
from hf_space.app import app

client = TestClient(app)

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuYcxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMIDEkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXcWyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfWed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfISI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIXdQIDAQAB
-----END PUBLIC KEY-----"""

# Corresponding mock private key to mint test tokens (2048-bit RSA)
# This is generated just for signing verification test tokens
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
# Note: For strict testing, we'll verify using our generated key pairs or bypass. 
# Wait, the verification endpoint in Q02 uses the hardcoded PUBLIC_KEY.
# So we need to sign the test token with a private key that matches PUBLIC_KEY.
# Since we don't have the private key of PUBLIC_KEY, how can we test?
# Ah! We can monkeypatch/override the PUBLIC_KEY inside Q02_oauth/main.py during test, 
# or temporarily sign with a key pair and mock the verification!
# Let's override T22026.GA2.Q02_oauth.main.PUBLIC_KEY with our private key's public key.
import T22026.GA2.Q02_oauth.main as q2_main
test_public_key_pem = private_key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
).decode("utf-8")
q2_main.PUBLIC_KEY = test_public_key_pem


def test_q1_metrics():
    print("Testing Q01: Metrics...")
    email = "test-user@example.com"
    # Preflight pre-check
    headers = {"Origin": "https://dash-wrong.example.com"}
    resp = client.options(f"/ga2/{email}/q1/stats", headers=headers)
    assert "Access-Control-Allow-Origin" not in resp.headers, "ACAO header should not be present for wrong origin"
    
    # Preflight correct origin
    from T22026.GA2.shared.tenant import get_q01_allowed_origin
    allowed = get_q01_allowed_origin(email)
    headers = {"Origin": allowed}
    resp = client.options(f"/ga2/{email}/q1/stats", headers=headers)
    print("OPTIONS status:", resp.status_code)
    print("OPTIONS headers:", dict(resp.headers))
    print("Expected allowed origin:", allowed)
    assert resp.headers.get("Access-Control-Allow-Origin") == allowed

    # GET Stats
    resp = client.get(f"/ga2/{email}/q1/stats?values=10,20,30", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == email
    assert data["count"] == 3
    assert data["sum"] == 60
    assert data["min"] == 10
    assert data["max"] == 30
    assert data["mean"] == 20.0
    assert "X-Request-ID" in resp.headers
    assert "X-Process-Time" in resp.headers
    print("[PASS] Q01 Metrics verified!")


def test_q2_oauth():
    print("Testing Q02: OAuth Verify...")
    email = "test-user@example.com"
    from T22026.GA2.shared.tenant import get_q02_jwt_parameters
    params = get_q02_jwt_parameters(email)
    
    # 1. Valid Token
    payload = {
        "iss": params["iss"],
        "aud": params["aud"],
        "sub": params["sub"],
        "email": "test-user@example.com",
        "exp": int(time.time()) + 3600
    }
    token = jwt.encode(payload, private_key_pem, algorithm="RS256")
    resp = client.post(f"/ga2/{email}/q2/verify", json={"token": token})
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    assert resp.json()["valid"] is True
    assert resp.json()["aud"] == params["aud"]

    # 2. Expired Token
    payload_expired = dict(payload, exp=int(time.time()) - 10)
    token_exp = jwt.encode(payload_expired, private_key_pem, algorithm="RS256")
    resp = client.post(f"/ga2/{email}/q2/verify", json={"token": token_exp})
    assert resp.status_code == 401
    assert resp.json()["valid"] is False

    # 3. Wrong Audience
    payload_aud = dict(payload, aud="wrong-aud")
    token_aud = jwt.encode(payload_aud, private_key_pem, algorithm="RS256")
    resp = client.post(f"/ga2/{email}/q2/verify", json={"token": token_aud})
    assert resp.status_code == 401
    print("[PASS] Q02 OAuth Verify verified!")


def test_q3_config():
    print("Testing Q03: Config layers...")
    email = "test-user@example.com"
    from T22026.GA2.shared.tenant import get_q03_config_layers
    layers = get_q03_config_layers(email)
    expected_port = layers["baseEffective"]["port"]

    # Test baseline GET /effective-config
    resp = client.get(f"/ga2/{email}/q3/effective-config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["port"] == expected_port
    assert data["api_key"] == "****"
    
    # Test overrides
    resp = client.get(f"/ga2/{email}/q3/effective-config?set=port=9090&set=debug=yes")
    assert resp.status_code == 200
    data_override = resp.json()
    assert data_override["port"] == 9090
    assert data_override["debug"] is True
    print("[PASS] Q03 Config Precedence verified!")


def test_q4_compose():
    print("Testing Q04: Compose Redis counter...")
    email = "test-user@example.com"
    # We mock get_redis() since redis is not running in tests
    import T22026.GA2.Q04_compose.main as q4_main
    class DummyRedis:
        def __init__(self):
            self.store = {}
        def incr(self, key):
            self.store[key] = self.store.get(key, 0) + 1
            return self.store[key]
        def get(self, key):
            return self.store.get(key, None)
        def ping(self):
            return True

    q4_main.r_client = DummyRedis()
    
    # Hit
    resp = client.post(f"/ga2/{email}/q4/hit/testkey")
    assert resp.json()["count"] == 1
    resp = client.post(f"/ga2/{email}/q4/hit/testkey")
    assert resp.json()["count"] == 2

    # Count
    resp = client.get(f"/ga2/{email}/q4/count/testkey")
    assert resp.json()["count"] == 2

    # Health
    resp = client.get(f"/ga2/{email}/q4/healthz")
    assert resp.json()["status"] == "ok"
    print("[PASS] Q04 Redis counter verified!")


def test_q5_analytics():
    print("Testing Q05: Analytics aggregation...")
    email = "test-user@example.com"
    from T22026.GA2.shared.tenant import get_q05_api_key
    key = get_q05_api_key(email)

    payload = {
        "events": [
            {"user": "alice", "amount": 100.0, "ts": 123},
            {"user": "bob", "amount": -50.0, "ts": 124},
            {"user": "alice", "amount": 50.0, "ts": 125}
        ]
    }
    
    # Missing Auth
    resp = client.post(f"/ga2/{email}/q5/analytics", json=payload)
    assert resp.status_code == 401

    # Valid Auth
    resp = client.post(f"/ga2/{email}/q5/analytics", json=payload, headers={"X-API-Key": key})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["total_events"] == 3
    assert data["unique_users"] == 2
    assert data["revenue"] == 150.0
    assert data["top_user"] == "alice"
    print("[PASS] Q05 Analytics verified!")


def test_q6_observability():
    print("Testing Q06: Observability...")
    email = "test-user@example.com"
    resp = client.get(f"/ga2/{email}/q6/work?n=5")
    assert resp.json()["done"] == 5

    # Metrics
    resp = client.get(f"/ga2/{email}/q6/metrics")
    assert "http_requests_total" in resp.text

    # Logs
    resp = client.get(f"/ga2/{email}/q6/logs/tail?limit=5")
    data = resp.json()
    assert len(data) > 0
    # Check fields
    for log in data:
        assert "level" in log
        assert "ts" in log
        assert "path" in log
        assert "request_id" in log
    # Check at least one path contains /work
    has_work = any("/work" in log["path"] for log in data)
    assert has_work, "At least one log entry must contain '/work'"
    print("[PASS] Q06 Observability verified!")


def test_q7_llm_tunnel():
    print("Testing Q07: LLM Tunnel completions...")
    email = "test-user@example.com"
    # Echo test
    payload = {
        "model": "mock-model",
        "messages": [{"role": "user", "content": "Please repeat this: TK9F3A1B"}]
    }
    resp = client.post(f"/ga2/{email}/q7/v1/chat/completions", json=payload)
    assert resp.status_code == 200
    assert "TK9F3A1B" in resp.json()["choices"][0]["message"]["content"]

    # Math test
    payload_math = {
        "model": "mock-model",
        "messages": [{"role": "user", "content": "What is 40 + 25?"}]
    }
    resp = client.post(f"/ga2/{email}/q7/v1/chat/completions", json=payload_math)
    assert "65" in resp.json()["choices"][0]["message"]["content"]
    print("[PASS] Q07 LLM Tunnel verified!")


def test_q8_extract():
    print("Testing Q08: LLM Invoice extract...")
    email = "test-user@example.com"
    invoice_text = "Vendor is Acme-1234 Industries Ltd., amount due is USD 540.50, pay by 2026-08-12."
    resp = client.post(f"/ga2/{email}/q8/extract", json={"text": invoice_text})
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert "Acme-1234 Industries Ltd" in data["vendor"]
    assert data["amount"] == 540.50
    assert data["currency"] == "USD"
    assert data["date"] == "2026-08-12"
    print("[PASS] Q08 LLM Extract verified!")


def test_q9_orders():
    print("Testing Q09: Orders idempotency & pagination...")
    email = "test-user@example.com"
    # Idempotency
    key = str(uuid.uuid4())
    resp1 = client.post(f"/ga2/{email}/q9/orders", headers={"Idempotency-Key": key})
    assert resp1.status_code == 201
    id1 = resp1.json()["id"]

    resp2 = client.post(f"/ga2/{email}/q9/orders", headers={"Idempotency-Key": key})
    assert resp2.status_code == 200
    id2 = resp2.json()["id"]
    assert id1 == id2, "Reusing Idempotency-Key should yield the same order id"

    # Pagination
    resp = client.get(f"/ga2/{email}/q9/orders?limit=5")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 5
    assert data["items"][0]["id"] == 1
    assert data["next_cursor"] == "6"
    print("[PASS] Q09 Orders verified!")


def test_q10_middleware():
    print("Testing Q10: Ping Middleware...")
    email = "test-user@example.com"
    
    # Context propagation
    rid = "test-rid-123"
    resp = client.get(f"/ga2/{email}/q10/ping", headers={"X-Request-ID": rid})
    assert resp.status_code == 200
    assert resp.json()["request_id"] == rid
    assert resp.headers.get("X-Request-ID") == rid

    # Rate limiting
    from T22026.GA2.shared.tenant import get_q10_middleware_params
    params = get_q10_middleware_params(email)
    bucket = params["bucket"]

    client_id = f"client-{uuid.uuid4()}"
    for _ in range(bucket):
        r = client.get(f"/ga2/{email}/q10/ping", headers={"X-Client-Id": client_id})
        assert r.status_code == 200

    # Next request should be rate limited (429)
    r_limited = client.get(f"/ga2/{email}/q10/ping", headers={"X-Client-Id": client_id})
    assert r_limited.status_code == 429
    assert "Retry-After" in r_limited.headers
    print("[PASS] Q10 Middleware verified!")


def main():
    print("=== STARTING GA2 VERIFICATION TESTS ===")
    test_q1_metrics()
    test_q2_oauth()
    test_q3_config()
    test_q4_compose()
    test_q5_analytics()
    test_q6_observability()
    test_q7_llm_tunnel()
    test_q8_extract()
    test_q9_orders()
    test_q10_middleware()
    print("=== ALL GA2 ENDPOINTS VERIFIED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
