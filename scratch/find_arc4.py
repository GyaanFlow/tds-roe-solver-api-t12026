with open("scratch/seedrandom.js", "r") as f:
    text = f.read()

idx = text.find("function ARC4")
if idx != -1:
    print(text[idx:idx+1500])
else:
    # Let's search for "mixkey" and see what is around it
    idx = text.find("function mixkey")
    if idx != -1:
        print(text[idx-1000:idx])
