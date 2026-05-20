# Q14 Dynamic Image API

Rebuilds scrambled 5x5 `jigsaw.webp` to original order, then applies luminance grayscale.

## Endpoints

- `POST /rebuild-grayscale`
- `POST /ga0/q14/rebuild-grayscale`
- `POST /t22026/ga0/q14/rebuild-grayscale`
- `GET /files/{name}`
- `GET /health`

## Upload field

- multipart form-data field name: `image`
- supported input: `.webp`

## Response

Returns URLs for generated PNG (lossless) and WEBP (if lossless encoder available).

## Local

```bash
cd T22026/GA0/Q14
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Scale Notes

- Stateless processing and short CPU-bound transforms.
- Request size cap (`MAX_UPLOAD_MB`) to protect service.
- For very high traffic, store outputs in object storage and serve via CDN.

