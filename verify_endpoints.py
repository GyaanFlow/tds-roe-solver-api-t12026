import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(method, path, data=None, json_data=None, expected_status=200):
    url = f"{BASE_URL}{path}"
    try:
        if method.upper() == "GET":
            resp = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            resp = requests.post(url, data=data, json=json_data, timeout=5)
        else:
            print(f"Unsupported method: {method}")
            return False

        if resp.status_code != expected_status:
            print(f"[FAIL] {method} {path} -> expected status {expected_status}, got {resp.status_code}. Response: {resp.text}")
            return False
        
        print(f"[PASS] {method} {path} -> status {resp.status_code}")
        return resp
    except Exception as e:
        print(f"[FAIL] {method} {path} -> exception: {e}")
        return False

def main():
    print("=== STARTING VERIFICATION TESTS ===")
    
    # 1. Main Hub
    test_endpoint("GET", "/")
    test_endpoint("GET", "/api/version")
    
    # 2. Q5 Code Interpreter
    test_endpoint("GET", "/q-code-interpreter-ai-analysis/health")
    # Test execution with traceback line extraction
    code_interpreter_payload = {
        "code": "a = 5\nb = 0\nc = a / b\n",
        "aipipe_token": "" # optional
    }
    resp = test_endpoint("POST", "/q-code-interpreter-ai-analysis/code-interpreter", json_data=code_interpreter_payload)
    if resp:
        data = resp.json()
        print("Q5 error lines extracted:", data.get("error"))
        # Division by zero happens on line 3
        if data.get("error") == [3]:
            print("[PASS] Q5 traceback line number extraction succeeded!")
        else:
            print("[FAIL] Q5 traceback line number extraction failed! Got:", data.get("error"))

    # 3. Q10 Student API
    test_endpoint("GET", "/q-fastapi/health")
    resp = test_endpoint("GET", "/q-fastapi/api?class=1A")
    if resp:
        data = resp.json()
        print(f"Q10 students returned: {len(data.get('students', []))}")
        if len(data.get("students", [])) > 0:
            print("[PASS] Q10 student query succeeded!")
        else:
            print("[FAIL] Q10 student query returned 0 students!")

    # 4. Q11 Sentiment API
    test_endpoint("GET", "/q-fastapi-sentiment-batch/health")
    sentiment_payload = {
        "sentences": ["I love this product", "This is terrible", "The table is brown"]
    }
    resp = test_endpoint("POST", "/q-fastapi-sentiment-batch/sentiment", json_data=sentiment_payload)
    if resp:
        data = resp.json()
        results = {r["sentence"]: r["sentiment"] for r in data.get("results", [])}
        print("Q11 sentiment results:", results)
        if results.get("I love this product") == "happy" and results.get("This is terrible") == "sad":
            print("[PASS] Q11 sentiment classification succeeded!")
        else:
            print("[FAIL] Q11 sentiment classification failed!")

    # 5. Q14 Image Grayscale
    test_endpoint("GET", "/q-image-grayscale-rebuild/health")

    # 6. Q16 Move/Rename Zip
    test_endpoint("GET", "/q-move-rename-files/health")

    # 7. Q18 Ollama Proxy Helper
    test_endpoint("GET", "/q-ollama/health")
    setup_payload = {
        "email": "student@example.com",
        "ngrok_token": None
    }
    resp = test_endpoint("POST", "/q-ollama/ga0/q18/setup", json_data=setup_payload)
    if resp:
        data = resp.json()
        session_id = data.get("session_id")
        print("Q18 setup returned session_id:", session_id)
        
        # Test proxy fallback version endpoint
        resp_version = test_endpoint("GET", f"/q-ollama/session/{session_id}/api/version")
        if resp_version:
            v_data = resp_version.json()
            x_email_header = resp_version.headers.get("x-email")
            print("Q18 /api/version returned:", v_data, "with X-Email header:", x_email_header)
            if v_data.get("version") == "mock-0.0.1" and x_email_header == "student@example.com":
                print("[PASS] Q18 session version proxy/fallback succeeded!")
            else:
                print("[FAIL] Q18 session version proxy/fallback failed!")

if __name__ == "__main__":
    main()
