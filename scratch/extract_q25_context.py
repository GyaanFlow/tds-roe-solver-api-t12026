from pathlib import Path

exam_path = Path(r"c:\Users\gaura\Downloads\tds-roe-solver\tds-roe-solver\exam.js")
content = exam_path.read_text(encoding="utf-8")

# Let's search for "q-vercel-latency"
pos = content.find("q-vercel-latency")
if pos != -1:
    # Print the code from 5000 characters before to 500 characters after
    start = max(0, pos - 5000)
    end = min(len(content), pos + 1000)
    print("Found! Printing block:")
    print(content[start:end])
else:
    print("Not found.")
