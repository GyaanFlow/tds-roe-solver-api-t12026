# T22026/GA3/dashboard.py

DASHBOARD_HTML = """<!DOCTYPE html>
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

    /* ── HERO ── */
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

    /* ── CONTAINER ── */
    .container {
      max-width: 960px;
      margin: 0 auto;
      padding: 2rem 1.25rem 4rem;
    }

    /* ── CARD STYLING ── */
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

    /* ── INPUTS & BUTTONS ── */
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

    /* ── DYNAMIC GRID ── */
    .grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 1.5rem;
    }

    /* ── QUESTION CARD ── */
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

    /* ── INTERACTIVE SOLVER ── */
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
    }
    .btn-copy-ans:hover {
      background: rgba(255, 255, 255, 0.15);
    }

    /* ── ACTION FOOTER ── */
    .q-footer {
      background: rgba(15, 23, 42, 0.2);
      padding: 1rem 1.5rem;
      border-top: 1px solid var(--border);
      display: flex;
      gap: 0.5rem;
    }

    /* ── TOAST NOTIFICATION ── */
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
  <p> IITM TDS 2026-05 — Seeded, structured, and interactive question solvers. </p>
</div>

<div class="container">
  <!-- SETTINGS CARD -->
  <div class="card">
    <label>Credentials & Configuration</label>
    <div class="input-row">
      <input type="email" id="student-email" placeholder="23f1000000@ds.study.iitm.ac.in" value="student@example.com" />
      <input type="text" id="aipipe-token" placeholder="aipipe.org API Key (optional)" />
      <button class="btn" id="btn-save-settings" onclick="saveSettings()">⚡ Save Settings</button>
    </div>
    <p style="font-size: 0.8rem; color: var(--muted);"> Saving settings writes credentials locally to enable LLM solvers dynamically for your tenant email. </p>
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

  // Load email from localStorage if saved
  document.addEventListener("DOMContentLoaded", () => {
    const savedEmail = localStorage.getItem("student_email");
    if (savedEmail) {
      document.getElementById("student-email").value = savedEmail;
      updatePaths(savedEmail);
    }
    const savedToken = localStorage.getItem("aipipe_token");
    if (savedToken) {
      document.getElementById("aipipe-token").value = savedToken;
    }

    // Set up drag-drop event listeners
    setupDragDrop("dz-q1", "file-q1", "q1");
    setupDragDrop("dz-q5", "file-q5", "q5");
    setupDragDrop("dz-q12", "file-q12", "q12");
  });

  function updatePaths(email) {
    const enc = encodeURIComponent(email);
    for (let q = 2; q <= 9; q++) {
      if (q === 5) continue;
      const el = document.getElementById(`path-q${q}`);
      if (el) {
        el.textContent = `${BASE}/ga3/${email}/q${q}`;
      }
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

    try {
      const resp = await fetch(`${BASE}/ga3/${encodeURIComponent(email)}/config`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ aipipe_token: token })
      });
      if (resp.ok) {
        showToast("Settings saved successfully!");
      } else {
        showToast("Failed to save settings on server.", true);
      }
    } catch (e) {
      showToast("Error connecting to server.", true);
    }
  }

  function setupDragDrop(dzId, fileInputId, qKey) {
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
  }

  function triggerFileSelect(inputId) {
    document.getElementById(inputId).click();
  }

  function handleFileSelect(qKey) {
    const input = document.getElementById(`file-${qKey}`);
    const dz = document.getElementById(`dz-${qKey}`);
    if (input.files.length > 0) {
      readFileContent(input.files[0], dz, qKey);
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
        dz.innerHTML = `📄 Loaded: <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
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
    const dataset = datasetRaw.trim().split("\\n").map(l => JSON.parse(l));
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
    code.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
    showToast("Solved! Answer displayed below.");
  }

  function copyText(elId) {
    const text = document.getElementById(elId).textContent;
    navigator.clipboard.writeText(text).then(() => {
      showToast("Answer copied to clipboard!");
    });
  }

  function copyPath(elId) {
    const text = document.getElementById(elId).textContent.trim();
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
