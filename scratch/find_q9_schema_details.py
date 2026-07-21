import sys
from pathlib import Path

grader_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\8b9c65e9-af90-47f2-a539-f7a81daafcac\scratch\grader_source.js")
content = grader_path.read_text(encoding="utf-8")

# Let's search for "no_action" or "template" or "quarantine" or "DUPLICATE"
lines = content.splitlines()
found = []
for i, line in enumerate(lines):
    if "no_action" in line or "reasonCode" in line or "DUPLICATE" in line:
        found.append((i+1, line))

print(f"Found {len(found)} lines.")
for line_no, text in found[:30]:
    sys.stdout.buffer.write(f"Line {line_no}: {text[:150]}\n".encode("utf-8"))
