import urllib.request

url = "https://raw.githubusercontent.com/HypeMonk/GA2/main/Ultimate_master/README.md"
try:
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
    print("Length of README.md:", len(html))
    with open("scratch/hype_readme.md", "w", encoding="utf-8") as f:
        f.write(html)
    print("Saved to scratch/hype_readme.md")
except Exception as e:
    print("Error:", e)
