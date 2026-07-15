# T22026/GA4/dashboard.py
"""
Unified Dashboard for IITM TDS GA4 — Live RAG API hub (Q3, Q4, Q5).
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
      --bg: #030712; --surface: #0f172a; --s2: #1e293b; --border: rgba(99,102,241,0.15);
      --text: #f8fafc; --muted: #94a3b8; --accent: #818cf8; --green: #34d399; --red: #f87171;
    }
    body { font-family: 'Outfit', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    .hero { background: radial-gradient(circle at top, rgba(99,102,241,0.12) 0%, var(--bg) 70%); border-bottom: 1px solid var(--border); padding: 3rem 1.5rem 2rem; text-align: center; }
    .hero h1 { font-size: clamp(1.8rem, 5vw, 2.8rem); font-weight: 800; background: linear-gradient(135deg,#fff 30%,var(--accent) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem; }
    .hero p { color: var(--muted); max-width: 640px; margin: 0 auto; }
    .wrap { max-width: 1080px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }
    .onboard { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.5rem; margin-bottom: 2rem; }
    .onboard input { width: 100%; padding: 0.7rem 0.9rem; border-radius: 8px; border: 1px solid var(--border); background: var(--s2); color: var(--text); font-family: inherit; margin-top: 0.4rem; }
    .onboard label { font-size: 0.85rem; color: var(--muted); }
    .onboard button { margin-top: 1rem; background: var(--accent); color: #030712; border: none; padding: 0.7rem 1.4rem; border-radius: 8px; font-weight: 700; cursor: pointer; }
    .onboard button:hover { opacity: 0.9; }
    #onboardStatus { margin-top: 0.9rem; font-size: 0.85rem; color: var(--muted); }
    #onboardStatus.ok { color: var(--green); }

    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 1.1rem; }
    .q-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.4rem; display: flex; flex-direction: column; gap: 0.8rem; }
    .q-header { display: flex; align-items: center; gap: 0.6rem; }
    .q-badge { background: rgba(129,140,248,0.15); color: var(--accent); font-weight: 800; font-size: 0.75rem; padding: 0.2rem 0.55rem; border-radius: 999px; }
    .q-title { font-weight: 700; font-size: 1.02rem; }
    .q-desc { color: var(--muted); font-size: 0.85rem; }
    .mono-path { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; background: var(--s2); border: 1px solid var(--border); border-radius: 8px; padding: 0.55rem 0.7rem; word-break: break-all; }
    .row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .btn-sec { flex: 1; background: rgba(255,255,255,.05); color: var(--text); border: 1px solid rgba(255,255,255,.08); padding: 0.55rem 0.8rem; border-radius: 8px; font-size: 0.82rem; font-weight: 600; cursor: pointer; }
    .btn-sec:hover { background: rgba(255,255,255,.1); }
    .btn-test { background: var(--accent); color: #030712; border: none; padding: 0.55rem 0.8rem; border-radius: 8px; font-size: 0.82rem; font-weight: 700; cursor: pointer; flex: 1; }
    .btn-test:hover { opacity: 0.9; }
    .btn-test:disabled { opacity: 0.5; cursor: wait; }
    .result { font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; background: #000; border: 1px solid var(--border); border-radius: 8px; padding: 0.65rem; white-space: pre-wrap; word-break: break-all; max-height: 220px; overflow: auto; display: none; }
    .result.show { display: block; }
    .result.err { color: var(--red); }
    .result.ok { color: var(--green); }
    footer { text-align: center; color: var(--muted); padding: 2rem; font-size: 0.8rem; }
  </style>
</head>
<body>
  <div class="hero">
    <h1>GA4 — Live RAG API Hub</h1>
    <p>The 3 GA4 questions graded by calling a real, dynamically deployed API URL: anti-hallucination grounded QA, two-stage vector search + re-ranking, and a GraphRAG pipeline. One isolated set of URLs per student email — no shared state between students.</p>
  </div>
  <div class="wrap">
    <div class="onboard">
      <label for="emailInput">Your email</label>
      <input id="emailInput" type="email" placeholder="you@example.com" />
      <button onclick="onboard()">Generate my URLs</button>
      <div id="onboardStatus">Enter your email, then click "Run test" on any card below — each card calls your own tenant URL live and shows the real response.</div>
    </div>

    <div class="grid">
      <!-- Q3 -->
      <div class="q-card">
        <div class="q-header"><span class="q-badge">Q3</span><span class="q-title">Grounded Answer API</span></div>
        <p class="q-desc">Answers strictly from provided chunks, cites chunk IDs, refuses with "I don't know" when unanswerable.</p>
        <div class="mono-path" id="path-q3">POST /ga4/{email}/grounded-answer</div>
        <div class="row">
          <button class="btn-sec" onclick="copyPath('path-q3')">Copy URL</button>
          <button class="btn-test" onclick="testQ3(this)">Run test</button>
        </div>
        <pre class="result" id="result-q3"></pre>
      </div>

      <!-- Q4 -->
      <div class="q-card">
        <div class="q-header"><span class="q-badge">Q4</span><span class="q-title">Vector Search + Re-ranking API</span></div>
        <p class="q-desc">Metadata filter → cosine similarity top-k → re-rank via lookup table.</p>
        <div class="mono-path" id="path-q4">POST /ga4/{email}/vector-search</div>
        <div class="row">
          <button class="btn-sec" onclick="copyPath('path-q4')">Copy URL</button>
          <button class="btn-test" onclick="testQ4(this)">Run test</button>
        </div>
        <pre class="result" id="result-q4"></pre>
      </div>

      <!-- Q5 -->
      <div class="q-card">
        <div class="q-header"><span class="q-badge">Q5</span><span class="q-title">GraphRAG Pipeline</span></div>
        <p class="q-desc">Extracts entities/relationships, answers multi-hop questions over a graph, summarizes a community.</p>
        <div class="mono-path" id="path-q5">POST /ga4/{email}/extract-graph, /graph-query, /community-summary</div>
        <div class="row">
          <button class="btn-sec" onclick="copyPath('path-q5')">Copy Base URL</button>
          <button class="btn-test" onclick="testQ5(this)">Run test</button>
        </div>
        <pre class="result" id="result-q5"></pre>
      </div>
    </div>

    <p style="color:var(--muted); font-size:0.85rem; margin-top:1.5rem;">
      Submit your tenant URL for each question directly as the exam answer — the grader calls it. The other 9 GA4
      questions are pure client-side computation (paste ZIP data → get JSON answer) and are handled by a separate solver.
    </p>
  </div>
  <footer>IITM TDS 2026-05 · GA4 · Multi-tenant hub — same email always gets the same routes, works for every student independently.</footer>
  <script>
    function currentEmail() {
      return document.getElementById('emailInput').value.trim() || 'student@example.com';
    }
    function tenantBase() {
      return `${window.location.origin}/ga4/${encodeURIComponent(currentEmail())}`;
    }
    function refreshPaths() {
      const base = tenantBase();
      document.getElementById('path-q3').textContent = `POST ${base}/grounded-answer`;
      document.getElementById('path-q4').textContent = `POST ${base}/vector-search`;
      document.getElementById('path-q5').textContent = `POST ${base}/extract-graph, /graph-query, /community-summary`;
    }
    document.getElementById('emailInput').addEventListener('input', refreshPaths);
    refreshPaths();

    function copyPath(id) {
      const text = document.getElementById(id).textContent;
      navigator.clipboard.writeText(text).then(() => {
        const el = document.getElementById(id);
        const original = el.textContent;
        el.textContent = 'Copied!';
        setTimeout(() => { el.textContent = original; }, 900);
      });
    }

    async function onboard() {
      const email = currentEmail();
      const out = document.getElementById('onboardStatus');
      out.className = '';
      out.textContent = 'Generating...';
      try {
        const res = await fetch('/ga4/onboard', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Failed');
        refreshPaths();
        out.className = 'ok';
        out.textContent = `Ready. Your routes live under ${data.solver_url_prefix}`;
      } catch (e) {
        out.className = '';
        out.textContent = 'Error: ' + e.message;
      }
    }

    async function runTest(btn, resultId, path, method, body) {
      const el = document.getElementById(resultId);
      btn.disabled = true;
      el.className = 'result show';
      el.textContent = 'Calling ' + path + ' ...';
      try {
        const res = await fetch(path, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: body ? JSON.stringify(body) : undefined
        });
        const data = await res.json();
        el.className = 'result show ' + (res.ok ? 'ok' : 'err');
        el.textContent = JSON.stringify(data, null, 2);
        return data;
      } catch (e) {
        el.className = 'result show err';
        el.textContent = 'Request failed: ' + e.message;
        return null;
      } finally {
        btn.disabled = false;
      }
    }

    async function testQ3(btn) {
      await runTest(btn, 'result-q3', `${tenantBase()}/grounded-answer`, 'POST', {
        question: "What year was FAISS released?",
        chunks: [
          { chunk_id: "C1", text: "FAISS was developed by Facebook AI Research and open-sourced in 2017." },
          { chunk_id: "C2", text: "Qdrant is a vector database written in Rust, released in 2021." }
        ]
      });
    }

    async function testQ4(btn) {
      await runTest(btn, 'result-q4', `${tenantBase()}/vector-search`, 'POST', {
        query_id: "Q001",
        query_vector: [0.9, 0.1],
        top_k: 3,
        rerank_top_n: 2,
        filter: { department: "finance" },
        documents: [
          { doc_id: "D1", department: "finance", year: 2024 },
          { doc_id: "D2", department: "finance", year: 2023 },
          { doc_id: "D3", department: "hr", year: 2024 }
        ],
        embeddings: { D1: [1, 0], D2: [0.9, 0.1], D3: [1, 0] },
        reranker_scores: { Q001: { D1: 0.5, D2: 0.9 } }
      });
    }

    async function testQ5(btn) {
      const base = tenantBase();
      const graph = await runTest(btn, 'result-q5', `${base}/extract-graph`, 'POST', {
        chunk_id: "C001",
        text: "LangChain was created by Harrison Chase. LangChain integrates with OpenAI."
      });
      if (!graph) return;
      const query = await runTest(btn, 'result-q5', `${base}/graph-query`, 'POST', {
        question: "Who created the framework that integrates with OpenAI?",
        graph
      });
      const el = document.getElementById('result-q5');
      el.textContent = 'extract-graph:\n' + JSON.stringify(graph, null, 2) + '\n\ngraph-query:\n' + JSON.stringify(query, null, 2);
    }
  </script>
</body>
</html>
"""
