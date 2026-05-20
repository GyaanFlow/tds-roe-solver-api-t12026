# Q19 Dynamic API

Upload zip + email and compute replace-across-files answer dynamically.

## Endpoints
- `POST /q19/solve`
- `POST /ga0/q19/solve`
- `POST /t22026/ga0/q19/solve`
- `GET /health`

## Input
- `email`: string
- `zip_file`: zip archive

## Logic
- Extract zip safely
- Target only `file*.txt`
- Replace `IITM` -> `IIT Madras` case-insensitively
- Compute SHA256 over concatenated sorted file byte content

## Robustness
- Zip slip guard
- Upload size limit
- Temp isolated workspace per request
- Guaranteed cleanup in finally

