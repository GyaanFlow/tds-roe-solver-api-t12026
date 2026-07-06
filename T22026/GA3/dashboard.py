# T22026/GA3/dashboard.py
"""
Unified Dashboard for IITM TDS GA3.
Provides interactive solvers and dynamic API URL generators.
"""

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GA3 Solvers & API Hub — IITM TDS 2026-05</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #030712;
      --surface: #0f172a;
      --s2: #1e293b;
      --s3: #334155;
      --border: rgba(99, 102, 241, 0.15);
      --border-hover: rgba(99, 102, 241, 0.35);
      --text: #f8fafc;
      --muted: #94a3b8;
      --accent: #818cf8;
      --accent-glow: rgba(129, 140, 248, 0.15);
      --green: #34d399;
      --blue: #38bdf8;
      --purple: #c084fc;
      --orange: #fb923c;
      --red: #f87171;
    }

    body {
      font-family: 'Outfit', system-ui, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      line-height: 1.5;
    }

    .hero {
      background: radial-gradient(circle at top, rgba(99, 102, 241, 0.12) 0%, var(--bg) 70%);
      border-bottom: 1px solid var(--border);
      padding: 3.5rem 1.5rem 2.5rem;
      text-align: center;
    }
    .hero h1 {
      font-size: clamp(2rem, 5vw, 3.2rem);
      font-weight: 800;
      background: linear-gradient(135deg, #ffffff 30%, var(--accent) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      margin-bottom: 0.6rem;
      letter-spacing: -0.02em;
    }
    .hero p {
      color: var(--muted);
      font-size: 1.05rem;
      max-width: 580px;
      margin: 0 auto;
    }

    .container {
      max-width: 960px;
      margin: 0 auto;
      padding: 2rem 1.25rem 4rem;
    }

    .card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 2rem;
      box-shadow: 0 4px 30px rgba(0, 0, 0, 0.4);
      margin-bottom: 2rem;
      transition: border-color 0.25s, box-shadow 0.25s;
    }
    .card:hover {
      border-color: var(--border-hover);
    }
    .card label {
      display: block;
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--muted);
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-bottom: 0.6rem;
    }

    .input-row {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
      margin-bottom: 1rem;
    }
    .input-row input {
      flex: 1;
      min-width: 260px;
      background: rgba(15, 23, 42, 0.6);
      border: 1.5px solid var(--border);
      border-radius: 12px;
      padding: 0.8rem 1.2rem;
      color: var(--text);
      font-size: 0.95rem;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
    }
    .input-row input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }
    .btn {
      background: var(--accent);
      color: var(--bg);
      border: none;
      border-radius: 12px;
      padding: 0.8rem 1.8rem;
      font-size: 0.95rem;
      font-weight: 700;
      cursor: pointer;
      transition: opacity 0.2s, transform 0.1s;
      white-space: nowrap;
    }
    .btn:hover {
      opacity: 0.9;
    }
    .btn:active {
      transform: translateY(1px);
    }
    .btn-sec {
      background: rgba(255, 255, 255, 0.05);
      color: var(--text);
      border: 1px solid var(--border);
    }
    .btn-sec:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    .q-card {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 16px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .q-header {
      background: rgba(30, 41, 59, 0.4);
      padding: 1.2rem 1.5rem;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }
    .q-title {
      font-size: 1.1rem;
      font-weight: 700;
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .q-badge {
      background: var(--accent-glow);
      color: var(--accent);
      padding: 2px 8px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-weight: 700;
      letter-spacing: 0.04em;
    }
    .q-type {
      font-size: 0.75rem;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 6px;
      font-family: 'JetBrains Mono', monospace;
    }
    .type-api {
      background: rgba(56, 189, 248, 0.1);
      color: var(--blue);
      border: 1px solid rgba(56, 189, 248, 0.2);
    }
    .type-submit {
      background: rgba(192, 132, 252, 0.1);
      color: var(--purple);
      border: 1px solid rgba(192, 132, 252, 0.2);
    }
    .q-body {
      padding: 1.5rem;
      flex: 1;
    }
    .q-desc {
      color: var(--muted);
      font-size: 0.9rem;
      margin-bottom: 1rem;
      line-height: 1.6;
    }
    .mono-path {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      background: rgba(15, 23, 42, 0.8);
      padding: 0.6rem 1rem;
      border-radius: 8px;
      color: var(--blue);
      border: 1px solid var(--border);
      overflow-x: auto;
      white-space: nowrap;
      margin-bottom: 1rem;
    }

    .solver-box {
      background: rgba(15, 23, 42, 0.4);
      border: 1px dashed var(--border);
      border-radius: 12px;
      padding: 1.2rem;
      margin-top: 1rem;
    }
    .drop-zone {
      border: 2px dashed var(--border);
      border-radius: 8px;
      padding: 1.5rem;
      text-align: center;
      cursor: pointer;
      color: var(--muted);
      transition: border-color 0.2s, background 0.2s;
      font-size: 0.9rem;
      margin-bottom: 1rem;
    }
    .drop-zone:hover, .drop-zone.dragover {
      border-color: var(--accent);
      background: rgba(129, 140, 248, 0.05);
      color: var(--text);
    }
    .solver-box textarea, .solver-box input[type="text"] {
      width: 100%;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.6rem 0.9rem;
      color: var(--text);
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      outline: none;
      margin-bottom: 1rem;
    }
    .solver-box textarea:focus, .solver-box input[type="text"]:focus {
      border-color: var(--accent);
    }
    .ans-area {
      position: relative;
      margin-top: 1rem;
      display: none;
    }
    .ans-area pre {
      background: #090d16;
      border: 1px solid var(--border);
      padding: 1rem;
      border-radius: 8px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.8rem;
      overflow-x: auto;
      max-height: 250px;
    }
    .btn-copy-ans {
      position: absolute;
      top: 8px;
      right: 8px;
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border: none;
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.72rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
      z-index: 10;
    }
    .btn-copy-ans:hover {
      background: rgba(255, 255, 255, 0.15);
    }
    .answer-summary {
      display: grid;
      gap: 0.8rem;
    }
    .answer-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 0.65rem;
    }
    .answer-chip {
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 0.8rem 0.9rem;
      background: rgba(15, 23, 42, 0.92);
    }
    .answer-chip span {
      display: block;
      font-size: 0.72rem;
      color: var(--muted);
      text-transform: uppercase;
      letter-spacing: 0.06em;
      margin-bottom: 0.25rem;
    }
    .answer-chip strong {
      font-family: 'JetBrains Mono', monospace;
      color: var(--text);
      font-size: 0.86rem;
      word-break: break-word;
    }

    .q-footer {
      background: rgba(15, 23, 42, 0.2);
      padding: 1rem 1.5rem;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 0.5rem;
    }

    .endpoint-panel {
      display: none;
      margin-bottom: 2rem;
    }
    .endpoint-head {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }
    .endpoint-title {
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--text);
    }
    .endpoint-sub {
      color: var(--muted);
      font-size: 0.82rem;
      margin-top: 0.2rem;
    }
    .endpoint-base {
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.76rem;
      color: var(--green);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.55rem 0.7rem;
      background: rgba(15, 23, 42, 0.7);
      max-width: 100%;
      overflow-x: auto;
    }
    .endpoint-list {
      display: grid;
      gap: 0.65rem;
    }
    .endpoint-row {
      display: grid;
      grid-template-columns: 56px 1fr auto;
      gap: 0.75rem;
      align-items: center;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 0.75rem;
      background: rgba(15, 23, 42, 0.45);
    }
    .endpoint-q {
      font-weight: 800;
      color: var(--accent);
      font-family: 'JetBrains Mono', monospace;
    }
    .endpoint-url {
      min-width: 0;
      overflow-x: auto;
      white-space: nowrap;
      font-family: 'JetBrains Mono', monospace;
      font-size: 0.78rem;
      color: var(--blue);
    }
    .endpoint-copy {
      padding: 0.5rem 0.75rem;
      font-size: 0.76rem;
    }
    @media (max-width: 680px) {
      .endpoint-row { grid-template-columns: 1fr; }
      .endpoint-copy { width: 100%; }
    }
    
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #10b981;
      color: #ffffff;
      padding: 12px 24px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      font-weight: 600;
      opacity: 0;
      transform: translateY(100%);
      transition: opacity 0.3s, transform 0.3s;
      z-index: 1000;
    }
    .toast.show {
      opacity: 1;
      transform: translateY(0);
    }
  </style>
