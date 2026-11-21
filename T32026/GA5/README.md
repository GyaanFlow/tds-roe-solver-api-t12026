# T3-2026 GA5 API hub

Mounted at `/t3ga5` by `hf_space/app.py`. Exam source: `exam-tds-2026-09-ga5.js`; extracted per-student data in `exam_data.json`.

| Question | Route | Module |
|---|---|---|
| Q1 `q-rag-colosseum-server` | `POST /t3ga5/{email}/query` | `rag.py`, `kb.py` |
| Q4 `q-harness-safety-router-server` | `POST /t3ga5/{email}/harness` | `harness.py` |
| Q2 `q-ollama-faiss-rank-correlation-server` | `GET /t3ga5/{email}/answers/ollama-dataset`, `.../ollama-script` (local compute) | `kb.py`, `ollama_matrix.py` |
| Q3 `q-ball-tracker-server` | not built yet | |

Everything is provider-free and deterministic: no model call is made, no per-student state is stored. See
[SOLVER_INTEGRATION_GUIDE.md](SOLVER_INTEGRATION_GUIDE.md) for the browser-solver wiring.

`kb.py` ports the exam's seeded generators (seedrandom ARC4) and is verified bit-for-bit against npm `seedrandom`
(`python -m pytest tests/test_t32026_ga5.py`).
