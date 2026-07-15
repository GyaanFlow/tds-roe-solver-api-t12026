
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