</head>
<body>

<div class="hero">
  <h1>GA3 Multi-Tenant API Hub</h1>
  <p>IITM TDS 2026-05 — Seeded, structured, and interactive question solvers.</p>
</div>

<div class="container">
  <!-- SETTINGS CARD -->
  <div class="card">
    <label>Credentials & Configuration</label>
    <div class="input-row">
      <input type="email" id="student-email" placeholder="23f1000000@ds.study.iitm.ac.in" autocomplete="email" />
      <input type="password" id="aipipe-token" placeholder="aipipe.org API Key (Required for LLM API tasks)" autocomplete="off" />
      <button class="btn" id="btn-save-settings" onclick="saveSettings()">Generate URLs</button>
    </div>
    <p style="font-size: 0.8rem; color: var(--muted);">Enter your IITM email and optional AI Pipe token, then click Generate URLs to unlock your personalized endpoints.</p>
  </div>

  <!-- ENDPOINT PANEL -->
  <div class="card endpoint-panel" id="endpoint-panel">
    <div class="endpoint-head">
      <div>
        <div class="endpoint-title">Personalized GA3 API URLs</div>
        <div class="endpoint-sub" id="endpoint-sub">Save your email and token to generate your routes.</div>
      </div>
      <button class="btn btn-sec" onclick="copyAllEndpoints()">Copy All</button>
    </div>
    <div class="endpoint-base" id="endpoint-base">/ga3/{email}</div>
    <div class="endpoint-list" id="endpoint-list"></div>
  </div>

  <!-- QUESTIONS SECTION -->
  <div class="grid" id="questions-grid">
    <!-- Q2 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q2</span> Multimodal Image QA</div>
        <span class="q-type type-api">API Endpoint</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Extracts structured data and answers natural language questions from base64 document images.</p>
        <div class="mono-path" id="path-q2">POST /ga3/{email}/q2</div>
      </div>
      <div class="q-footer">
        <button class="btn btn-sec" onclick="copyPath('path-q2')">Copy URL</button>
      </div>
    </div>

    <!-- Q3 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q3</span> Fixed Schema Invoice Extraction</div>
        <span class="q-type type-api">API Endpoint</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Reads raw invoice plain text and extracts a fixed set of structured YYYY-MM-DD fields.</p>
        <div class="mono-path" id="path-q3">POST /ga3/{email}/q3</div>
      </div>
      <div class="q-footer">
        <button class="btn btn-sec" onclick="copyPath('path-q3')">Copy URL</button>
      </div>
    </div>

    <!-- Q4 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q4</span> Dynamic Schema Structured Extraction</div>
        <span class="q-type type-api">API Endpoint</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Performs structure alignment at runtime based on caller-defined dynamic type definitions.</p>
        <div class="mono-path" id="path-q4">POST /ga3/{email}/q4</div>
      </div>
      <div class="q-footer">
        <button class="btn btn-sec" onclick="copyPath('path-q4')">Copy URL</button>
      </div>
    </div>

    <!-- Q6 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q6</span> Korean Audio Dataset API</div>
        <span class="q-type type-api">API Endpoint</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Extracts tabular CSVs from base64 payloads, computing sample statistics and covariance matrices.</p>
        <div class="mono-path" id="path-q6">POST /ga3/{email}/q6</div>
      </div>
      <div class="q-footer">
        <button class="btn btn-sec" onclick="copyPath('path-q6')">Copy URL</button>
      </div>
    </div>

    <!-- Q7 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q7</span> Invoice Intelligence structured Extraction</div>
        <span class="q-type type-api">API Endpoint</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Strict exact-match parser extract and maps nested line_items, priority, and date strings.</p>
        <div class="mono-path" id="path-q7">POST /ga3/{email}/q7</div>
      </div>
      <div class="q-footer">
        <button class="btn btn-sec" onclick="copyPath('path-q7')">Copy URL</button>
      </div>
    </div>

    <!-- Q8 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q8</span> Passage Ranking (Semantic Search)</div>
        <span class="q-type type-api">API Endpoint</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Generates text-embedding-3-small vectors and ranks the top-3 closest candidates.</p>
        <div class="mono-path" id="path-q8">POST /ga3/{email}/q8</div>
      </div>
      <div class="q-footer">
        <button class="btn btn-sec" onclick="copyPath('path-q8')">Copy URL</button>
      </div>
    </div>

    <!-- Q9 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q9</span> Word-Problem Solver API</div>
        <span class="q-type type-api">API Endpoint</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Performs word-problem logic, returning step-by-step reasoning details and integer answers.</p>
        <div class="mono-path" id="path-q9">POST /ga3/{email}/q9</div>
      </div>
      <div class="q-footer">
        <button class="btn btn-sec" onclick="copyPath('path-q9')">Copy URL</button>
      </div>
    </div>
  </div>
