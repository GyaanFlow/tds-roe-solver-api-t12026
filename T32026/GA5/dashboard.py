DASHBOARD_HTML = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>T3-2026 GA5 API Hub</title>
  <style>
    :root{color-scheme:dark;--bg:#0a1020;--panel:#121b2e;--line:#273650;--text:#e9f0ff;--muted:#9aabc4;--mint:#71e0c1;--blue:#7ab8ff;--red:#ff8585}
    *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px system-ui,sans-serif;line-height:1.55}
    main{max-width:980px;margin:auto;padding:40px 18px 64px}h1{font-size:clamp(28px,5vw,44px);margin:6px 0 10px}
    .tag{color:var(--mint);font:12px ui-monospace,monospace;text-transform:uppercase;letter-spacing:.1em}
    .card{border:1px solid var(--line);background:var(--panel);border-radius:14px;padding:18px;margin:14px 0}
    input,textarea{width:100%;background:#0a1221;color:var(--text);border:1px solid #314563;border-radius:8px;padding:10px;font:13px ui-monospace,monospace}
    button{background:#1c3c63;color:#eaf4ff;border:1px solid #35577f;border-radius:8px;padding:9px 14px;font-weight:700;cursor:pointer}
    code,.url{font:12px ui-monospace,monospace;color:#b9d5ff;overflow-wrap:anywhere}.muted{color:var(--muted);font-size:13px}
    pre{background:#070c15;border:1px solid var(--line);border-radius:8px;padding:10px;white-space:pre-wrap;word-break:break-word;max-height:260px;overflow:auto;font:12px ui-monospace,monospace;color:#c5f5e6}
    table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid var(--line);padding:7px 6px;text-align:left;vertical-align:top;font-size:13px}
  </style>
</head>
<body><main>
  <div class="tag">T3 · 2026 · GA5</div><h1>GA5 service bench</h1>
  <p class="muted">Per-student endpoints for the RAG gauntlet, the harness safety router, the Ollama rank-correlation helper and the ball tracker. Enter your exam email to get your URLs.</p>
  <div class="card"><label for="email"><b>Exam email</b></label><input id="email" type="email" placeholder="you@ds.study.iitm.ac.in"><p class="muted">Nothing is stored. Your email seeds the knowledge base and dataset exactly as the exam page does.</p></div>
  <div class="card"><div class="tag">Q1 · RAG Colosseum (2 marks)</div>
    <p class="muted">Submit the <b>base URL</b> (no /query):</p><div class="url" id="u-base">enter your email</div>
    <p><textarea id="q" rows="2">What quorum does Raft require to commit a log entry?</textarea></p>
    <button onclick="ask()">Try a question</button><pre id="r-q">Ready.</pre></div>
  <div class="card"><div class="tag">Q4 · Harness safety router (1 mark)</div>
    <p class="muted">Submit the <b>exact POST route</b>:</p><div class="url" id="u-harness">enter your email</div></div>
  <div class="card"><div class="tag">Q2 · Ollama + FAISS rank correlation (2 marks)</div>
    <p class="muted">Graded on real Ollama embeddings, so it runs on your machine. Download the script (needs <code>ollama pull nomic-embed-text</code> and <code>mxbai-embed-large</code>), run it, paste the 10×7 matrix.</p>
    <div class="url" id="u-script">enter your email</div><div class="url" id="u-data"></div></div>
  <div class="card"><div class="tag">Q3 · Track the red ball (2 marks)</div>
    <p class="muted">Computed from your signed frames URL: see the integration guide.</p></div>
</main>
<script>
const $=id=>document.getElementById(id), root=()=>location.pathname.replace(/\/$/,'');
function em(){return encodeURIComponent($('email').value.trim().toLowerCase())}
function paint(){const e=em(),h=location.origin+root();if(!e){return}
 $('u-base').textContent=`${h}/${e}`;$('u-harness').textContent=`${h}/${e}/harness`;
 $('u-script').textContent=`Script: ${h}/${e}/answers/ollama-script`;$('u-data').textContent=`Dataset: ${h}/${e}/answers/ollama-dataset`}
$('email').addEventListener('input',paint);
async function ask(){const e=em();if(!e){$('r-q').textContent='Enter your email first.';return}
 try{const r=await fetch(`${root()}/${e}/query`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:$('q').value,top_k:3})});$('r-q').textContent=JSON.stringify(await r.json(),null,2)}catch(x){$('r-q').textContent=x.message}}
</script></body></html>"""
