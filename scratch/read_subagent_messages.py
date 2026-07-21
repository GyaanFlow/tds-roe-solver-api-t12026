import json
from pathlib import Path
import sys

transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\50001445-e1ea-459a-b4b2-6d095a07b45f\.system_generated\logs\transcript_full.jsonl")
if not transcript_path.exists():
    transcript_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\50001445-e1ea-459a-b4b2-6d095a07b45f\.system_generated\logs\transcript.jsonl")

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        content = data.get("content") or ""
        # Check if content has "send_message" or "Mailroom" or "Q9"
        if "send_message" in str(data.get("tool_calls")) or "Mailroom" in content:
            # Print the tool calls or the content
            for tc in data.get("tool_calls", []):
                if tc.get("name") == "send_message" or "send_message" in str(tc):
                    sys.stdout.buffer.write(f"\n================ MESSAGE ================\n".encode("utf-8"))
                    sys.stdout.buffer.write(f"{json.dumps(tc.get('args'), indent=2)}\n".encode("utf-8"))
