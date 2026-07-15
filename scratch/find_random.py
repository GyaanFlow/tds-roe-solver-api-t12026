with open("scratch/seedrandom.js", "r") as f:
    text = f.read()

idx = text.find("function prng")
if idx == -1:
    idx = text.find("function impl")
if idx == -1:
    idx = text.find("var ")
# Let's print the main wrapper or how random is generated
print(text[idx:idx+1500])
