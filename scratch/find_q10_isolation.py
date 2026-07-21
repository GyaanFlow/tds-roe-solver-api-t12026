import sys
from pathlib import Path

grader_path = Path(r"C:\Users\gaura\.gemini\antigravity\brain\8b9c65e9-af90-47f2-a539-f7a81daafcac\scratch\grader_source.js")
content = grader_path.read_text(encoding="utf-8")

# Let's search for "q-a2a-durable-delegate-server" or "isolation" or "404" or "403" around line 1214
lines = content.splitlines()
found = []
for i, line in enumerate(lines):
    if i >= 1100 and i <= 1400:
        if "404" in line or "403" in line or "isolation" in line or "tenant" in line or "token" in line:
            found.append((i+1, line))

print(f"Found {len(found)} lines.")
for line_no, text in found:
    sys.stdout.buffer.write(f"Line {line_no}: {text[:150]}\n".encode("utf-8"))
