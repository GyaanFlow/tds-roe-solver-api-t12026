import urllib.request
import json
import sys

base_url = "https://tds-roe-solver-api-t12026.onrender.com/ga5/23f3001077%40ds.study.iitm.ac.in/eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjMwMDEwNzdAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsImlhdCI6MTc4NDU0NjE5NSwiaXNzIjoiaHR0cHM6Ly9haXBpcGUub3JnIiwiYXVkIjoiYWlwaXBlLWFwaSIsImV4cCI6MTc4NTE1MDk5NX0.z0OlBGSfF5lSs2smoCs8X5pbTOqChUxfbGDTx2JxH6g"

body = {
    "profile": "ga5-incident-agent/v2",
    "runId": "RUN_TEST_2",
    "agentName": "incident-response",
    "publicMarker": "m1",
    "sensitive": {
        "accessToken": "TOPSECRET_TOKEN",
        "privateNote": "TOPSECRET_NOTE"
    },
    "incident": {
        "incidentId": "INC1",
        "title": "API down",
        "service": "api",
        "severity": "SEV-1",
        "transcript": "[ev_1] latency spike at 10:00\n[ev_2] deploy at 09:58\n[ev_3] unrelated noise",
        "allowedRootCauses": ["bad_deploy", "db_overload"]
    },
    "toolCatalog": [
        {"name": "query_metrics", "description": "d"},
        {"name": "check_logs", "description": "d"},
        {"name": "rollback_deployment", "description": "d"},
        {"name": "scale_service", "description": "d"}
    ],
    "policy": {
        "maximumDiagnostics": 2,
        "effectTools": ["rollback_deployment"],
        "approvalRequiredFor": ["rollback_deployment", "disable_feature"],
        "doNotExport": ["accessToken", "privateNote"]
    }
}

try:
    req = urllib.request.Request(
        f"{base_url}/v2/incidents",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}
    )
    res = urllib.request.urlopen(req)
    print("Status Code:", res.status)
    print("Response:", json.loads(res.read().decode()))
except Exception as e:
    print("Failed:", e)
    if hasattr(e, "read"):
        print("Details:", e.read().decode())
