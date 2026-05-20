# Q10 Dynamic Student API

This service is built for T22026/GA0 Q10 and serves students from `q-fastapi.csv`.

## Endpoints

- `GET /api`
- `GET /api?class=1A&class=1B`
- `GET /ga0/q10/api`
- `GET /ga0/q10/api?class=1A&class=1B`
- `GET /t22026/ga0/q10/api`
- `GET /health`

## Contract

Response format is always:

```json
{
  "students": [
    {"studentId": 101, "class": "1A"}
  ]
}
```

- Preserves CSV order.
- Supports repeated `class` query parameters.
- If no `class` is provided, returns all rows.

## Local run

```bash
cd T22026/GA0/Q10
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Render deploy

Use `render.yaml` blueprint or manually set:
- Root Directory: `T22026/GA0/Q10`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4`

## Scale notes

For lakh+ users:
- Use multiple workers (already enabled).
- Put Render behind CDN/WAF if public.
- Keep CSV static and versioned.
- Add Redis caching if you later move to large mutable datasets.

