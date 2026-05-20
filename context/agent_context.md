# Agent Context (Persistent)

## Purpose
This file stores durable context across terms, graded assignments (GA), and question attempts.

## Conventions
- Timestamp format: ISO 8601
- Always log: decision, rationale, affected paths, and status.
- Never store secrets/tokens.

## Current Workspace Snapshot
- Active term: T22026
- Active GA: GA0
- Created on: 2026-05-20
- Root path: C:\Users\gaura\Downloads\tds-roe-solver\tds-roe-solver-api

## Timeline Log

### 2026-05-20
- Initialized future-proof structure: `T22026/GA0/Q01..Q10`.
- Initialized Git repository.
- Added Graphify context scaffolding under `context/graphify/`.
- Seeded templates for future term/GA/question expansion.

## Next Actions
- Add per-question metadata files when questions are assigned.
- Maintain graph snapshots after each major change.

### 2026-05-20 (Q5 API Build)
- Implemented production-ready dynamic API at `T22026/GA0/Q05/app/main.py`.
- Added per-request token intake (`aipipe_token` body or `X-AIPipe-Token` header).
- Added execution timeout + subprocess isolation + AI fallback for error line extraction.
- Added deployment artifacts: `requirements.txt`, `Procfile`, `render.yaml`, `Q05 README.md`.

### 2026-05-20 (Q10 API Build)
- Copied and renamed `q-fastapi (4).csv` to `T22026/GA0/Q10/q-fastapi.csv`.
- Built production-ready Q10 API at `T22026/GA0/Q10/app/main.py`.
- Added Render deployment assets: `requirements.txt`, `Procfile`, `render.yaml`, `Q10 README.md`.
- Verified CSV load and schema with 2000 rows.

### 2026-05-20 (Q11 API Build)
- Built production-ready Q11 API at `T22026/GA0/Q11/app/main.py` using VADER.
- Added strict aliases: `/ga0/q11/sentiment` and `/t22026/ga0/q11/sentiment`.
- Added Render deployment assets: `requirements.txt`, `Procfile`, `render.yaml`, `Q11 README.md`.
- Added batch-size and sentence-length safety limits for scale readiness.

### 2026-05-20 (Q14 API Build)
- Built production-ready Q14 image API at `T22026/GA0/Q14/app/main.py`.
- Added strict aliases: `/ga0/q14/rebuild-grayscale` and `/t22026/ga0/q14/rebuild-grayscale`.
- Added built-in frontend page at `/` for upload/testing.
- Added Render assets: `requirements.txt`, `Procfile`, `render.yaml`, `Q14 README.md`.

### 2026-05-20 (Q16 API Build)
- Built production-ready Q16 API at `T22026/GA0/Q16/app/main.py`.
- Accepts zip + email and computes move/rename/hash answer dynamically.
- Added strict aliases: `/ga0/q16/solve`, `/t22026/ga0/q16/solve`.
- Added per-request temp workspace + guaranteed cleanup.
- Added Render deploy assets and frontend usage page.

### 2026-05-20 (Q18 API Build)
- Built production-ready Q18 API at `T22026/GA0/Q18/app/main.py`.
- Added dynamic setup endpoint using email + optional ngrok token.
- Added strict aliases: `/ga0/q18/setup`, `/t22026/ga0/q18/setup`.
- Added proxy-style route with required response headers and `/api/version` fallback.
- Added frontend usage page and Render deploy assets.

### 2026-05-20 (Q19 API Build)
- Built production-ready Q19 API at `T22026/GA0/Q19/app/main.py`.
- Accepts zip + email and computes replacement+checksum answer dynamically.
- Added strict aliases: `/ga0/q19/solve`, `/t22026/ga0/q19/solve`.
- Added zip safety checks, upload limits, and guaranteed cleanup.
- Added frontend usage page and Render deploy assets.

