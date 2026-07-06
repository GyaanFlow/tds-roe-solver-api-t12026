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
    <!-- Q1 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q1</span> Automated Video Curation Pipeline</div>
        <span class="q-type type-submit">Submit JSON</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Filters candidate YouTube videos by duration, keyword inclusion/exclusion, and uploads date sorting.</p>
        <div class="solver-box">
          <div class="drop-zone" id="dz-q1" onclick="triggerFileSelect('file-q1')">
            Drag & Drop <strong>q-youtube-metadata-filter-server.json</strong> here or click to browse
          </div>
          <input type="file" id="file-q1" style="display:none" onchange="handleFileSelect('q1')" />
          <button class="btn btn-sec" onclick="solveQ1()">Solve Curation</button>
          
          <div class="ans-area" id="ans-q1">
            <button class="btn-copy-ans" onclick="copyText('pre-q1')">Copy</button>
            <pre><code id="pre-q1"></code></pre>
          </div>
        </div>
      </div>
    </div>

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

    <!-- Q5 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q5</span> Cosine Similarity Search</div>
        <span class="q-type type-submit">Submit JSON</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Computes 64-dimensional vector dot-product scores and resolves alpha document ties.</p>
        <div class="solver-box">
          <div class="drop-zone" id="dz-q5" onclick="triggerFileSelect('file-q5')">
            Drag & Drop <strong>q-cosine-similarity-server.json</strong> here or click to browse
          </div>
          <input type="file" id="file-q5" style="display:none" onchange="handleFileSelect('q5')" />
          <button class="btn btn-sec" onclick="solveQ5()">Solve Similarities</button>
          
          <div class="ans-area" id="ans-q5">
            <button class="btn-copy-ans" onclick="copyText('pre-q5')">Copy</button>
            <pre><code id="pre-q5"></code></pre>
          </div>
        </div>
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

    <!-- Q10 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q10</span> Proof-of-Work Nonce Hunt</div>
        <span class="q-type type-submit">Submit Nonce</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Searches for a SHA-256 leading zero bits hash match for your personalized token and difficulty.</p>
        <div class="solver-box">
          <input type="text" id="pow-token" placeholder="Your assigned Token (e.g. ds_abc123...)" />
          <input type="text" id="pow-difficulty" placeholder="Difficulty (e.g. 16)" />
          <button class="btn btn-sec" onclick="solveQ10()">Mine Nonce</button>
          
          <div class="ans-area" id="ans-q10">
            <button class="btn-copy-ans" onclick="copyText('pre-q10')">Copy</button>
            <pre><code id="pre-q10"></code></pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Q11 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q11</span> Context Window Heist</div>
        <span class="q-type type-submit">Submit JSON</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Performs sliding window recency conflict resolution over a 20,000+ token context haystack.</p>
        <div class="solver-box">
          <textarea id="heist-haystack" rows="4" placeholder="Paste your seeded context heist document content here..."></textarea>
          <button class="btn btn-sec" onclick="solveQ11()">Extract Facts</button>
          
          <div class="ans-area" id="ans-q11">
            <button class="btn-copy-ans" onclick="copyText('pre-q11')">Copy</button>
            <pre><code id="pre-q11"></code></pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Q12 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q12</span> Spin Up the CLI</div>
        <span class="q-type type-submit">Submit session.cast</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Classifies incident logs using shell piping, computing final hash validation data.</p>
        <div class="solver-box">
          <div class="drop-zone" id="dz-q12" onclick="triggerFileSelect('file-q12')">
            Drag & Drop your dataset JSON or copy-paste it here
          </div>
          <input type="file" id="file-q12" style="display:none" onchange="handleFileSelect('q12')" />
          <textarea id="cli-dataset" rows="3" style="display:none" placeholder="Or paste dataset content..."></textarea>
          <input type="text" id="cli-marker" placeholder="Your personalized marker (e.g. SPINCLI_HASH)" />
          <button class="btn btn-sec" onclick="solveQ12()">Generate Cast File</button>
          
          <div class="ans-area" id="ans-q12">
            <button class="btn-copy-ans" onclick="copyText('pre-q12')">Copy</button>
            <pre><code id="pre-q12"></code></pre>
          </div>
        </div>
      </div>
    </div>

    <!-- Q13 -->
    <div class="q-card">
      <div class="q-header">
        <div class="q-title"><span class="q-badge">Q13</span> Embedding Trapdoors</div>
        <span class="q-type type-submit">Submit JSON</span>
      </div>
      <div class="q-body">
        <p class="q-desc">Resolves lexical negations and maps query strings to the closest semantic neighbor IDs.</p>
        <div class="solver-box">
          <textarea id="trapdoors-json" rows="4" placeholder="Paste your queries and corpus JSON content here..."></textarea>
          <button class="btn btn-sec" onclick="solveQ13()">Map Neighbors</button>
          
          <div class="ans-area" id="ans-q13">
            <button class="btn-copy-ans" onclick="copyText('pre-q13')">Copy</button>
            <pre><code id="pre-q13"></code></pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

