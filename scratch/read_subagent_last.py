import json
from pathlib import Path
import sys

transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\50001445-e1ea-459a-b4b2-6d095a07b45f\.system_generated\logs\transcript_full.jsonl")
if not transcript_path.exists():
    transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\50001445-e1ea-459a-b4b2-6d095a07b45f\.system_generated\logs\transcript.jsonl")

if not transcript_path.exists():
    print("Transcript not found")
    exit(1)

with open(transcript_path, "r", encoding="utf-8") as f:
    lines = [json.loads(line) for line in f]

# Print the last 3 planner responses
planner_responses = [x for x in lines if x.get("type") == "PLANNER_RESPONSE" or x.get("source") == "MODEL"]
print(f"Total model responses: {len(planner_responses)}")
for r in planner_responses[-3:]:
    sys.stdout.buffer.write(f"\n================ MODEL RESPONSE ================\n".encode("utf-8"))
    sys.stdout.buffer.write(f"{r.get('content', '')}\n".encode("utf-8"))
