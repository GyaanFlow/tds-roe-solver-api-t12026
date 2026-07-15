
var fso = new ActiveXObject("Scripting.FileSystemObject");
var file = fso.OpenTextFile("scratch/seedrandom.min.js", 1);
var seedrandom_code = file.ReadAll();
file.Close();

eval(seedrandom_code);

var email = "23f1000805@ds.study.iitm.ac.in";
var seed1 = "q-fastapi-metrics-cors-server#" + email + "#";
var rng = Math.seedrandom(seed1, { global: false });

// Let's get the internal key by re-running mixkey or getting it
function get_arc4_state(seed) {
  var mask = 256 - 1;
  var key = [];
  var stringseed = seed + '', smear = 0, j = 0;
  while (j < stringseed.length) {
    // JS: undefined * 19 is NaN, which bitwise XORs as 0. So we can just use (key[mask & j] || 0) or let JScript do NaN coercion
    key[mask & j] = mask & (smear ^= (key[mask & j] || 0) * 19) + stringseed.charCodeAt(j++);
  }
  
  var s = [];
  var i = 0;
  var j = 0;
  var t;
  var keylen = key.length;
  while (i < 256) {
    s[i] = i++;
  }
  WScript.Echo("Init s 0-9: " + s.slice(0, 10).join(", "));
  var j_list = [];
  for (i = 0; i < 256; i++) {
    if (i == 52) {
      WScript.Echo("i=52 j_before=" + j + " s[52]=" + s[52] + " key[52]=" + key[i % keylen]);
    }
    s[i] = s[j = mask & (j + key[i % keylen] + (t = s[i]))];
    s[j] = t;
    j_list.push(j);
  }
  return { s: s, i: 0, j: j, key: key };
}

var state = get_arc4_state(seed1);
WScript.Echo("key[61] value: " + state.key[61]);
WScript.Echo("key[61] type: " + typeof state.key[61]);