<div class="toast" id="toast">Copied!</div>

<script>
  let BASE = window.location.origin;
  let filesData = {};
  const GA3_ENDPOINTS = [
    { q: "Q1", label: "Video curation solver", path: "/solve/q1" },
    { q: "Q2", label: "Multimodal image QA API", path: "/q2" },
    { q: "Q3", label: "Fixed invoice extraction API", path: "/q3" },
    { q: "Q4", label: "Dynamic schema extraction API", path: "/q4" },
    { q: "Q5", label: "Cosine similarity solver", path: "/solve/q5" },
    { q: "Q6", label: "Korean audio dataset API", path: "/q6" },
    { q: "Q7", label: "Invoice intelligence API", path: "/q7" },
    { q: "Q8", label: "Semantic ranking API", path: "/q8" },
    { q: "Q9", label: "Word problem solver API", path: "/q9" },
    { q: "Q10", label: "Proof-of-work solver", path: "/solve/q10" },
    { q: "Q11", label: "Context heist solver", path: "/solve/q11" },
    { q: "Q12", label: "CLI cast solver", path: "/solve/q12" },
    { q: "Q13", label: "Embedding trapdoor solver", path: "/solve/q13" }
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

    setupDragDrop("dz-q1", "file-q1", "q1");
    setupDragDrop("dz-q5", "file-q5", "q5");
    setupDragDrop("dz-q12", "file-q12", "q12");
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

  function parseDataset(raw) {
    const trimmed = raw.trim();
    if (!trimmed) {
      throw new Error("empty dataset");
    }
    if (trimmed.startsWith("[")) {
      return JSON.parse(trimmed);
    }
    return trimmed.split("\\n").filter(Boolean).map((line) => JSON.parse(line));
  }

  function setupDragDrop(dzId, fileInputId, qKey) {
    try {
      const dz = document.getElementById(dzId);
      dz.addEventListener("dragover", (e) => {
        e.preventDefault();
        dz.classList.add("dragover");
      });
      dz.addEventListener("dragleave", () => {
        dz.classList.remove("dragover");
      });
      dz.addEventListener("drop", (e) => {
        e.preventDefault();
        dz.classList.remove("dragover");
        if (e.dataTransfer.files.length > 0) {
          const file = e.dataTransfer.files[0];
          readFileContent(file, dz, qKey);
        }
      });
    } catch (err) {
      console.error(err);
    }
  }

  function triggerFileSelect(inputId) {
    document.getElementById(inputId).click();
  }

  function handleFileSelect(qKey) {
    try {
      const input = document.getElementById(`file-${qKey}`);
      const dz = document.getElementById(`dz-${qKey}`);
      if (input.files.length > 0) {
        readFileContent(input.files[0], dz, qKey);
      }
    } catch (err) {
      console.error(err);
    }
  }

  function readFileContent(file, dz, qKey) {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const rawContent = e.target.result;
        if (qKey !== "q12") {
          JSON.parse(rawContent);
        }
        filesData[qKey] = rawContent;
        dz.innerHTML = `Loaded: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
      } catch (err) {
        showToast("Invalid JSON file uploaded.", true);
      }
    };
    reader.readAsText(file);
  }

  async function solveQ1() {
    if (!filesData.q1) {
      showToast("Please upload a parameters JSON file.", true);
      return;
    }
    const email = document.getElementById("student-email").value.trim();
    showToast("Solving curation pipeline...");
    try {
      const resp = await fetch(`${BASE}/ga3/${encodeURIComponent(email)}/solve/q1`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: filesData.q1
      });
      if (resp.ok) {
        const data = await resp.json();
        showAnswer("q1", data);
      } else {
        const err = await resp.json();
        showToast(err.error || "Solver failed.", true);
      }
    } catch (e) {
      showToast("Network error occurred.", true);
    }
  }

  async function solveQ5() {
    if (!filesData.q5) {
      showToast("Please upload the Cosine Similarity JSON file.", true);
      return;
    }
    const email = document.getElementById("student-email").value.trim();
    showToast("Computing similarity ranking...");
    try {
      const resp = await fetch(`${BASE}/ga3/${encodeURIComponent(email)}/solve/q5`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: filesData.q5
      });
      if (resp.ok) {
        const data = await resp.json();
        showAnswer("q5", data);
      } else {
        const err = await resp.json();
        showToast(err.error || "Solver failed.", true);
      }
    } catch (e) {
      showToast("Network error occurred.", true);
    }
  }

  async function solveQ10() {
    const token = document.getElementById("pow-token").value.trim();
    const difficulty = parseInt(document.getElementById("pow-difficulty").value.trim(), 10);
    if (!token || isNaN(difficulty)) {
      showToast("Please enter a valid token and difficulty.", true);
      return;
    }
    const email = document.getElementById("student-email").value.trim();
    showToast("Mining nonce (this may take a few seconds)...");
    try {
      const resp = await fetch(`${BASE}/ga3/${encodeURIComponent(email)}/solve/q10`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, difficulty })
      });
      if (resp.ok) {
        const data = await resp.json();
        showAnswer("q10", data.nonce);
      } else {
        showToast("Mining failed.", true);
      }
    } catch (e) {
      showToast("Network error occurred.", true);
    }
  }

  async function solveQ11() {
    const haystack = document.getElementById("heist-haystack").value.trim();
    if (!haystack) {
      showToast("Please paste the haystack content.", true);
      return;
    }
    const email = document.getElementById("student-email").value.trim();
    showToast("Extracting latest facts...");
    try {
      const resp = await fetch(`${BASE}/ga3/${encodeURIComponent(email)}/solve/q11`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ haystack })
      });
      if (resp.ok) {
        const data = await resp.json();
        showAnswer("q11", data);
      } else {
        showToast("Extraction failed.", true);
      }
    } catch (e) {
      showToast("Network error occurred.", true);
    }
  }

  async function solveQ12() {
    let datasetRaw = filesData.q12 || document.getElementById("cli-dataset").value.trim();
    const marker = document.getElementById("cli-marker").value.trim();
    if (!datasetRaw || !marker) {
      showToast("Please upload/paste dataset and enter the marker.", true);
      return;
    }
    const dataset = parseDataset(datasetRaw);
    const email = document.getElementById("student-email").value.trim();
    showToast("Generating asciinema recording...");
    try {
      const resp = await fetch(`${BASE}/ga3/${encodeURIComponent(email)}/solve/q12`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset, marker })
      });
      if (resp.ok) {
        const data = await resp.json();
        showAnswer("q12", data.session_cast);
      } else {
        showToast("Generation failed.", true);
      }
    } catch (e) {
      showToast("Network error occurred.", true);
    }
  }

  async function solveQ13() {
    const rawJson = document.getElementById("trapdoors-json").value.trim();
    if (!rawJson) {
      showToast("Please paste the trapdoors queries and corpus JSON.", true);
      return;
    }
    const email = document.getElementById("student-email").value.trim();
    showToast("Mapping neighbors...");
    try {
      const body = JSON.parse(rawJson);
      const resp = await fetch(`${BASE}/ga3/${encodeURIComponent(email)}/solve/q13`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      if (resp.ok) {
        const data = await resp.json();
        showAnswer("q13", data);
      } else {
        showToast("Mapping failed.", true);
      }
    } catch (e) {
      showToast("Network error occurred.", true);
    }
  }

  function showAnswer(qKey, data) {
    const area = document.getElementById(`ans-${qKey}`);
    const code = document.getElementById(`pre-${qKey}`);
    area.style.display = "block";

    if (qKey === "q11" && data && typeof data === "object" && data.answers) {
      const answers = data.answers;
      const items = Object.entries(answers)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([k, v]) => `<div class="answer-chip"><span>${k}</span><strong>${String(v)}</strong></div>`)
        .join("");
      area.innerHTML = `<button class="btn-copy-ans" onclick="copyText('pre-q11')">Copy</button><div class="answer-summary"><div class="answer-grid">${items}</div><pre><code id="pre-${qKey}"></code></pre></div>`;
      const summary = Object.entries(answers).sort(([a], [b]) => a.localeCompare(b)).map(([k, v]) => `${k}: ${v}`).join('\\\\n');
      document.getElementById(`pre-${qKey}`).textContent = summary;
    } else {
      code.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
    }
    showToast("Solved! Answer displayed below.");
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
