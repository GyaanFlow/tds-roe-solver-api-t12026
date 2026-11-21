#!/usr/bin/env python3
"""Q2 q-ollama-faiss-rank-correlation-server: build the 10x7 matrix on YOUR machine.

Two real Ollama embedding models are needed for the graded value (rho must be within +/-0.05 of the
reference), so this cannot be computed by a hosted API. Requirements:

    ollama pull nomic-embed-text
    ollama pull mxbai-embed-large
    pip install requests numpy

Usage:
    python ollama_matrix.py dataset.json            # dataset.json = the file shown in the exam
    python ollama_matrix.py --email you@ds.study.iitm.ac.in --host https://<hub>   # fetch it from the hub

Prints the 10x7 JSON matrix [[a1,a2,a3,b1,b2,b3,rho], ...] to paste into the exam.
It follows the exam's starter script exactly (normalised embeddings, inner-product search over all 50
documents, Spearman rho between the two models' score vectors) but needs neither FAISS nor SciPy.
"""
import argparse
import json
import sys
from urllib.parse import quote

import numpy as np
import requests

import os
import time

OLLAMA = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
if not OLLAMA.startswith("http"):
    OLLAMA = "http://" + OLLAMA
MODEL_A, MODEL_B = "nomic-embed-text", "mxbai-embed-large"


class OllamaError(RuntimeError):
    pass


def _post(path: str, payload: dict, tries: int = 3):
    last = None
    for attempt in range(tries):
        try:
            r = requests.post(f"{OLLAMA}{path}", json=payload, timeout=180)
            if r.status_code == 404 and "not found" in r.text.lower() and "model" in r.text.lower():
                raise OllamaError(f"Model '{payload.get('model')}' is not installed. Run: ollama pull {payload.get('model')}")
            return r
        except requests.ConnectionError as exc:
            last = exc
            time.sleep(1.5 * (attempt + 1))
        except requests.Timeout as exc:
            last = exc
    raise OllamaError(f"Cannot reach Ollama at {OLLAMA} ({type(last).__name__}). Is `ollama serve` running? "
                      f"Set OLLAMA_HOST if it listens elsewhere.")


def embed_one(model: str, text: str) -> list[float]:
    """Older Ollama exposes /api/embeddings {prompt}; newer builds prefer /api/embed {input}."""
    r = _post("/api/embeddings", {"model": model, "prompt": text})
    if r.status_code == 200 and r.json().get("embedding"):
        return r.json()["embedding"]
    r2 = _post("/api/embed", {"model": model, "input": text})
    if r2.status_code == 200:
        rows = r2.json().get("embeddings") or []
        if rows and rows[0]:
            return rows[0]
    raise OllamaError(f"Ollama returned HTTP {r2.status_code} for model '{model}': {r2.text[:200]}")


def embed(model: str, texts: list[str]) -> np.ndarray:
    rows = [embed_one(model, text) for text in texts]
    if len({len(r) for r in rows}) != 1:
        raise OllamaError(f"Model '{model}' returned embeddings of different sizes")
    arr = np.array(rows, dtype=np.float32)
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    if (norms == 0).any():
        raise OllamaError(f"Model '{model}' returned an all-zero embedding")
    arr /= norms  # faiss.normalize_L2
    return arr


def rank_average(values: np.ndarray) -> np.ndarray:
    """Ranks with ties averaged (what scipy.stats.spearmanr uses)."""
    order = np.argsort(values, kind="mergesort")
    ranks = np.empty(len(values), dtype=np.float64)
    ranks[order] = np.arange(len(values), dtype=np.float64)
    for v in np.unique(values):
        mask = values == v
        if mask.sum() > 1:
            ranks[mask] = ranks[mask].mean()
    return ranks


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    ra, rb = rank_average(a), rank_average(b)
    ra, rb = ra - ra.mean(), rb - rb.mean()
    return float((ra * rb).sum() / np.sqrt((ra * ra).sum() * (rb * rb).sum()))


def top3(scores: np.ndarray) -> list[int]:
    # IndexFlatIP returns the largest inner products first; ties resolve to the lower index.
    return [int(i) for i in np.argsort(-scores, kind="stable")[:3]]


def build_matrix(corpus_a, corpus_b, queries_a, queries_b) -> list[list]:
    matrix = []
    for q in range(len(queries_a)):
        sa = corpus_a @ queries_a[q]
        sb = corpus_b @ queries_b[q]
        matrix.append(top3(sa) + top3(sb) + [round(spearman(sa, sb), 4)])
    return matrix


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset", nargs="?")
    ap.add_argument("--email")
    ap.add_argument("--host", help="hub origin, e.g. https://tds-roe-solver-api-t12026.onrender.com")
    args = ap.parse_args()
    if args.dataset:
        data = json.load(open(args.dataset, encoding="utf-8"))
    elif args.email and args.host:
        url = f"{args.host.rstrip('/')}/t3ga5/{quote(args.email.strip().lower(), safe='')}/answers/ollama-dataset"
        for attempt in range(6):  # the free host may be asleep
            try:
                resp = requests.get(url, timeout=60)
                if resp.status_code == 200:
                    data = resp.json()
                    break
                print(f"dataset request returned HTTP {resp.status_code}; retrying...", file=sys.stderr)
            except requests.RequestException as exc:
                print(f"dataset request failed ({type(exc).__name__}); retrying...", file=sys.stderr)
            time.sleep(8)
        else:
            sys.exit("ERROR: could not download the dataset from the hub; pass dataset.json instead")
    else:
        ap.error("give dataset.json, or --email and --host")
    sentences, queries = data["sentences"], data["queries"]
    if len(sentences) != 50 or len(queries) != 10:
        sys.exit("ERROR: unexpected dataset shape (need 50 sentences and 10 queries)")
    try:
        print("embedding with", MODEL_A, "...", file=sys.stderr)
        ca, qa = embed(MODEL_A, sentences), embed(MODEL_A, queries)
        print("embedding with", MODEL_B, "...", file=sys.stderr)
        cb, qb = embed(MODEL_B, sentences), embed(MODEL_B, queries)
    except OllamaError as exc:
        sys.exit(f"ERROR: {exc}")
    matrix = build_matrix(ca, cb, qa, qb)
    rhos = [row[6] for row in matrix]
    if min(rhos) >= 0.95:
        print("WARNING: every rho >= 0.95 - did both runs use the same model?", file=sys.stderr)
    print(json.dumps(matrix))


if __name__ == "__main__":
    main()
