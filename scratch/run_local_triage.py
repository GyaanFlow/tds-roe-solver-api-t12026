import asyncio
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from T22026.GA5.mailroom import triage_dossier_llm

token = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjMwMDEwNzdAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsImlhdCI6MTc4NDU0NjE5NSwiaXNzIjoiaHR0cHM6Ly9haXBpcGUub3JnIiwiYXVkIjoiYWlwaXBlLWFwaSIsImV4cCI6MTc4NTE1MDk5NX0.z0OlBGSfF5lSs2smoCs8X5pbTOqChUxfbGDTx2JxH6g"

import asyncio
import json
import os
import sys
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from T22026.GA5.mailroom import triage_dossier_llm

token = "eyJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6IjIzZjMwMDEwNzdAZHMuc3R1ZHkuaWl0bS5hYy5pbiIsImlhdCI6MTc4NDU0NjE5NSwiaXNzIjoiaHR0cHM6Ly9haXBpcGUub3JnIiwiYXVkIjoiYWlwaXBlLWFwaSIsImV4cCI6MTc4NTE1MDk5NX0.z0OlBGSfF5lSs2smoCs8X5pbTOqChUxfbGDTx2JxH6g"

transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\8b9c65e9-af90-47f2-a539-f7a81daafcac\.system_generated\logs\transcript_full.jsonl")
if not transcript_path.exists():
    transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\8b9c65e9-af90-47f2-a539-f7a81daafcac\.system_generated\logs\transcript.jsonl")

dossiers = []
with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        if '"dossiers"' in line:
            try:
                data = json.loads(line)
                # Check tool calls
                for tc in data.get("tool_calls", []):
                    cmd = tc.get("args", {}).get("CommandLine") or ""
                    if "mailroom" in cmd and "propose" in cmd:
                        # Extract the JSON payload from the curl/wget/python command
                        import re
                        m = re.search(r"({.*})", cmd)
                        if m:
                            parsed = json.loads(m.group(1))
                            if len(parsed.get("dossiers", [])) > 20:
                                dossiers = parsed["dossiers"]
                                break
                if dossiers:
                    break
            except Exception:
                pass

if not dossiers:
    print("No dossiers found in transcript")
    sys.exit(1)

print(f"Loaded {len(dossiers)} dossiers from transcript.")

async def run_all():
    # Let's test the first 5 dossiers
    for i, d in enumerate(dossiers[:10]):
        print(f"\n--- Dossier {d['dossierId']} ---")
        print("Objective:", d.get("objective"))
        # Print mailbox
        print("Mailbox:", d.get("mailbox"))
        # Run triage
        try:
            res = await triage_dossier_llm(d, token)
            print("Action Chosen:", res["action"])
            print("Target:", res["target"])
            print("Payload:", res["payload"])
            print("Evidence:", res["evidence"])
        except Exception as e:
            print("Failed:", e)

asyncio.run(run_all())
