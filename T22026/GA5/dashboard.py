# T22026/GA5/dashboard.py
"""
Interactive GA5 dashboard — Agent Safety/Infra API hub (Q2, Q3, Q4, Q5, Q6).
Same layout as GA4: email + AIPipe token credentials, per-question cards with
token-embedded submission URLs (owner never pays), Copy-URL and live Run-test
buttons, toast notifications.
"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GA5 Live API Hub — IITM TDS 2026-05</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #030712; --surface: #0f172a; --s2: #1e293b; --border: rgba(56,189,248,0.18);
      --text: #f8fafc; --muted: #94a3b8; --accent: #38bdf8; --accent-2: #0ea5e9;
      --green: #34d399; --red: #f87171;
    }
    body { font-family: 'Outfit', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    .hero { background: radial-gradient(circle at top, rgba(56,189,248,0.14) 0%, var(--bg) 70%); border-bottom: 1px solid var(--border); padding: 2.6rem 1.5rem 1.8rem; text-align: center; }
    .hero h1 { font-size: clamp(1.7rem, 5vw, 2.6rem); font-weight: 800; background: linear-gradient(135deg,#fff 30%,var(--accent) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.4rem; }
    .hero p { color: var(--muted); max-width: 680px; margin: 0 auto; font-size: 0.95rem; }
    .wrap { max-width: 1120px; margin: 0 auto; padding: 1.8rem 1.5rem 4rem; }

    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.4rem; margin-bottom: 1.4rem; }
    .card > label { display:block; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 700; margin-bottom: 0.7rem; }
    .input-row { display: flex; gap: 0.6rem; flex-wrap: wrap; }
    .input-row input { flex: 1 1 240px; padding: 0.7rem 0.9rem; border-radius: 9px; border: 1px solid var(--border); background: var(--s2); color: var(--text); font-family: inherit; font-size: 0.9rem; }
    .input-row input:focus { outline: none; border-color: var(--accent); }
    .btn { background: var(--accent); color: #04121c; border: none; padding: 0.7rem 1.3rem; border-radius: 9px; font-weight: 700; cursor: pointer; font-family: inherit; }
    .btn:hover { background: var(--accent-2); color:#fff; }
    .btn-sec { background: rgba(255,255,255,.05); color: var(--text); border: 1px solid rgba(255,255,255,.1); padding: 0.55rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 600; cursor: pointer; font-family: inherit; }
    .btn-sec:hover { background: rgba(255,255,255,.12); }
    .hint { font-size: 0.8rem; color: var(--muted); margin-top: 0.7rem; }

    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.1rem; }
    .q-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.3rem; display: flex; flex-direction: column; gap: 0.75rem; }
    .q-head { display: flex; align-items: center; gap: 0.55rem; }
    .q-badge { background: rgba(56,189,248,0.16); color: var(--accent); font-weight: 800; font-size: 0.72rem; padding: 0.18rem 0.5rem; border-radius: 999px; }
    .q-title { font-weight: 700; font-size: 1rem; }
    .q-type { margin-left:auto; font-size:0.68rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:999px; }
    .type-llm { background: rgba(248,113,113,0.15); color: var(--red); }
    .type-calc { background: rgba(52,211,153,0.15); color: var(--green); }
    .q-desc { color: var(--muted); font-size: 0.84rem; }
    .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; background: var(--s2); border: 1px solid var(--border); border-radius: 8px; padding: 0.55rem 0.65rem; word-break: break-all; }
    .row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .btn-test { background: var(--accent); color: #04121c; border: none; padding: 0.55rem 0.8rem; border-radius: 8px; font-size: 0.82rem; font-weight: 700; cursor: pointer; flex: 1; }
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
    <h1>GA5 — Agent Safety/Infra API Hub</h1>
    <p>5 GA5 questions graded by calling a live API URL: proration billing, a pre-tool-call guardrail, a skill-safety scanner, a run-budget/loop guard, and a real MCP server. Only Q4 uses your own AIPipe token (embedded in the URL) — the owner never pays.</p>
  </div>

  <div class="wrap">
    <!-- CREDENTIALS -->
    <div class="card">
      <label>Credentials &amp; Configuration</label>
      <div class="input-row">
        <input type="email" id="student-email" placeholder="23f1000000@ds.study.iitm.ac.in" autocomplete="email" />
        <input type="password" id="aipipe-token" placeholder="aipipe.org API key (optional — improves Q4 accuracy)" autocomplete="off" />
        <button class="btn" onclick="generateUrls()">Generate URLs</button>
      </div>
      <p class="hint">Q2, Q3, Q5, Q6 need no token — they're pure deterministic policy engines, per-student seeded from your email. Q4 works without a token (heuristic scan) but is more accurate with one embedded in the URL.</p>
    </div>

    <div class="grid">
      <!-- Q2 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q2</span><span class="q-title">Proration Bug Fix</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Computes prorated billing charge for v1 (fixed 30-day divisor) and v2 (actual month length) specs.</p>
        <div class="mono" id="url-q2" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q2')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ2(this)">Run test</button>
        </div>
        <pre class="result" id="res-q2"></pre>
      </div>

      <!-- Q3 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q3</span><span class="q-title">Pre-Tool-Call Guardrail</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Allows/blocks bash, write_file, http_request calls against your seeded secret file, write dir, and allowed hosts.</p>
        <div class="mono" id="url-q3" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q3')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ3(this)">Run test</button>
        </div>
        <pre class="result" id="res-q3"></pre>
      </div>

      <!-- Q4 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q4</span><span class="q-title">Skill Safety Audit</span><span class="q-type type-llm">token improves it</span></div>
        <p class="q-desc">Scans an agent skill file for 4 vulnerability categories (secret, prompt injection, excessive permissions, unclear provenance).</p>
        <div class="mono" id="url-q4" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q4')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ4(this)">Run test</button>
        </div>
        <pre class="result" id="res-q4"></pre>
      </div>

      <!-- Q5 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q5</span><span class="q-title">Run Budget &amp; Loop Guard</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Halts on budget exhaustion or a 3x-repeat / 6-step alternating cycle; allows legitimate pagination and polling.</p>
        <div class="mono" id="url-q5" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q5')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ5(this)">Run test</button>
        </div>
        <pre class="result" id="res-q5"></pre>
      </div>

      <!-- Q6 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q6</span><span class="q-title">Live MCP Server</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Real MCP JSON-RPC endpoint exposing tool <code>solve_challenge</code>; hashes the per-call <code>X-Exam-Challenge</code> header with your email.</p>
        <div class="mono" id="url-q6" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q6')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ6(this)">Run test</button>
        </div>
        <pre class="result" id="res-q6"></pre>
      </div>
    </div>

    <p class="hint" style="margin-top:1.4rem;">
      Submit the URLs above as your exam answers — the grader calls them directly. Each is isolated per email
      (seeded from your identity), so any student can use this same hub independently.
    </p>
  </div>

  <div id="toast" class="toast"></div>
  <footer>IITM TDS 2026-05 · GA5 · Per-student seeded policies — same model as GA3/GA4, owner never pays.</footer>

  <script>
    const ORIGIN = window.location.origin;

    function emailVal() { return (document.getElementById('student-email').value || '').trim(); }
    function tokenVal() { return (document.getElementById('aipipe-token').value || '').trim(); }
    function encEmail() { return encodeURIComponent(emailVal() || 'student@example.com'); }

    function callBase() {
      const t = tokenVal();
      const b = `${ORIGIN}/ga5/${encEmail()}`;
      return t ? `${b}/${encodeURIComponent(t)}` : b;
    }

    function refreshUrls() {
      const enc = encEmail();
      const t = tokenVal();
      const tokSeg = t ? `/${encodeURIComponent(t)}` : '';
      setUrl('url-q2', `${ORIGIN}/ga5/${enc}/proration`);
      setUrl('url-q3', `${ORIGIN}/ga5/${enc}/guardrail`);
      setUrl('url-q4', `${ORIGIN}/ga5/${enc}${tokSeg}/skill-scan`);
      setUrl('url-q5', `${ORIGIN}/ga5/${enc}/budget-guard`);
      setUrl('url-q6', `${ORIGIN}/ga5/${enc}/mcp`);
    }
    function setUrl(id, url) {
      const el = document.getElementById(id);
      el.textContent = url;
      el.dataset.copy = url;
    }

    function generateUrls() {
      const email = emailVal();
      if (!email || !email.includes('@')) { toast('Enter a valid email.', true); return; }
      localStorage.setItem('ga5_email', email);
      localStorage.setItem('ga5_token', tokenVal());
      refreshUrls();
      toast('URLs ready for ' + email + '.');
    }

    function copyUrl(id) {
      const url = document.getElementById(id).dataset.copy || '';
      if (!url || url.includes('Enter ')) { toast('Generate URLs first.', true); return; }
      navigator.clipboard.writeText(url).then(() => toast('URL copied to clipboard!'));
    }

    async function runTest(btn, resId, path, payload, headers) {
      const el = document.getElementById(resId);
      btn.disabled = true;
      el.className = 'result show'; el.textContent = 'Calling ' + path + ' …';
      try {
        const r = await fetch(path, {
          method: 'POST',
          headers: Object.assign({ 'Content-Type': 'application/json' }, headers || {}),
          body: JSON.stringify(payload)
        });
        let data;
        try { data = await r.json(); } catch (e) { data = { note: '(no JSON body — HTTP ' + r.status + ')' }; }
        el.className = 'result show ' + (r.ok ? 'ok' : 'err');
        el.textContent = JSON.stringify(data, null, 2);
        return data;
      } catch (e) {
        el.className = 'result show err'; el.textContent = 'Request failed: ' + e.message;
        return null;
      } finally { btn.disabled = false; }
    }

    function testQ2(btn) {
      return runTest(btn, 'res-q2', `${ORIGIN}/ga5/${encEmail()}/proration`, {
        old_price: 10, new_price: 20, days_remaining: 15, days_in_actual_month: 28, spec: 'v2'
      });
    }

    function testQ3(btn) {
      return runTest(btn, 'res-q3', `${ORIGIN}/ga5/${encEmail()}/guardrail`, {
        tool: 'bash', command: 'sudo cat /etc/shadow'
      });
    }

    function testQ4(btn) {
      const skill = '---\nname: notes-digest\ndescription: Summarizes meeting notes.\n---\n\nUse api_key: sk-abc123def456ghijk to call the summarizer.';
      return runTest(btn, 'res-q4', callBase() + '/skill-scan', { skill });
    }

    function testQ5(btn) {
      return runTest(btn, 'res-q5', `${ORIGIN}/ga5/${encEmail()}/budget-guard`, {
        budget_tokens: 20000,
        steps: [
          { step_number: 1, tool: 'fetch_page', args: { url: 'https://example.com/1' }, tokens_used: 9000 },
          { step_number: 2, tool: 'summarize', args: { text: '...' }, tokens_used: 7000 },
          { step_number: 3, tool: 'fetch_page', args: { url: 'https://example.com/2' }, tokens_used: 5000 }
        ]
      });
    }

    async function testQ6(btn) {
      const path = `${ORIGIN}/ga5/${encEmail()}/mcp`;
      await runTest(btn, 'res-q6', path, { jsonrpc: '2.0', id: 1, method: 'initialize', params: {} });
      await runTest(btn, 'res-q6', path, { jsonrpc: '2.0', id: 2, method: 'tools/list' });
      const challenge = '0123456789abcdef0123456789abcdef';
      const result = await runTest(btn, 'res-q6', path,
        { jsonrpc: '2.0', id: 3, method: 'tools/call', params: { name: 'solve_challenge', arguments: {} } },
        { 'X-Exam-Challenge': challenge, 'X-Exam-Timestamp': String(Date.now()) }
      );
      document.getElementById('res-q6').textContent = 'tools/call result:\n' + JSON.stringify(result, null, 2);
    }

    function toast(msg, isErr = false) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.style.background = isErr ? '#ef4444' : '#10b981';
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2600);
    }

    document.getElementById('student-email').value = localStorage.getItem('ga5_email') || '';
    document.getElementById('aipipe-token').value = localStorage.getItem('ga5_token') || '';
    document.getElementById('student-email').addEventListener('input', refreshUrls);
    document.getElementById('aipipe-token').addEventListener('input', refreshUrls);
    refreshUrls();
  </script>
</body>
</html>
"""
