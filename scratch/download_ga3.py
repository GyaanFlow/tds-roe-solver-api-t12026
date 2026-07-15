# download_ga3.py
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://exam.sanand.workers.dev/exam-tds-2026-05-ga3.js"
req = urllib.request.Request(
    url, 
    headers={'User-Agent': 'Mozilla/5.0'}
)

try:
    with urllib.request.urlopen(req, context=ctx) as response:
        html = response.read().decode('utf-8')
        with open("scratch/ga3_raw.js", "w", encoding="utf-8") as f:
            f.write(html)
        print("Success! Downloaded ga3_raw.js")
except Exception as e:
    print("Error:", e)
