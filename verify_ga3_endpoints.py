import base64
import json
import math
import sys
from fastapi.testclient import TestClient
from hf_space.app import app

client = TestClient(app)

# Mock Q1 youtube metadata fetch to avoid network calls during test
import T22026.GA3.solvers as solvers
solvers.get_youtube_metadata_cached = lambda url: {
    "id": "_C8kWso4ne4",
    "title": "Mock python video title",
    "description": "Mock description containing python",
    "duration": 500,
    "upload_date": "20260520"
}

# Mock the async AIPipe chat function to avoid external API calls
async def _mock_aipipe_chat(messages, model="gpt-4o-mini", max_tokens=800, force_json=False, timeout=90, retries=4):
    prompt_text = ""
    for m in messages:
        if isinstance(m.get("content"), str):
            prompt_text += m["content"] + "\n"
        elif isinstance(m.get("content"), list):
            for part in m["content"]:
                if isinstance(part, dict) and part.get("type") == "text":
                    prompt_text += part["text"] + "\n"

    prompt_lower = prompt_text.lower()

    # Q2 multimodal QA
    if "question" in prompt_lower and "image" in prompt_lower:
        return '{"work": "Extracted answer from image.", "answer": "42"}'

    # Q3 invoice_extract
    if "invoice_no" in prompt_lower:
        return '{"invoice_no": "INV-123", "date": "2026-05-20", "vendor": "Test Vendor", "amount": 100.0, "tax": 10.0, "currency": "USD"}'

    # Q4 dynamic_extract
    if "customer_name" in prompt_lower and "quantity" in prompt_lower:
        return '{"customer_name": "Rahul", "item": "notebooks", "quantity": 3, "amount": 240.0, "purchase_date": "2026-06-12", "store": "Alpha Store"}'

    # Q6 korean audio
    if "transcript" in prompt_lower and "columns" in prompt_lower:
        return json.dumps({
            "columns": ["id", "name", "score", "age"],
            "data_rows": [["1", "Alice", "85.0", "23"], ["2", "Bob", "95.0", "25"], ["3", "Charlie", "75.0", "21"]],
            "num_rows": None,
            "explicit_stats": {},
            "requested_stats": ["mean", "std", "variance", "min", "max", "median", "mode", "range", "allowed_values", "value_range", "correlation"]
        })

    # Q7 structured extraction
    if "vendor" in prompt_lower and "currency" in prompt_lower:
        return json.dumps({
            "vendor": "Acme Industrial Supply",
            "currency": "USD",
            "total_amount": 12480,
            "invoice_date": "2024-03-03",
            "due_in_days": 30,
            "is_paid": False,
            "priority": "high",
            "contact_email": "ap@acme.com",
            "line_items": [{"sku": "WIDGET-204", "quantity": 12, "unit_price": 40}, {"sku": "BOLT-118", "quantity": 200, "unit_price": 5}],
            "item_count": 2
        })

    # Q8 semantic rank
    if "query" in prompt_lower and "candidates" in prompt_lower:
        pass  # handled by _openai_embeddings mock

    # Q9 cot math
    if "solve" in prompt_lower or "problem" in prompt_lower:
        return '{"reasoning": "We perform step-by-step arithmetic. First, add 20 and 22 to get 42. Then verify by subtracting 20 from 42 to get 22. The answer is 42.", "answer": 42}'

    return "{}"


async def _mock_openai_embeddings(texts, model="text-embedding-3-small"):
    return [[0.1, 0.2, 0.3] for _ in texts]


solvers._aipipe_chat = _mock_aipipe_chat
solvers._openai_embeddings = _mock_openai_embeddings


