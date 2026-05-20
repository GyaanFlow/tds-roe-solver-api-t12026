# Graphify Context

Store graph-oriented context tracking artifacts here.

Suggested files:
- `graph-index.md`: human-readable index of graph snapshots
- `*.json`: graph exports
- `*.html`: graph visualizations
- `audit-*.md`: audit reports


## 2026-05-21 Update

### Architecture Events
- Introduced dual deployment strategy:
  - Primary: GitHub -> Render
  - Secondary: GitHub -> Hugging Face Spaces (Docker unified app)
- Added `hf_space/app.py` gateway mounting Q5/Q10/Q11/Q14/Q16/Q18/Q19.

### Reliability Events
- Fixed runtime boot failures from strict filesystem assumptions with `/tmp` fallback for Q14/Q16/Q19.
- Fixed dynamic import/Pydantic annotation resolution in unified app loader via module registration.
- Added route compatibility aliases for previously used URLs.

### Product UX Events
- Upgraded root unified UI from basic list to card-based hub navigation.
- Improved per-question UI display quality for key routes under active usage (Q11/Q16/Q19).

### Traceability
- Canonical term namespace: `T22026`.
- Context source of truth: `context/agent_context.md`.
