import urllib.request
import subprocess
import os

# Download seedrandom.min.js
urllib.request.urlretrieve(
    "https://cdnjs.cloudflare.com/ajax/libs/seedrandom/3.0.5/seedrandom.min.js",
    "scratch/seedrandom.min.js"
)

# Write a JScript file to run in cscript
jscript_content = """
// Load seedrandom
var window = this;
var fso = new ActiveXObject("Scripting.FileSystemObject");
var file = fso.OpenTextFile("scratch/seedrandom.min.js", 1);
var seedrandom_code = file.ReadAll();
file.Close();

// Eval seedrandom to define it globally
eval(seedrandom_code);

var email = "23f1000805@ds.study.iitm.ac.in";
var seed1 = "q-fastapi-metrics-cors-server#" + email + "#";
var rng = Math.seedrandom(seed1, { global: false });

var r = "abcdefghijklmnopqrstuvwxyz0123456789";
var out = "";
for (var i = 0; i < 6; i++) {
    var idx = Math.floor(rng() * r.length);
    out += r.charAt(idx);
}

WScript.Echo("Seed: " + seed1);
WScript.Echo("AllowedOrigin suffix: " + out);

"""

with open("scratch/run_seedrandom.js", "w", encoding="utf-8") as f:
    f.write(jscript_content)

# Run via cscript
res = subprocess.run(["cscript", "//Nologo", "scratch/run_seedrandom.js"], capture_output=True, text=True)
print("CSCRIPT STDOUT:\n", res.stdout)
print("CSCRIPT STDERR:\n", res.stderr)
