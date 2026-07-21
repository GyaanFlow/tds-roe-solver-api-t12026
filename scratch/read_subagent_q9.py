import json
from pathlib import Path
import sys

transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\50001445-e1ea-459a-b4b2-6d095a07b45f\.system_generated\logs\transcript.jsonl")
if not transcript_path.exists():
    print("Subagent transcript not found!")
    exit(1)

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            # Find any response content from the subagent containing "Q9" or "Mailroom"
            if data.get("type") == "PLANNER_RESPONSE" or data.get("type") == "MODEL":
                content = data.get("content") or ""
                if "Q9" in content or "Mailroom" in content:
                    # Print first 200 chars or lines
                    sys.stdout.buffer.write(f"\n--- STEP ---\n{content}\n".encode("utf-8"))
        except Exception as e:
            pass
