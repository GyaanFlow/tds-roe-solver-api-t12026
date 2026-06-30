---
title: TDS ROE Solver API T12026
emoji: 🚀
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# TDS Exam Workspace


Future-proof workspace for term-wise, GA-wise, and question-wise tracking.

## Structure

- `T22026/GA0/Qxx/` : per-question work area
- `context/agent_context.md` : cumulative execution/context log
- `context/graphify/` : graphify artifacts and graph snapshots
- `templates/` : reusable scaffolds for new terms/GAs/questions

## Naming Convention

- Term: `TYYYY` (example: `T22026`)
- GA: `GA0`, `GA1`, ...
- Question: `Q01`, `Q02`, ...

## Workflow

1. Create new term folder (`T2027`).
2. Add GA folder (`GA1`).
3. Add question folders (`Q01...QNN`).
4. Update `context/agent_context.md` with milestones and decisions.
5. Save graph context snapshots in `context/graphify/`.
