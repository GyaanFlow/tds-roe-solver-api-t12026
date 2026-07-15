import requests
from typing import List, Dict, Any, Optional

class GA2ApiClient:
    """
    Reusable client wrapper to consume the GA2 Multi-Tenant API Hub
    from other solver projects or automation scripts.
    """
    def __init__(self, email: str, base_host: str = "https://tds-roe-solver-api-t12026.onrender.com"):
        self.email = email
        self.base_host = base_host.rstrip('/')

    def get_url(self, path: str) -> str:
        return f"{self.base_host}/ga2/{self.email}/{path.lstrip('/')}"

    # Q01: Metrics + CORS
    def get_stats(self, values: List[int]) -> Dict[str, Any]:
        val_str = ",".join(map(str, values))
        url = self.get_url(f"q1/stats?values={val_str}")
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    # Q02: OAuth JWT Verify
    def verify_token(self, token: str) -> Dict[str, Any]:
        url = self.get_url("q2/verify")
        resp = requests.post(url, json={"token": token})
        resp.raise_for_status()
        return resp.json()

    # Q03: Config Precedence
    def get_effective_config(self, overrides: Optional[List[str]] = None) -> Dict[str, Any]:
        path = "q3/effective-config"
        if overrides:
            query = "&".join(f"set={o}" for o in overrides)
            path = f"{path}?{query}"
        url = self.get_url(path)
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    # Q04: Redis Counter
    def hit_counter(self, key: str) -> Dict[str, Any]:
        url = self.get_url(f"q4/hit/{key}")
        resp = requests.post(url)
        resp.raise_for_status()
        return resp.json()

    def get_counter(self, key: str) -> Dict[str, Any]:
        url = self.get_url(f"q4/count/{key}")
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    # Q05: Analytics
    def submit_analytics(self, api_key: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        url = self.get_url("q5/analytics")
        headers = {"X-API-Key": api_key}
        resp = requests.post(url, json={"events": events}, headers=headers)
        resp.raise_for_status()
        return resp.json()

    # Q06: Observability
    def perform_work(self, n: int) -> Dict[str, Any]:
        url = self.get_url(f"q6/work?n={n}")
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    def get_metrics_text(self) -> str:
        url = self.get_url("q6/metrics")
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.text

    # Q07: LLM Chat completions
    def get_completions(self, model: str, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        url = self.get_url("q7/v1/chat/completions")
        resp = requests.post(url, json={"model": model, "messages": messages})
        resp.raise_for_status()
        return resp.json()

    # Q08: Invoice Extractor
    def extract_invoice(self, text: str) -> Dict[str, Any]:
        url = self.get_url("q8/extract")
        resp = requests.post(url, json={"text": text})
        resp.raise_for_status()
        return resp.json()

    # Q09: Orders
    def create_order(self, idempotency_key: str, client_id: str) -> Dict[str, Any]:
        url = self.get_url("q9/orders")
        headers = {
            "Idempotency-Key": idempotency_key,
            "X-Client-Id": client_id
        }
        resp = requests.post(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

    def list_orders(self, limit: int = 10, cursor: Optional[str] = None) -> Dict[str, Any]:
        path = f"q9/orders?limit={limit}"
        if cursor:
            path += f"&cursor={cursor}"
        url = self.get_url(path)
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()

    # Q10: Ping Middleware Stack
    def ping_middleware(self, client_id: str, request_id: Optional[str] = None) -> Dict[str, Any]:
        url = self.get_url("q10/ping")
        headers = {"X-Client-Id": client_id}
        if request_id:
            headers["X-Request-ID"] = request_id
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
