from pathlib import Path
import re

grader_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\8b9c65e9-af90-47f2-a539-f7a81daafcac\scratch\grader_source.js")
if not grader_path.exists():
    print("Grader file not found!")
    exit(1)

content = grader_path.read_text(encoding="utf-8")

# Let's search for "q-taint-aware-agent-executor-server" or "ga5-mailroom-action-gate/v2" in the file
lines = content.splitlines()
found = []
for i, line in enumerate(lines):
    if "ga5-mailroom" in line or "Lethal-Trifecta" in line or "dossiers" in line or "scored" in line:
        found.append((i+1, line))

print(f"Found {len(found)} matching lines.")
import sys
for line_no, text in found:
    sys.stdout.buffer.write(f"Line {line_no}: {text[:150]}\n".encode("utf-8"))
