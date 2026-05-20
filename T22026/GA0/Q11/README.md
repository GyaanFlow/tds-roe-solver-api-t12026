# Q11 Dynamic Sentiment API

Production-ready FastAPI service for T22026/GA0 Q11 using VADER.

## Endpoints

- `POST /sentiment`
- `POST /ga0/q11/sentiment`
- `POST /t22026/ga0/q11/sentiment`
- `GET /health`

## Request

```json
{
  "sentences": ["I love this!", "This is bad", "It is okay"]
}
```

## Response

```json
{
  "results": [
    {"sentence":"I love this!","sentiment":"happy"},
    {"sentence":"This is bad","sentiment":"sad"},
    {"sentence":"It is okay","sentiment":"neutral"}
  ]
}
```

## Local Run

```bash
cd T22026/GA0/Q11
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Render Deploy

Use `render.yaml` or set:
- Root Directory: `T22026/GA0/Q11`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4`

## Scale Notes

- Multi-worker setup enabled.
- Batch and sentence-length caps protect service under heavy load.
- Stateless design is horizontally scalable.

