import urllib.request

url = "https://cdnjs.cloudflare.com/ajax/libs/seedrandom/3.0.5/seedrandom.js"
urllib.request.urlretrieve(url, "scratch/seedrandom.js")

with open("scratch/seedrandom.js", "r") as f:
    text = f.read()

idx = text.find("function mixkey")
if idx != -1:
    print(text[idx:idx+800])
else:
    print("Not found")

