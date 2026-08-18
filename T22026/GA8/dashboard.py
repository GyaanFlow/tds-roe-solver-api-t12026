from __future__ import annotations

"""
T22026/GA8/dashboard.py — Interactive Web Dashboard for GA8 Hub.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

DASHBOARD_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>GA8 MLOps & LLM Systems Hub — IITM TDS 2026-05</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg: #030712; --surface: #0f172a; --s2: #1e293b; --border: rgba(99,102,241,0.22);
      --text: #f8fafc; --muted: #94a3b8; --accent: #6366f1; --accent-2: #818cf8;
      --cyan: #38bdf8; --green: #34d399; --red: #f87171; --orange: #fb923c;
    }
    body { font-family: 'Outfit', system-ui, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; }
    .hero { background: radial-gradient(circle at top, rgba(99,102,241,0.18) 0%, var(--bg) 70%); border-bottom: 1px solid var(--border); padding: 2.6rem 1.5rem 1.8rem; text-align: center; }
    .hero h1 { font-size: clamp(1.7rem, 5vw, 2.6rem); font-weight: 800; background: linear-gradient(135deg,#fff 30%,var(--cyan) 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.4rem; }
    .hero p { color: var(--muted); max-width: 760px; margin: 0 auto; font-size: 0.95rem; }
    .wrap { max-width: 1140px; margin: 0 auto; padding: 1.8rem 1.5rem 4rem; }

    .card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.4rem; margin-bottom: 1.4rem; }
    .card > label { display:block; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 700; margin-bottom: 0.7rem; }
    .input-row { display: flex; gap: 0.6rem; flex-wrap: wrap; }
    .input-row input { flex: 1 1 280px; padding: 0.7rem 0.9rem; border-radius: 9px; border: 1px solid var(--border); background: var(--s2); color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; }
    .input-row input:focus { outline: none; border-color: var(--cyan); }
    .btn { background: var(--cyan); color: #04121c; border: none; padding: 0.7rem 1.4rem; border-radius: 9px; font-weight: 700; cursor: pointer; font-family: inherit; }
    .btn:hover { background: #7dd3fc; color:#000; }
    .btn-sec { background: rgba(255,255,255,.05); color: var(--text); border: 1px solid rgba(255,255,255,.1); padding: 0.55rem 0.85rem; border-radius: 8px; font-size: 0.82rem; font-weight: 600; cursor: pointer; font-family: inherit; }
    .btn-sec:hover { background: rgba(255,255,255,.12); }
    .hint { font-size: 0.8rem; color: var(--muted); margin-top: 0.7rem; }

    .section-title { font-size: 1.25rem; font-weight: 700; color: #fff; margin: 1.8rem 0 1rem; display: flex; align-items: center; gap: 0.5rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 1.1rem; }
    .q-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.3rem; display: flex; flex-direction: column; gap: 0.75rem; }
    .q-head { display: flex; align-items: center; gap: 0.55rem; }
    .q-badge { background: rgba(99,102,241,0.18); color: var(--accent-2); font-weight: 800; font-size: 0.72rem; padding: 0.18rem 0.5rem; border-radius: 999px; }
    .q-title { font-weight: 700; font-size: 1rem; }
    .q-type { margin-left:auto; font-size:0.68rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:999px; }
    .type-calc { background: rgba(52,211,153,0.15); color: var(--green); }
    .type-auto { background: rgba(56,189,248,0.15); color: var(--cyan); }
    .q-desc { color: var(--muted); font-size: 0.84rem; }
    .mono { font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; background: var(--s2); border: 1px solid var(--border); border-radius: 8px; padding: 0.55rem 0.65rem; word-break: break-all; }
    .row { display: flex; gap: 0.5rem; flex-wrap: wrap; }
    .btn-test { background: var(--accent); color: #fff; border: none; padding: 0.55rem 0.8rem; border-radius: 8px; font-size: 0.82rem; font-weight: 700; cursor: pointer; flex: 1; }
    .btn-test:hover { background: var(--accent-2); }
    .btn-test:disabled { opacity: 0.5; cursor: wait; }
    .result { font-family: 'JetBrains Mono', monospace; font-size: 0.73rem; background: #000; border: 1px solid var(--border); border-radius: 8px; padding: 0.6rem; white-space: pre-wrap; word-break: break-all; max-height: 220px; overflow: auto; display: none; }
    .result.show { display: block; }
    .result.err { color: var(--red); }
    .result.ok { color: var(--green); }

    .calc-card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 1.4rem; margin-bottom: 1.1rem; }
    .calc-val { font-family: 'JetBrains Mono', monospace; font-size: 1.15rem; color: var(--green); font-weight: 700; margin: 0.4rem 0; }

    .toast { position: fixed; bottom: 24px; right: 24px; background: #10b981; color: #fff; padding: 12px 22px; border-radius: 9px; box-shadow: 0 4px 12px rgba(0,0,0,.3); font-weight: 600; opacity: 0; transform: translateY(100%); transition: opacity .3s, transform .3s; z-index: 1000; }
    .toast.show { opacity: 1; transform: translateY(0); }
    footer { text-align: center; color: var(--muted); padding: 2rem; font-size: 0.8rem; }
  </style>
</head>
<body>
  <div class="hero">
    <h1>GA8 — MLOps &amp; LLM Systems Hub</h1>
    <p>10 MLOps and LLM systems solvers: 7 deterministic policy endpoints graded via direct live HTTP calls (Corpus Builder, BQML Gate, MLflow Promotion, PEFT Adapt/Repair, Quantize Gate, Content DAG Pipeline, Model Bundle Verifier) + automated calculators for Q8, Q9, Q10.</p>
  </div>

  <div class="wrap">
    <!-- CREDENTIALS -->
    <div class="card">
      <label>Student Email Configuration</label>
      <div class="input-row">
        <input type="email" id="student-email" placeholder="23f1000000@ds.study.iitm.ac.in" autocomplete="email" />
        <button class="btn" onclick="generateUrls()">Generate URLs &amp; Calculate</button>
      </div>
      <p class="hint">All GA8 questions are pure deterministic rule engines, seeded per student email. No LLM tokens or external API keys needed.</p>
    </div>

    <!-- API ENDPOINTS -->
    <div class="section-title"><span>📡</span> Part 1: Live Policy API Endpoints (Q1 – Q7)</div>
    <div class="grid">
      <!-- Q1 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q1</span><span class="q-title">Immutable Training Corpus</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Enforces JSONL validation, NFKC normalization, deduplication, hash splitting (0–5 train, 6–7 val, 8–9 test), and Jaccard contamination rejection.</p>
        <div class="mono" id="url-q1" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q1')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ1(this)">Run test</button>
        </div>
        <pre class="result" id="res-q1"></pre>
      </div>

      <!-- Q2 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q2</span><span class="q-title">Leakage-Safe BQML Gate</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Two-phase BigQuery ML gate: feature point-in-time eligibility and trial selection in phase 1; test evaluation and slice floor checks in phase 2.</p>
        <div class="mono" id="url-q2" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q2')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ2(this)">Run test</button>
        </div>
        <pre class="result" id="res-q2"></pre>
      </div>

      <!-- Q3 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q3</span><span class="q-title">MLflow Model Promotion Gate</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Verifiable model registry promotion gate: binds artifact digests, evaluates age limits, slices, and checks champion improvement threshold.</p>
        <div class="mono" id="url-q3" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q3')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ3(this)">Run test</button>
        </div>
        <pre class="result" id="res-q3"></pre>
      </div>

      <!-- Q4 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q4</span><span class="q-title">PEFT Choice &amp; Training Repair</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Dual operation: priority adaptation selection (prompt_only &rarr; retrieval &rarr; lora &rarr; qlora), token loss labeling, and adapter parameter repair.</p>
        <div class="mono" id="url-q4" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q4')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ4(this)">Run test</button>
        </div>
        <pre class="result" id="res-q4"></pre>
      </div>

      <!-- Q5 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q5</span><span class="q-title">Quantized Model Admission Gate</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Stateful two-phase gate: candidate inventory freeze and package digest binding; aggregate and slice floor accuracy ranking.</p>
        <div class="mono" id="url-q5" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q5')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ5(this)">Run test</button>
        </div>
        <pre class="result" id="res-q5"></pre>
      </div>

      <!-- Q6 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q6</span><span class="q-title">Content-Addressed DAG Pipeline</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">6-stage content-addressed ML pipeline controller with DAG dependency keys, transition checks, receipt tokens, and atomic 409 rollback.</p>
        <div class="mono" id="url-q6" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q6')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ6(this)">Run test</button>
        </div>
        <pre class="result" id="res-q6"></pre>
      </div>

      <!-- Q7 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q7</span><span class="q-title">Verifiable Model Bundle Verifier</span><span class="q-type type-calc">no token</span></div>
        <p class="q-desc">Untrusted bundle verifier: verifies inventory digests, safetensors configs, HTML comment model card markers, and manifest consistency.</p>
        <div class="mono" id="url-q7" data-copy="">Enter email above…</div>
        <div class="row">
          <button class="btn-sec" onclick="copyUrl('url-q7')">Copy submit URL</button>
          <button class="btn-test" onclick="testQ7(this)">Run test</button>
        </div>
        <pre class="result" id="res-q7"></pre>
      </div>
    </div>

    <!-- CALCULATORS -->
    <div class="section-title"><span>⚡</span> Part 2: Automated Solvers &amp; Calculators (Q8 – Q10)</div>
    <div class="grid">
      <!-- Q8 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q8</span><span class="q-title">LoRA Parameter &amp; Size Calculator</span><span class="q-type type-auto">automated</span></div>
        <p class="q-desc">Calculates exact trainable parameter count and adapter safetensors byte size for your per-layer LLaMA LoRA assignment.</p>
        <div class="row">
          <button class="btn-test" onclick="calcQ8(this)">Calculate Q8 Answers</button>
        </div>
        <pre class="result" id="res-q8"></pre>
      </div>

      <!-- Q9 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q9</span><span class="q-title">PyTorch Training Simulation &amp; MLflow</span><span class="q-type type-auto">automated</span></div>
        <p class="q-desc">Simulates exact PyTorch gradient descent training loop with optimizer, learning rate schedule, and MLflow run ID fingerprinting.</p>
        <div class="row">
          <button class="btn-test" onclick="calcQ9(this)">Calculate Q9 Answers</button>
        </div>
        <pre class="result" id="res-q9"></pre>
      </div>

      <!-- Q10 -->
      <div class="q-card">
        <div class="q-head"><span class="q-badge">Q10</span><span class="q-title">Green AI &amp; HF Model Card Carbon</span><span class="q-type type-auto">automated</span></div>
        <p class="q-desc">Computes GPU energy (kWh), total CO2 (kg), and generates the exact Hugging Face Model Card YAML frontmatter block.</p>
        <div class="row">
          <button class="btn-test" onclick="calcQ10(this)">Calculate Q10 Answers</button>
        </div>
        <pre class="result" id="res-q10"></pre>
      </div>
    </div>

    <p class="hint" style="margin-top:1.4rem;">
      Submit the URLs above as your exam answers — the grader calls them directly. Each endpoint is dynamically isolated and deterministic per student email.
    </p>
  </div>

  <div id="toast" class="toast"></div>
  <footer>IITM TDS 2026-05 · GA8 · MLOps &amp; LLM Systems Hub</footer>

  <script>
    const ORIGIN = window.location.origin;

    function emailVal() { return (document.getElementById('student-email').value || '').trim(); }
    function encEmail() { return encodeURIComponent(emailVal() || 'student@example.com'); }

    function refreshUrls() {
      const enc = encEmail();
      setUrl('url-q1', `${ORIGIN}/ga8/${enc}/build-corpus`);
      setUrl('url-q2', `${ORIGIN}/ga8/${enc}/bqml`);
      setUrl('url-q3', `${ORIGIN}/ga8/${enc}/promote`);
      setUrl('url-q4', `${ORIGIN}/ga8/${enc}/adapt`);
      setUrl('url-q5', `${ORIGIN}/ga8/${enc}/quantize`);
      setUrl('url-q6', `${ORIGIN}/ga8/${enc}/pipeline`);
      setUrl('url-q7', `${ORIGIN}/ga8/${enc}/verify-bundle`);
    }

    function setUrl(id, url) {
      const el = document.getElementById(id);
      if (el) {
        el.textContent = url;
        el.dataset.copy = url;
      }
    }

    function generateUrls() {
      const email = emailVal();
      if (!email || !email.includes('@')) { toast('Enter a valid email address.', true); return; }
      localStorage.setItem('ga8_email', email);
      refreshUrls();
      toast('URLs updated for ' + email + '.');
    }

    function copyUrl(id) {
      const el = document.getElementById(id);
      const text = el ? (el.dataset.copy || el.textContent) : '';
      if (!text || text.startsWith('Enter email')) {
        toast('Please enter your student email first.', true);
        return;
      }
      navigator.clipboard.writeText(text).then(() => {
        toast('Copied URL to clipboard!');
      }).catch(() => {
        toast('Failed to copy', true);
      });
    }

    function toast(msg, err=false) {
      const t = document.getElementById('toast');
      t.textContent = msg;
      t.style.background = err ? '#ef4444' : '#10b981';
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2600);
    }

    function showResult(id, data, isErr=false) {
      const el = document.getElementById(id);
      if (!el) return;
      el.textContent = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
      el.className = 'result show ' + (isErr ? 'err' : 'ok');
    }

    // Live Test Runners
    async function testQ1(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/build-corpus`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            policy: { minTime: "2026-01-01T00:00:00Z", maxTime: "2026-01-02T00:00:00Z", contaminationThreshold: 0.8 },
            objects: [{
              uri: "gs://bucket/sample.jsonl", generation: "1", fetchedGeneration: "1",
              crc32c: "7a8bc5aa", schemaId: "training-v1",
              content: '{"id":"r1","entity":"User A","eventTime":"2026-01-01T10:00:00Z","revision":1,"text":"sample row"}\n'
            }]
          })
        });
        const json = await res.json();
        showResult('res-q1', json, !res.ok);
      } catch (e) {
        showResult('res-q1', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    async function testQ2(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/bqml`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            phase: "select", runId: "test-run-" + Date.now(), forbiddenFeatures: [], numTrialsLimit: 5,
            rows: [{ id: "r1", entity: "E1", eventTime: "2026-01-01T00:00:00Z", predictionTime: "2026-01-01T01:00:00Z", version: 1, split: "TRAIN", features: {"f1": {"value": "1", "availableAt": "2026-01-01T00:30:00Z"}} }],
            trials: [{ trialId: 1, status: "SUCCEEDED", evalMetric: 0.92 }]
          })
        });
        const json = await res.json();
        showResult('res-q2', json, !res.ok);
      } catch (e) {
        showResult('res-q2', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    async function testQ3(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/promote`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            asOf: "2026-01-01T12:00:00Z", championVersion: "1",
            policy: { datasetDigest: "d_hash", schemaDigest: "s_hash", maxAgeSeconds: 86400, accuracyFloor: 0.8, requiredSlices: {}, maxLatencyMs: 100, maxSizeBytes: 1000000, minImprovement: 0.05 },
            versions: [{
              version: "1", artifactDigest: "art1",
              evaluation: { createdAt: "2026-01-01T11:00:00Z", artifactDigest: "art1", datasetDigest: "d_hash", schemaDigest: "s_hash", accuracy: 0.88, latencyMs: 40, sizeBytes: 200000, slices: {} }
            }]
          })
        });
        const json = await res.json();
        showResult('res-q3', json, !res.ok);
      } catch (e) {
        showResult('res-q3', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    async function testQ4(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/adapt`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            operation: "choose",
            policy: { minQuality: 0.8, freshnessRequired: false, maxLatencyMs: 100, maxMemoryMb: 1024, maxLabeledExamples: 100, maxTotalCost: 500, horizonRequests: 1000 },
            candidates: [
              { name: "prompt_only", available: true, quality: 0.85, freshness: true, latencyMs: 50, memoryMb: 256, labeledExamples: 0, oneTimeCost: 10, recurringCost: 0.01 },
              { name: "lora", available: true, quality: 0.95, freshness: false, latencyMs: 70, memoryMb: 512, labeledExamples: 50, oneTimeCost: 50, recurringCost: 0.01 }
            ]
          })
        });
        const json = await res.json();
        showResult('res-q4', json, !res.ok);
      } catch (e) {
        showResult('res-q4', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    async function testQ5(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/quantize`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            phase: "freeze", freezeId: "test-freeze-" + Date.now(), calibrationDigest: "cal1", tokenizerDigest: "tok1", allowedUnsupportedReasons: [],
            candidates: [{ name: "int8", files: {"model.safetensors": "content"}, loadable: true, calibrationDigest: "cal1", tokenizerDigest: "tok1" }]
          })
        });
        const json = await res.json();
        showResult('res-q5', json, !res.ok);
      } catch (e) {
        showResult('res-q5', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    async function testQ6(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/pipeline`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            session: "test-session-" + Date.now(), revision: 1,
            inputs: { generation: "1", checksum: "chk", canonicalData: "data", prepareCode: "prep", prepareConfig: "cfg", trainCode: "train", trainConfig: "tcfg", runtime: "py311", evaluateCode: "eval", evaluateConfig: "ecfg", schemaDigest: "sch", publishConfig: "pcfg" },
            events: []
          })
        });
        const json = await res.json();
        showResult('res-q6', json, !res.ok);
      } catch (e) {
        showResult('res-q6', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    async function testQ7(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/verify-bundle`, {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            policy: { requiredSlices: ["critical"], license: "mit", intendedUse: "research", limitations: "none" },
            files: {}
          })
        });
        const json = await res.json();
        showResult('res-q7', json, !res.ok);
      } catch (e) {
        showResult('res-q7', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    // Calculators (Q8, Q9, Q10)
    async function calcQ8(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/solve/q8`);
        const json = await res.json();
        showResult('res-q8', {
          "Trainable Parameters": json.trainable_params,
          "Adapter Safetensors Bytes": json.adapter_file_size_bytes,
          "Layers": json.layers ? json.layers.length : 0
        }, !res.ok);
      } catch (e) {
        showResult('res-q8', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    async function calcQ9(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/solve/q9`);
        const json = await res.json();
        showResult('res-q9', {
          "Final Loss": json.final_loss,
          "Mean Last 10 Loss": json.mean_last_10_loss,
          "MLflow Run ID": json.run_id
        }, !res.ok);
      } catch (e) {
        showResult('res-q9', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    async function calcQ10(btn) {
      btn.disabled = true;
      try {
        const enc = encEmail();
        const res = await fetch(`${ORIGIN}/ga8/${enc}/solve/q10`);
        const json = await res.json();
        showResult('res-q10', {
          "Energy (kWh)": json.energy_kWh,
          "CO2 (kg)": json.co2_kg,
          "YAML Frontmatter": json.yaml_frontmatter
        }, !res.ok);
      } catch (e) {
        showResult('res-q10', { error: e.message }, true);
      } finally {
        btn.disabled = false;
      }
    }

    // Init
    window.addEventListener('DOMContentLoaded', () => {
      const saved = localStorage.getItem('ga8_email') || localStorage.getItem('ga5_email') || '';
      if (saved) {
        document.getElementById('student-email').value = saved;
        refreshUrls();
      }
    });
  </script>
</body>
</html>
"""


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def ga8_dashboard_view(request: Request) -> str:
    return DASHBOARD_HTML
