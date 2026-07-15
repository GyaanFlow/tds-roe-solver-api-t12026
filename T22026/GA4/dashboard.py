# T22026/GA4/dashboard.py
"""
Interactive GA4 dashboard — Live RAG API hub (Q3, Q4, Q5).
Mirrors the GA3 dashboard: email + AIPipe token credentials, per-question cards
with token-embedded submission URLs (so each caller pays with their own key),
Copy-URL and live Run-test buttons, and toast notifications.
"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GA4 Live API Hub — IITM TDS 2026-05</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #030712; --surface: #0f172a; --s2: #1e293b; --border: rgba(192,132,252,0.18);
      --text: #f8fafc; --muted: #94a3b8; --accent: #c084fc; --accent-2: #a855f7;
      --green: #34d399; --red: #f87171;
    }
    body { font-family: 'Outfit', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    .hero { background: radial-gradient(circle at top, rgba(192,132,252,0.14) 0%, var(--bg) 70%); border-bottom: 1px solid var(--border); padding: 2.6rem 1.5rem 1.8rem; text-align: center; }
    .hero h1 { font-size: clamp(1.7rem, 5vw, 2.6rem); font-weight: 800; background: linear-gradient(135deg,#fff 30%,var(--accent) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.4rem; }
    .hero p { color: var(--muted); max-width: 660px; margin: 0 auto; font-size: 0.95rem; }
    .wrap { max-width: 1080px; margin: 0 auto; padding: 1.8rem 1.5rem 4rem; }

    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.4rem; margin-bottom: 1.4rem; }
    .card > label { display:block; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 700; margin-bottom: 0.7rem; }
    .input-row { display: flex; gap: 0.6rem; flex-wrap: wrap; }
    .input-row input { flex: 1 1 240px; padding: 0.7rem 0.9rem; border-radius: 9px; border: 1px solid var(--border); background: var(--s2); color: var(--text); font-family: inherit; font-size: 0.9rem; }
    .input-row input:focus { outline: none; border-color: var(--accent); }
    .btn { background: var(--accent); color: #1a032e; border: none; padding: 0.7rem 1.3rem; border-radius: 9px; font-weight: 700; cursor: pointer; font-family: inherit; }
    .btn:hover { background: var(--accent-2); color:#fff; }
    .btn-sec { background: rgba(255,255,255,.05); color: var(--text); border: 1px solid rgba(255,255,255,.1); padding: 0.55rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 600; cursor: pointer; font-family: inherit; }
    .btn-sec:hover { background: rgba(255,255,255,.12); }
    .hint { font-size: 0.8rem; color: var(--muted); margin-top: 0.7rem; }

    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.1rem; }
    .q-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.3rem; display: flex; flex-direction: column; gap: 0.75rem; }
    .q-head { display: flex; align-items: center; gap: 0.55rem; }
    .q-badge { background: rgba(192,132,252,0.16); color: var(--accent); font-weight: 800; font-size: 0.72rem; padding: 0.18rem 0.5rem; border-radius: 999px; }
    .q-title { font-weight: 700; font-size: 1rem; }
    .q-type { margin-left:auto; font-size:0.68rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:999px; }
    .type-llm { background: rgba(248,113,113,0.15); color: var(--red); }
    .type-calc { background: rgba(52,211,153,0.15); color: var(--green); }
    .q-desc { color: var(--muted); font-size: 0.84rem; }
    .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; background: var(--s2); border: 1px solid var(--border); border-radius: 8px; padding: 0.55rem 0.65rem; word-break: break-all; }
    .row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .btn-test { background: var(--accent); color: #1a032e; border: none; padding: 0.55rem 0.8rem; border-radius: 8px; font-size: 0.82rem; font-weight: 700; cursor: pointer; flex: 1; }
    .btn-test:hover { background: var(--accent-2); color:#fff; }
    .btn-test:disabled { opacity: 0.5; cursor: wait; }
    .result { font-family: 'JetBrains Mono', monospace; font-size: 0.73rem; background: #000; border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem; white-space: pre-wrap; word-break: break-all; max-height: 220px; overflow: auto; display: none; }
    .result.show { display: block; }
    .result.err { color: var(--red); }
    .result.ok { color: var(--green); }

    .toast { position: fixed; bottom: 24px; right: 24px; background: #10b981; color: #fff; padding: 12px 22px; border-radius: 9px; box-shadow: 0 4px 12px rgba(0,0,0,.3); font-weight: 600; opacity: 0; transform: translateY(100%); transition: opacity .3s, transform .3s; z-index: 1000; }
    .toast.show { opacity: 1; transform: translateY(0); }
    footer { text-align: center; color: var(--muted); padding: 2rem; font-size: 0.8rem; }
  </style>
</head>
<body>
  <div class="hero">
    <h1>GA4 — Live RAG API Hub</h1>
    <p>The 3 GA4 questions graded by calling a live API URL: grounded QA, vector search + re-ranking, and GraphRAG. Q3 &amp; Q5 use your own AIPipe token (embedded in the URL) — the owner never pays.</p>
  </div>

  <div class="wrap">
    <!-- CREDENTIALS -->
    <div class="card">
      <label>Credentials &amp; Configuration</label>
      <div class="input-row">
        <input type="email" id="student-email" placeholder="23f1000000@ds.study.iitm.ac.in" autocomplete="email" />
        <input type="password" id="aipipe-token" placeholder="aipipe.org API key (required for Q3 &amp; Q5)" autocomplete="off" />
        <button class="btn" onclick="generateUrls()">Generate URLs</button>
      </div>
      <p class="hint">Enter your IITM email and AIPipe token, then click Generate URLs. Your token is embedded in the Q3/Q5 submission URLs so each call is billed to <em>your</em> key. Q4 needs no token.</p>
    </div>

    <div class="grid">
      <!-- Q3 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q3</span><span class="q-title">Grounded Answer API</span><span class="q-type type-llm">LLM · token</span></div>
        <p class="q-desc">Answers strictly from provided chunks, cites chunk IDs, refuses when unanswerable.</p>
        <div class="mono" id="url-q3" data-copy="">Enter email + token above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q3')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ3(this)">Run test</button>
        </div>
        <pre class="result" id="res-q3"></pre>
      </div>

      <!-- Q4 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q4</span><span class="q-title">Vector Search + Re-ranking</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Filters your seeded 500-doc corpus (generated in-memory from your email), cosine top-k, then re-ranks.</p>
        <div class="mono" id="url-q4" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q4')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ4(this)">Run test</button>
        </div>
        <pre class="result" id="res-q4"></pre>
      </div>

      <!-- Q5 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q5</span><span class="q-title">GraphRAG Pipeline</span><span class="q-type type-llm">LLM · token</span></div>
        <p class="q-desc">extract-graph → graph-query → community-summary. Submit the base URL; the grader appends the sub-paths.</p>
        <div class="mono" id="url-q5" data-copy="">Enter email + token above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q5')">Copy base URL</button>
          <button class="btn-test" onclick="testQ5(this)">Run test</button>
        </div>
        <pre class="result" id="res-q5"></pre>
      </div>
    </div>

    <p class="hint" style="margin-top:1.4rem;">
      Submit the URLs above as your exam answers — the grader calls them directly. <strong>Warm the dyno</strong>
      (click any Run test) right before checking Q3, since Render's free tier cold-starts and the grader's Q3 timeout is short.
      The other 9 GA4 questions are pure client-side computation, handled by your separate solver.
    </p>
  </div>

  <div id="toast" class="toast"></div>
  <footer>IITM TDS 2026-05 · GA4 · Per-caller token model — same as GA3, owner never pays.</footer>

  <script>
    const ORIGIN = window.location.origin;

    function emailVal() { return (document.getElementById('student-email').value || '').trim(); }
    function tokenVal() { return (document.getElementById('aipipe-token').value || '').trim(); }
    function encEmail() { return encodeURIComponent(emailVal() || 'student@example.com'); }

    // base for live test calls (token embedded so LLM calls use the caller's key)
    function callBase() {
      const t = tokenVal();
      const b = `${ORIGIN}/ga4/${encEmail()}`;
      return t ? `${b}/${encodeURIComponent(t)}` : b;
    }

    function refreshUrls() {
      const enc = encEmail();
      const t = tokenVal();
      const tokSeg = t ? `/${encodeURIComponent(t)}` : '/<YOUR_AIPIPE_TOKEN>';
      setUrl('url-q3', `${ORIGIN}/ga4/${enc}${tokSeg}/grounded-answer`);
      setUrl('url-q4', `${ORIGIN}/ga4/${enc}/vector-search`);        // no token
      setUrl('url-q5', `${ORIGIN}/ga4/${enc}${tokSeg}`);            // base URL
    }
    function setUrl(id, url) {
      const el = document.getElementById(id);
      el.textContent = url;
      el.dataset.copy = url;
    }

    function generateUrls() {
      const email = emailVal();
      if (!email || !email.includes('@')) { toast('Enter a valid email.', true); return; }
      if (!tokenVal()) { toast('Q4 ready. Add your AIPipe token for Q3 & Q5.', true); }
      localStorage.setItem('ga4_email', email);
      localStorage.setItem('ga4_token', tokenVal());
      refreshUrls();
      if (emailVal() && tokenVal()) toast('URLs ready — token embedded for Q3 & Q5.');
    }

    function copyUrl(id) {
      const url = document.getElementById(id).dataset.copy || '';
      if (!url || url.includes('<YOUR_AIPIPE_TOKEN>') || url.includes('Enter ')) { toast('Generate URLs first.', true); return; }
      navigator.clipboard.writeText(url).then(() => toast('URL copied to clipboard!'));
    }

    async function runTest(btn, resId, path, payload) {
      const el = document.getElementById(resId);
      btn.disabled = true;
      el.className = 'result show'; el.textContent = 'Calling ' + path + ' …';
      try {
        const r = await fetch(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
        const data = await r.json();
        el.className = 'result show ' + (r.ok ? 'ok' : 'err');
        el.textContent = JSON.stringify(data, null, 2);
        return data;
      } catch (e) {
        el.className = 'result show err'; el.textContent = 'Request failed: ' + e.message;
        return null;
      } finally { btn.disabled = false; }
    }

    function testQ3(btn) {
      return runTest(btn, 'res-q3', `${callBase()}/grounded-answer`, {
        question: 'What year was FAISS released?',
        chunks: [
          { chunk_id: 'C1', text: 'FAISS was developed by Facebook AI Research and open-sourced in 2017.' },
          { chunk_id: 'C2', text: 'Qdrant is a vector database written in Rust, released in 2021.' }
        ]
      });
    }

    function testQ4(btn) {
      // grader-style call: only the query; server generates the corpus from the email
      return runTest(btn, 'res-q4', `${ORIGIN}/ga4/${encEmail()}/vector-search`, {
        query_id: 'Q001',
        query_vector: Array.from({ length: 100 }, (_, i) => Math.sin(i) * 0.1),
        top_k: 10, rerank_top_n: 3,
        filter: { department: 'finance' }
      });
    }

    async function testQ5(btn) {
      const base = callBase();
      const graph = await runTest(btn, 'res-q5', `${base}/extract-graph`, {
        chunk_id: 'C001', text: 'LangChain was created by Harrison Chase. LangChain integrates with OpenAI.'
      });
      if (!graph) return;
      const query = await runTest(btn, 'res-q5', `${base}/graph-query`, {
        question: 'Who created the framework that integrates with OpenAI?', graph
      });
      document.getElementById('res-q5').textContent =
        'extract-graph:\n' + JSON.stringify(graph, null, 2) + '\n\ngraph-query:\n' + JSON.stringify(query, null, 2);
    }

    function toast(msg, isErr = false) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.style.background = isErr ? '#ef4444' : '#10b981';
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2600);
    }

    // restore + init
    document.getElementById('student-email').value = localStorage.getItem('ga4_email') || '';
    document.getElementById('aipipe-token').value = localStorage.getItem('ga4_token') || '';
    document.getElementById('student-email').addEventListener('input', refreshUrls);
    document.getElementById('aipipe-token').addEventListener('input', refreshUrls);
    refreshUrls();
  </script>
</body>
</html>
"""
