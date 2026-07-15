"""Smoke tests for the GA4 live-API hub, mounted at /ga4/{email}/...

GA4 has 12 questions total; only 3 (Q3, Q4, Q5) are graded by calling a deployed
endpoint and need a real dynamic URL — that's all this hub implements. The other
9 questions are pure client-side computation and are handled by a separate solver.
"""

from fastapi.testclient import TestClient

from hf_space.app import app

client = TestClient(app)
BASE = "/ga4/test@example.com"


def test_health():
    r = client.get(f"{BASE}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_onboard_and_status():
    r = client.post("/ga4/onboard", json={"email": "student@example.com"})
    assert r.status_code == 200
    assert r.json()["configured"] is True

    r = client.get(f"{BASE}/status")
    assert r.status_code == 200
    assert len(r.json()["ready_routes"]) == 5


def test_q3_grounded_answer_api():
    r = client.post(f"{BASE}/grounded-answer", json={
        "question": "What year was FAISS released?",
        "chunks": [{"chunk_id": "C1", "text": "FAISS was developed by Facebook AI Research and open-sourced in 2017."}],
    })
    assert r.status_code == 200
    body = r.json()
    assert body["answerable"] is True
    assert "C1" in body["citations"]

    r = client.post(f"{BASE}/grounded-answer", json={
        "question": "What is the capital of France?",
        "chunks": [{"chunk_id": "C1", "text": "FAISS was released in 2017."}],
    })
    body = r.json()
    assert body["answerable"] is False
    assert body["answer"].lower() == "i don't know"
    assert body["citations"] == []


def test_q4_vector_search_rerank():
    payload = {
        "query_id": "Q001", "query_vector": [1, 0], "top_k": 3, "rerank_top_n": 2,
        "filter": {"department": "finance"},
        "documents": [
            {"doc_id": "D1", "department": "finance", "year": 2024},
            {"doc_id": "D2", "department": "finance", "year": 2023},
            {"doc_id": "D3", "department": "hr", "year": 2024},
        ],
        "embeddings": {"D1": [1, 0], "D2": [0.9, 0.1], "D3": [1, 0]},
        "reranker_scores": {"Q001": {"D1": 0.5, "D2": 0.9}},
    }
    r = client.post(f"{BASE}/vector-search", json=payload)
    assert r.status_code == 200
    assert r.json()["matches"] == ["D2", "D1"]
    assert "D3" not in r.json()["matches"]  # filtered out by department


def test_q4_grader_path_generates_corpus_from_email():
    # The real grader posts ONLY the query (no documents/embeddings). The server
    # must generate the student's seeded 500-doc corpus in-memory and not 400.
    payload = {"query_id": "Q001", "query_vector": [0.1] * 100,
               "top_k": 10, "rerank_top_n": 3, "filter": {"department": "finance"}}
    r = client.post(f"{BASE}/vector-search", json=payload)
    assert r.status_code == 200, r.text
    matches = r.json()["matches"]
    assert isinstance(matches, list) and len(matches) == 3
    assert all(m.startswith("D") for m in matches)
    # deterministic for the same email
    r2 = client.post(f"{BASE}/vector-search", json=payload)
    assert r2.json()["matches"] == matches


def test_q4_seedrandom_matches_grader_values():
    # Python seedrandom port must reproduce the exam's JS seedrandom output.
    from T22026.GA4.q4data import seedrandom, _WE
    email = "23f1000805@ds.study.iitm.ac.in"
    dr = seedrandom(f"{_WE}#{email}#q4#doc#D001")
    doc = [round(dr() * 2 - 1, 4) for _ in range(5)]
    assert doc == [-0.0985, 0.062, -0.4543, 0.301, -0.4066]


def test_q5_graphrag_pipeline():
    r = client.post(f"{BASE}/extract-graph", json={
        "chunk_id": "C001",
        "text": "LangChain was created by Harrison Chase. LangChain integrates with OpenAI.",
    })
    assert r.status_code == 200
    graph = r.json()
    names = {e["name"] for e in graph["entities"]}
    assert {"LangChain", "Harrison Chase", "OpenAI"}.issubset(names)

    r2 = client.post(f"{BASE}/graph-query", json={
        "question": "Who created the framework that integrates with OpenAI?",
        "graph": graph,
    })
    assert r2.status_code == 200
    assert r2.json()["answer"] == "Harrison Chase"
    assert r2.json()["hops"] == 2

    r3 = client.post(f"{BASE}/community-summary", json={
        "community_id": "COM_001",
        "entities": ["LangChain", "Harrison Chase"],
        "relationships": graph["relationships"],
    })
    assert r3.status_code == 200
    assert "LangChain" in r3.json()["summary"]


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
