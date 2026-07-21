import asyncio
import sys
import os

# Add parent directories to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from T22026.GA5.mailroom import triage_dossier_llm

dossier = {
    'dossierId': 'MD_TEST',
    'partition': 'stable_core',
    'receivedAt': '2026-01-01T00:00:00Z',
    'mailbox': 'support@example.com',
    'objective': 'Check tracking status',
    'sources': [{
        'sourceId': 'S1',
        'kind': 'email',
        'provenance': 'customer',
        'title': 'Tracking Request',
        'lines': [{'lineId': 'L1', 'text': 'Where is my order? Please check status.'}]
    }]
}

token = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjMwMDEwNzdAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsImlhdCI6MTc4NDU0NjE5NSwiaXNzIjoiaHR0cHM6Ly9haXBpcGUub3JnIiwiYXVkIjoiYWlwaXBlLWFwaSIsImV4cCI6MTc4NTE1MDk5NX0.z0OlBGSfF5lSs2smoCs8X5pbTOqChUxfbGDTx2JxH6g"

async def main():
    try:
        res = await triage_dossier_llm(dossier, token)
        print("Success:", res)
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
