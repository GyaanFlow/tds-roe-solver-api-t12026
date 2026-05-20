# Q16 Dynamic API

Upload zip + email, then API computes move/rename/hash answer for Q16.

## Endpoints
- `POST /q16/solve`
- `POST /ga0/q16/solve`
- `POST /t22026/ga0/q16/solve`
- `GET /health`

## Form fields
- `email` (string)
- `zip_file` (.zip)

## Output
Includes:
- files moved
- files renamed
- sha256 digest (`answer_sha256`)
- exam-style answer line (`answer_line`)

## Robustness
- Unsafe zip path rejection (zip-slip guard)
- Upload size limits
- Per-request isolated temp workspace
- Guaranteed cleanup (`finally` remove workspace)

## Local
```bash
cd T22026/GA0/Q16
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