def test_ga3_routes():
    print("=== STARTING GA3 ENDPOINT VERIFICATION TESTS ===")

    # 1. Test Gateway Root
    res = client.get("/ga3/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    print("[PASS] GA3 Gateway Root verified!")

    # 2. Test OPTIONS / CORS Headers
    res = client.options(
        "/ga3/test@ds.study.iitm.ac.in/q2",
        headers={
            "Origin": "https://exam.sanand.workers.dev",
            "Access-Control-Request-Method": "POST"
        }
    )
    assert res.status_code == 200
    assert res.headers.get("access-control-allow-origin") == "*"
    print("[PASS] GA3 OPTIONS CORS verified!")

    # 3. Test health + onboarding + status
    res = client.get("/ga3/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    print("[PASS] GA3 health endpoint verified!")

    res = client.post(
        "/ga3/onboard",
        json={"email": "test@ds.study.iitm.ac.in", "aipipe_token": "test-token-value"},
    )
    assert res.status_code == 200, res.text
    onboard = res.json()
    assert onboard["configured"] is True
    assert onboard["has_token"] is True
    assert "/ga3/test%40ds.study.iitm.ac.in/q2" in onboard["ready_routes"][0]
    assert len(onboard["ready_routes"]) == 13
    print("[PASS] Onboard endpoint verified!")

    res = client.get("/ga3/test@ds.study.iitm.ac.in/status")
    assert res.status_code == 200, res.text
    status = res.json()
    assert status["has_token"] is True
    assert len(status["ready_routes"]) == 13
    print("[PASS] Tenant status endpoint verified!")

    # 4. Test Config Saving Endpoint
    res = client.post(
        "/ga3/test@ds.study.iitm.ac.in/config",
        json={"aipipe_token": "test-token-value"}
    )
    assert res.status_code == 200
    from T22026.GA3.shared.tenant import get_tenant_config
    config = get_tenant_config("test@ds.study.iitm.ac.in")
    assert config.get("aipipe_token") == "test-token-value"
    print("[PASS] Config saving endpoint verified!")

    res = client.post("/ga3/test@ds.study.iitm.ac.in/solve/q12", json={"bad": True})
    assert res.status_code == 400
    print("[PASS] Invalid solver payload returns 400!")

    # 5. Test Q2 Multimodal Image QA
    payload_q2 = {"image_base64": "iVBOR...", "question": "What is the answer?"}
    res = client.post("/ga3/test@ds.study.iitm.ac.in/q2", json=payload_q2)
    assert res.status_code == 200, f"Q2 failed: {res.text}"
    assert res.json() == {"answer": "42"}, f"Q2 got: {res.json()}"

    res = client.post("/ga3/test@ds.study.iitm.ac.in/answer-image", json=payload_q2)
    assert res.status_code == 200, f"Q2 direct failed: {res.text}"
    assert res.json() == {"answer": "42"}, f"Q2 direct got: {res.json()}"
    print("[PASS] Q2 Multimodal QA endpoints verified!")

    # 6. Test Q3 Fixed Schema Invoice Extraction
    payload_q3 = {"invoice_text": "Vendor: Test Vendor, Invoice No: INV-123"}
    res = client.post("/ga3/test@ds.study.iitm.ac.in/q3", json=payload_q3)
    assert res.status_code == 200, f"Q3 failed: {res.text}"
    assert res.json()["invoice_no"] == "INV-123"

    res = client.post("/ga3/test@ds.study.iitm.ac.in/extract", json=payload_q3)
    assert res.status_code == 200, f"Q3 direct failed: {res.text}"
    assert res.json()["invoice_no"] == "INV-123"
    print("[PASS] Q3 Invoice Extraction endpoints verified!")

    # 7. Test Q4 Dynamic Schema Structured Extraction
    payload_q4 = {
        "text": "Rahul bought 3 notebooks...",
        "schema": {"customer_name": "string", "quantity": "integer"}
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/q4", json=payload_q4)
    assert res.status_code == 200, f"Q4 failed: {res.text}"
    assert res.json()["customer_name"] == "Rahul"

    res = client.post("/ga3/test@ds.study.iitm.ac.in/dynamic-extract", json=payload_q4)
    assert res.status_code == 200, f"Q4 direct failed: {res.text}"
    assert res.json()["customer_name"] == "Rahul"
    print("[PASS] Q4 Dynamic Extraction endpoints verified!")

    # 8. Test Q1 Solver Route
    q1_payload = {
        "source_urls": ["https://www.youtube.com/watch?v=_C8kWso4ne4"],
        "min_duration_seconds": 300,
        "max_duration_seconds": 2400,
        "required_words": ["python"],
        "forbidden_words": ["shorts"],
        "limit": 1
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/solve/q1", json=q1_payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    assert res.json() == {"urls": ["https://www.youtube.com/watch?v=_C8kWso4ne4"]}
    print("[PASS] Q1 Solver verified!")

    # 9. Test Q5 Solver Route
    q5_payload = {
        "documents": [
            {"doc_id": "D000001", "embedding": [1.0, 0.0]},
            {"doc_id": "D000002", "embedding": [0.0, 1.0]}
        ],
        "queries": [
            {"query_id": "Q001", "embedding": [1.0, 0.0]}
        ]
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/solve/q5", json=q5_payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    assert res.json() == {"Q001": ["D000001", "D000002"]}
    print("[PASS] Q5 Solver verified!")

    # 10. Test Q6: Korean Audio Dataset API with mock Base64 CSV
    csv_content = (
        "id,name,score,age\n"
        "1,Alice,85.0,23\n"
        "2,Bob,95.0,25\n"
        "3,Charlie,75.0,21\n"
    )
    b64_data = base64.b64encode(csv_content.encode("utf-8")).decode("utf-8")

    payload = {
        "audio_id": "test_q6",
        "audio_base64": b64_data
    }

    res = client.post("/ga3/test@ds.study.iitm.ac.in/q6", json=payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()

    assert data["rows"] == 3
    assert data["columns"] == ["id", "name", "score", "age"]
    assert math.isclose(data["mean"]["score"], 85.0)
    assert math.isclose(data["mean"]["age"], 23.0)
    assert math.isclose(data["std"]["score"], 10.0), f"std={data['std']}"
    assert math.isclose(data["variance"]["score"], 100.0), f"variance={data['variance']}"
    assert data["min"]["age"] == 21.0
    assert data["max"]["age"] == 25.0
    assert data["allowed_values"]["name"] == ["Alice", "Bob", "Charlie"]
    print("[PASS] Q6 Audio Dataset parser statistics verified!")

    # 11. Test Q10 Solver Route (Proof of Work)
    q10_payload = {
        "token": "powtest",
        "difficulty": 4
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/solve/q10", json=q10_payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    assert "nonce" in res.json()
    print("[PASS] Q10 Solver verified!")

    # 12. Test Q11 Solver Route (Context Heist)
    q11_payload = {
        "haystack": "LATEST FACT [Q1]: The current active retrieval strategy is hybrid-v4. Use this value."
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/solve/q11", json=q11_payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    ans = res.json()
    assert ans["answers"]["q1"] == "hybrid-v4"
    print("[PASS] Q11 Solver verified!")

    # 13. Test Q12 Solver Route (Spin Up CLI)
    q12_payload = {
        "dataset": [
            {"id": "log-001", "message": "password spray detected for tenant login"}
        ],
        "marker": "SPINCLI_VERIFY"
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/solve/q12", json=q12_payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    assert "session_cast" in res.json()
    print("[PASS] Q12 Solver verified!")

    # 14. Test Q13 Solver Route (Embedding Trapdoors)
    q13_payload = {
        "queries": [
            {"id": "q1", "text": "patient has low blood sugar", "domain": "medical"}
        ],
        "corpus": [
            {"id": "p-005", "text": "clinical note reports hypoglycemia"}
        ]
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/solve/q13", json=q13_payload)
    assert res.status_code == 200, f"Failed: {res.text}"
    assert res.json() == {"q1": "p-005"}
    print("[PASS] Q13 Solver verified!")

    # 15. Test Q9 Word Problem Solver
    q9_payload = {
        "problem_id": "p0",
        "problem": "Calculate 20 + 22."
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/q9", json=q9_payload)
    assert res.status_code == 200, f"Q9 failed: {res.text}"
    ans_q9 = res.json()
    assert ans_q9["answer"] == 42
    assert len(ans_q9["reasoning"]) >= 80
    print("[PASS] Q9 Solver verified!")

    # 16. Test Q8 Semantic Rank
    q8_payload = {
        "query": "test query",
        "candidates": ["candidate a", "candidate b", "candidate c"]
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/q8", json=q8_payload)
    assert res.status_code == 200, f"Q8 failed: {res.text}"
    print("[PASS] Q8 Solver verified!")

    # 17. Test Q7 Structured Extraction
    q7_payload = {
        "text": "INVOICE from Acme Industrial Supply. Total: $12,480. Due: Net 30.",
        "schema": {"type": "object", "properties": {}}
    }
    res = client.post("/ga3/test@ds.study.iitm.ac.in/q7", json=q7_payload)
    assert res.status_code == 200, f"Q7 failed: {res.text}"
    q7_data = res.json()
    assert q7_data["vendor"] == "Acme Industrial Supply"
    assert q7_data["currency"] == "USD"
    print("[PASS] Q7 Solver verified!")

    # 18. Test cache-stats endpoint
    res = client.get("/ga3/cache-stats")
    assert res.status_code == 200
    print("[PASS] Cache stats endpoint verified!")

    print("=== ALL GA3 ENDPOINTS VERIFIED SUCCESSFULLY ===")


if __name__ == "__main__":
    try:
        test_ga3_routes()
    except AssertionError as e:
        print(f"[FAIL] Assertion error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