</div>

<div class="toast" id="toast">Copied!</div>

<script>
  let BASE = window.location.origin;
  const GA3_ENDPOINTS = [
    { q: "Q2", label: "Multimodal image QA API", path: "/q2" },
    { q: "Q3", label: "Fixed invoice extraction API", path: "/q3" },
    { q: "Q4", label: "Dynamic schema extraction API", path: "/q4" },
    { q: "Q6", label: "Korean audio dataset API", path: "/q6" },
    { q: "Q7", label: "Invoice intelligence API", path: "/q7" },
    { q: "Q8", label: "Semantic ranking API", path: "/q8" },
    { q: "Q9", label: "Word problem solver API", path: "/q9" }
  ];

  function buildTenantBase(email, token = "") {
    const sessionId = localStorage.getItem("ga3_session_id");
    if (sessionId) {
      return `${BASE}/ga3/${email}/${encodeURIComponent(sessionId)}`;
    }
    if (token) {
      return `${BASE}/ga3/${email}/${encodeURIComponent(token)}`;
    }
    return `${BASE}/ga3/${email}`;
  }

  function renderEndpointPanel(email, hasToken = false) {
    try {
      const panel = document.getElementById("endpoint-panel");
      const list = document.getElementById("endpoint-list");
      const token = document.getElementById("aipipe-token").value.trim();
      const base = buildTenantBase(email, token);
      panel.style.display = "block";
      document.getElementById("endpoint-base").textContent = base;
      document.getElementById("endpoint-sub").textContent = token
        ? `Tenant ready for ${email}. Session ID embedded dynamically. No key data saved on disk!`
        : `Tenant ready for ${email}. Add an AI Pipe token for Q2, Q3, Q4, Q7, and Q9.`;
      list.innerHTML = "";
      GA3_ENDPOINTS.forEach((item, idx) => {
        const url = `${base}${item.path}`;
        const row = document.createElement("div");
        row.className = "endpoint-row";
        row.innerHTML = `
          <div class="endpoint-q">${item.q}</div>
          <div class="endpoint-url" title="${url}">${url}<div style="color:var(--muted);font-family:Outfit,sans-serif;font-size:0.72rem;margin-top:0.2rem">${item.label}</div></div>
          <button class="btn btn-sec endpoint-copy" onclick="copyEndpoint(${idx})">Copy</button>
        `;
        row.dataset.url = url;
        list.appendChild(row);
      });
    } catch (err) {
      console.error("Failed to render endpoint panel:", err);
    }
  }

  function copyEndpoint(index) {
    try {
      const row = document.querySelectorAll(".endpoint-row")[index];
      if (!row) return;
      navigator.clipboard.writeText(row.dataset.url).then(() => showToast("Endpoint copied."));
    } catch (err) {
      console.error(err);
    }
  }

  function copyAllEndpoints() {
    try {
      const urls = Array.from(document.querySelectorAll(".endpoint-row")).map((row) => row.dataset.url).join("\\n");
      if (!urls) return;
      navigator.clipboard.writeText(urls).then(() => showToast("All GA3 endpoints copied."));
    } catch (err) {
      console.error(err);
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    const savedToken = localStorage.getItem("aipipe_token") || "";
    if (savedToken) {
      document.getElementById("aipipe-token").value = savedToken;
    }
    const savedEmail = localStorage.getItem("student_email");
    if (savedEmail) {
      document.getElementById("student-email").value = savedEmail;
      updatePaths(savedEmail);
      renderEndpointPanel(savedEmail, Boolean(savedToken));
    }

    const emailInput = document.getElementById("student-email");
    const tokenInput = document.getElementById("aipipe-token");
    
    tokenInput.placeholder = "aipipe.org API Key (Required for LLM API tasks)";

    const onEnter = (event) => {
      if (event.key === "Enter") saveSettings();
    };
    emailInput.addEventListener("keydown", onEnter);
    tokenInput.addEventListener("keydown", onEnter);

    const autoUpdate = () => {
      const email = emailInput.value.trim();
      const token = tokenInput.value.trim();
      localStorage.removeItem("ga3_session_id");
      if (email && email.includes("@")) {
        localStorage.setItem("student_email", email);
        localStorage.setItem("aipipe_token", token);
        updatePaths(email);
        renderEndpointPanel(email, Boolean(token));
      }
    };
    emailInput.addEventListener("input", autoUpdate);
    tokenInput.addEventListener("input", autoUpdate);
  });

  function updatePaths(email) {
    try {
      const tokenInput = document.getElementById("aipipe-token");
      const token = tokenInput ? tokenInput.value.trim() : "";
      
      const sessionId = localStorage.getItem("ga3_session_id");
      let visualBase = "";
      let copyBase = "";
      
      if (sessionId) {
        visualBase = `${BASE}/ga3/${email}/${encodeURIComponent(sessionId)}`;
        copyBase = visualBase;
      } else if (token) {
        visualBase = `${BASE}/ga3/${email}/••••••••••••`;
        copyBase = `${BASE}/ga3/${email}/${encodeURIComponent(token)}`;
      } else {
        visualBase = `${BASE}/ga3/${email}`;
        copyBase = visualBase;
      }
      
      for (let q = 2; q <= 9; q++) {
        if (q === 5) continue;
        const el = document.getElementById(`path-q${q}`);
        if (el) {
          el.textContent = `POST ${visualBase}/q${q}`;
          el.dataset.copyUrl = `${copyBase}/q${q}`;
        }
      }
    } catch (err) {
      console.error("Failed to update paths:", err);
    }
  }

  async function saveSettings() {
    const email = document.getElementById("student-email").value.trim();
    const token = document.getElementById("aipipe-token").value.trim();
    if (!email || !email.includes("@")) {
      showToast("Please enter a valid email.", true);
      return;
    }
    localStorage.setItem("student_email", email);
    localStorage.setItem("aipipe_token", token);
    
    updatePaths(email);
    renderEndpointPanel(email, Boolean(token));

    const enc = encodeURIComponent(email);
    try {
      const requests = [
        fetch(`${BASE}/ga3/onboard`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, aipipe_token: token || null })
        })
      ];
      if (token) {
        requests.push(
          fetch(`${BASE}/ga3/${enc}/config`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ aipipe_token: token })
          })
        );
      }
      const [onboardResp] = await Promise.all(requests);
      const data = await onboardResp.json();
      if (onboardResp.ok) {
        if (data.session_id) {
          localStorage.setItem("ga3_session_id", data.session_id);
        } else {
          localStorage.removeItem("ga3_session_id");
        }
        updatePaths(email);
        renderEndpointPanel(email, Boolean(token));
        showToast(`URLs ready. Base: ${data.solver_url_prefix}`);
      } else {
        showToast(data.detail || data.error || "Token save failed (URLs still generated).", true);
      }
    } catch (e) {
      showToast("URLs generated locally. Server save failed.", true);
    }
  }

  function copyText(elId) {
    const text = document.getElementById(elId).textContent;
    navigator.clipboard.writeText(text).then(() => {
      showToast("Answer copied to clipboard!");
    });
  }

  function copyPath(elId) {
    const el = document.getElementById(elId);
    let text = el.dataset.copyUrl || el.textContent.trim();
    if (text.startsWith("POST ")) {
      text = text.substring(5).trim();
    } else if (text.startsWith("GET ")) {
      text = text.substring(4).trim();
    }
    navigator.clipboard.writeText(text).then(() => {
      showToast("URL copied to clipboard!");
    });
  }

  // Visual masking helper mapping
  function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.background = isError ? "#ef4444" : "#10b981";
    toast.classList.add("show");
    setTimeout(() => {
      toast.classList.remove("show");
    }, 2500);
  }
</script>
</body>
</html>
"""
