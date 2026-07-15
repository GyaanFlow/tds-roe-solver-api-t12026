from pathlib import Path

exam_path = Path(r"c:\Users\gaura\Downloads\tds-roe-solver\tds-roe-solver\exam.js")
content = exam_path.read_text(encoding="utf-8")

# Let's search for "q-vercel" in the file
pos = content.find("q-vercel-latency")
if pos == -1:
    pos = content.find("vercel")

if pos != -1:
    start = max(0, pos - 300)
    end = min(len(content), pos + 8000)
    print("Found! Printing block:")
    print(content[start:end])
else:
    print("Not found.")
