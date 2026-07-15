with open("scratch/seedrandom.js", "r") as f:
    text = f.read()

idx = text.find("function tostring")
if idx != -1:
    print(text[idx:idx+500])
else:
    print("Not found")
