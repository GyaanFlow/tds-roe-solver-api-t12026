# Q5 Dynamic Code Interpreter API

Production-ready FastAPI service for T22026/GA0 Q5.

## Endpoint

- `POST /code-interpreter`
- `POST /ga0/q5/code-interpreter`
- `POST /t22026/ga0/q5/code-interpreter`
- `GET /health`

## Request

```json
{
  "code": "print('hello')",
  "aipipe_token": "<optional-if-using-header>"
}
```

You may pass token in either location:
- JSON body field: `aipipe_token`
- Header: `X-AIPipe-Token: <token>`

## Response

```json
{
  "error": [2],
  "result": "Traceback..."
}
```

- `error` is empty on successful execution.
- On failure, `error` contains likely failure line numbers.

## Local Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Render Deploy

1. Push repository to GitHub.
2. Create Render Web Service.
3. Use `T22026/GA0/Q05/render.yaml` (Blueprint) or set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2`

## Security Notes

- Do not hardcode tokens in source code.
- Client-specific AIPipe token is accepted per request.
- Execution uses a subprocess with timeout and output capture.
- For heavy production usage (lakh+ users), isolate execution in a separate worker pool/container sandbox.

