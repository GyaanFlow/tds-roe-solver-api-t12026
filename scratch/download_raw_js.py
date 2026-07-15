import requests

url = "https://exam.sanand.workers.dev/exam-tds-2026-05-ga2.js"
r = requests.get(url)
with open("ga2_raw.js", "w", encoding="utf-8") as f:
    f.write(r.text)
print("Saved raw file. Length:", len(r.text))
