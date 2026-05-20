# Q18 Dynamic API

Creates dynamic Q18 setup info from email (+ optional ngrok token), and serves checker-compatible proxy headers.

## Endpoints
- `POST /q18/setup`
- `POST /ga0/q18/setup`
- `POST /t22026/ga0/q18/setup`
- `GET /api/version` (through catch-all proxy route)
- `GET /health`

## Request (setup)
```json
{"email":"you@example.com","ngrok_token":"optional"}
```

## Notes
- On Render, ngrok is typically unnecessary because your deployed URL is already public.
- If local Ollama upstream is unavailable, `/api/version` returns a safe mock version JSON with required headers.

