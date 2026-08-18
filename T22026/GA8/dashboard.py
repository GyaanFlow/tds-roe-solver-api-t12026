from __future__ import annotations

"""
T22026/GA8/dashboard.py — Interactive Web Dashboard for GA8 Hub.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
async def ga8_dashboard_view(request: Request) -> str:
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GA8 MLOps & LLM Systems Gateway | IITM TDS</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  <style>
    :root {
      --bg: #030712;
      --surface: #0f172a;
      --card-bg: rgba(17, 24, 39, 0.75);
      --border: rgba(99, 102, 241, 0.18);
      --border-hover: rgba(99, 102, 241, 0.4);
      --text: #f9fafb;
      --muted: #9ca3af;
      --accent: #6366f1;
      --accent-hover: #818cf8;
      --green: #10b981;
      --orange: #fb923c;
      --purple: #c084fc;
      --cyan: #38bdf8;
      --red: #f43f5e;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background-color: var(--bg);
      background-image:
        radial-gradient(at 0% 0%, rgba(99,102,241,.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(56,189,248,.1) 0px, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      padding: 40px 20px;
    }
    .container { width: 100%; max-width: 1100px; margin: 0 auto; }
    .header { text-align: center; margin-bottom: 40px; }
    .badge {
      display: inline-block; padding: 6px 14px; border-radius: 9999px;
      background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3);
      color: var(--accent-hover); font-size: 0.82rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 12px;
    }
    .header h1 {
      font-size: clamp(2.2rem, 5vw, 3.2rem); font-weight: 800;
      background: linear-gradient(135deg, #ffffff 30%, #38bdf8 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      margin-bottom: 10px; letter-spacing: -0.02em;
    }
    .header p { color: var(--muted); max-width: 700px; margin: 0 auto; font-size: 1.05rem; line-height: 1.6; }

    /* Student Email Control */
    .tenant-card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 16px; padding: 24px; margin-bottom: 36px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.3);
    }
    .tenant-form { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    .tenant-form input {
      flex: 1; min-width: 280px; background: rgba(0,0,0,0.4);
      border: 1px solid var(--border); border-radius: 10px; padding: 12px 16px;
      color: var(--text); font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; outline: none;
    }
    .tenant-form input:focus { border-color: var(--cyan); }
    .btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 8px;
      padding: 12px 22px; font-size: 0.9rem; font-weight: 700; border-radius: 10px;
      border: none; cursor: pointer; text-decoration: none; transition: all 0.2s;
    }
    .btn-primary { background: var(--cyan); color: #030712; }
    .btn-primary:hover { background: #7dd3fc; transform: translateY(-1px); }
    .btn-secondary { background: rgba(255,255,255,0.06); color: var(--text); border: 1px solid var(--border); }
    .btn-secondary:hover { background: rgba(255,255,255,0.12); }

    /* Section Grids */
    .section-title { font-size: 1.4rem; font-weight: 700; margin-bottom: 20px; color: #fff; display: flex; align-items: center; gap: 10px; }
    .grid { display: grid; grid-template-columns: 1fr; gap: 20px; margin-bottom: 40px; }
    @media (min-width: 768px) { .grid { grid-template-columns: repeat(2, 1fr); } }

    .card {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 16px; padding: 24px; box-shadow: 0 8px 20px rgba(0,0,0,0.25);
      display: flex; flex-direction: column; justify-content: space-between;
      transition: all 0.25s ease;
    }
    .card:hover { border-color: var(--border-hover); transform: translateY(-2px); }
    .card-meta { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
    .card-title { font-size: 1.15rem; font-weight: 700; color: #fff; margin-bottom: 8px; }
    .card-desc { font-size: 0.88rem; color: var(--muted); line-height: 1.5; margin-bottom: 16px; }

    .endpoint-box {
      background: rgba(0,0,0,0.5); border: 1px solid rgba(255,255,255,0.06);
      border-radius: 8px; padding: 10px 14px; font-family: 'JetBrains Mono', monospace;
      font-size: 0.82rem; color: var(--cyan); word-break: break-all; margin-bottom: 12px;
      display: flex; justify-content: space-between; align-items: center; gap: 8px;
    }
    .copy-btn {
      background: none; border: none; color: var(--muted); cursor: pointer;
      font-size: 1rem; padding: 4px; transition: color 0.2s;
    }
    .copy-btn:hover { color: var(--text); }

    pre {
      background: #090d16; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px;
      padding: 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem;
      color: #38bdf8; overflow-x: auto; max-height: 220px;
    }
    .footer { text-align: center; color: var(--muted); font-size: 0.85rem; margin-top: 50px; }
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <span class="badge">IITM TDS Graded Assignment 8</span>
    <h1>GA8 MLOps & LLM Systems Gateway</h1>
    <p>10 deterministic MLOps and LLM systems solvers. Live URL endpoints for Q1–Q7 policy gates, and automated calculators for Q8–Q10.</p>
  </div>

  <!-- Student Email Bar -->
  <div class="tenant-card">
    <div class="tenant-form">
      <input type="email" id="studentEmail" placeholder="Enter your student email (e.g. 23f1000805@ds.study.iitm.ac.in)" />
      <button class="btn btn-primary" onclick="updateEndpoints()"><i class="bi bi-arrow-repeat"></i> Update Endpoints</button>
    </div>
  </div>

  <!-- Live Endpoints (Q1 - Q7) -->
  <div class="section-title"><i class="bi bi-hdd-network text-info"></i> Live API Policy Endpoints (Submit base URL to exam)</div>
  <div class="grid">
    <!-- Q1 -->
    <div class="card">
      <div>
        <div class="card-meta text-info">Q1 · 1.5 Marks · POST /build-corpus</div>
        <div class="card-title">Immutable Training Corpus</div>
        <div class="card-desc">Deterministic JSONL corpus engine with RFC 3339 validation, Unicode NFKC canonicalization, deduplication, hash splitting, and Jaccard contamination guard.</div>
        <div class="endpoint-box">
          <span id="ep-q1">/ga8/{email}/build-corpus</span>
          <button class="copy-btn" onclick="copyText('ep-q1')"><i class="bi bi-clipboard"></i></button>
        </div>
      </div>
    </div>

    <!-- Q2 -->
    <div class="card">
      <div>
        <div class="card-meta text-info">Q2 · 1.5 Marks · POST /bqml</div>
        <div class="card-title">Leakage-Safe BigQuery ML Gate</div>
        <div class="card-desc">Stateful two-phase experiment gate. Selection verifies point-in-time features; evaluation enforces metric and required-slice floors.</div>
        <div class="endpoint-box">
          <span id="ep-q2">/ga8/{email}/bqml</span>
          <button class="copy-btn" onclick="copyText('ep-q2')"><i class="bi bi-clipboard"></i></button>
        </div>
      </div>
    </div>

    <!-- Q3 -->
    <div class="card">
      <div>
        <div class="card-meta text-info">Q3 · 1.25 Marks · POST /promote</div>
        <div class="card-title">MLflow Model Promotion Gate</div>
        <div class="card-desc">Deterministic model-registry promotion gate with immutable artifact digest binding, age limits, and champion improvement threshold check.</div>
        <div class="endpoint-box">
          <span id="ep-q3">/ga8/{email}/promote</span>
          <button class="copy-btn" onclick="copyText('ep-q3')"><i class="bi bi-clipboard"></i></button>
        </div>
      </div>
    </div>

    <!-- Q4 -->
    <div class="card">
      <div>
        <div class="card-meta text-info">Q4 · 2.0 Marks · POST /adapt</div>
        <div class="card-title">PEFT Adaptation Choice & Repair</div>
        <div class="card-desc">Unified PEFT solver. Priority selection over prompt_only/retrieval/lora/qlora, and loss token labeling + adapter parameter integrity repair.</div>
        <div class="endpoint-box">
          <span id="ep-q4">/ga8/{email}/adapt</span>
          <button class="copy-btn" onclick="copyText('ep-q4')"><i class="bi bi-clipboard"></i></button>
        </div>
      </div>
    </div>

    <!-- Q5 -->
    <div class="card">
      <div>
        <div class="card-meta text-info">Q5 · 1.25 Marks · POST /quantize</div>
        <div class="card-title">Quantized Model Admission Gate</div>
        <div class="card-desc">Stateful two-phase quantization gate. Freezes candidate package manifests and admits candidates meeting size, latency, and slice accuracy floors.</div>
        <div class="endpoint-box">
          <span id="ep-q5">/ga8/{email}/quantize</span>
          <button class="copy-btn" onclick="copyText('ep-q5')"><i class="bi bi-clipboard"></i></button>
        </div>
      </div>
    </div>

    <!-- Q6 -->
    <div class="card">
      <div>
        <div class="card-meta text-info">Q6 · 1.5 Marks · POST /pipeline</div>
        <div class="card-title">Content-Addressed ML Pipeline</div>
        <div class="card-desc">Stateful 6-node DAG pipeline controller with deterministic content-addressed caching, transition matrices, and receipt validation.</div>
        <div class="endpoint-box">
          <span id="ep-q6">/ga8/{email}/pipeline</span>
          <button class="copy-btn" onclick="copyText('ep-q6')"><i class="bi bi-clipboard"></i></button>
        </div>
      </div>
    </div>

    <!-- Q7 -->
    <div class="card">
      <div>
        <div class="card-meta text-info">Q7 · 1.0 Mark · POST /verify-bundle</div>
        <div class="card-title">Model Bundle & Model Card Verifier</div>
        <div class="card-desc">Untrusted bundle verifier checking inventory checksums, safetensors configs, HTML comment model card markers, and cross-manifest consistency.</div>
        <div class="endpoint-box">
          <span id="ep-q7">/ga8/{email}/verify-bundle</span>
          <button class="copy-btn" onclick="copyText('ep-q7')"><i class="bi bi-clipboard"></i></button>
        </div>
      </div>
    </div>
  </div>

  <!-- Interactive Solvers (Q8 - Q10) -->
  <div class="section-title"><i class="bi bi-cpu text-warning"></i> Automated Calculators & Solvers (Q8, Q9, Q10)</div>
  <div class="grid">
    <!-- Q8 -->
    <div class="card">
      <div>
        <div class="card-meta text-warning">Q8 · 2.0 Marks · QLoRA Parameter Audit</div>
        <div class="card-title">Per-Layer LoRA Synthesis Solver</div>
        <div class="card-desc">Computes the verified trainable parameter count and adapter disk byte size for your assigned LLaMA layer configuration.</div>
        <button class="btn btn-secondary mb-2 w-100" onclick="solveQ('q8')"><i class="bi bi-play-circle"></i> Calculate Q8 Answer</button>
        <pre id="out-q8">// Output will appear here</pre>
      </div>
    </div>

    <!-- Q9 -->
    <div class="card">
      <div>
        <div class="card-meta text-warning">Q9 · 2.5 Marks · MLflow Fingerprint Audit</div>
        <div class="card-title">PyTorch Training Loop Simulator</div>
        <div class="card-desc">Simulates the exact step-by-step training loop on your synthetic dataset and computes final loss, run ID, and trailing loss mean.</div>
        <button class="btn btn-secondary mb-2 w-100" onclick="solveQ('q9')"><i class="bi bi-play-circle"></i> Calculate Q9 Answer</button>
        <pre id="out-q9">// Output will appear here</pre>
      </div>
    </div>

    <!-- Q10 -->
    <div class="card" style="grid-column: 1 / -1;">
      <div>
        <div class="card-meta text-warning">Q10 · 2.5 Marks · Green AI Carbon Accounting</div>
        <div class="card-title">Hugging Face Model Card Carbon Frontmatter Generator</div>
        <div class="card-desc">Computes total kWh and kg CO2eq emissions for your assigned GPU run log and generates the exact YAML frontmatter block for your Hugging Face model README.md.</div>
        <button class="btn btn-secondary mb-2 w-100" onclick="solveQ('q10')"><i class="bi bi-play-circle"></i> Generate Q10 YAML Frontmatter</button>
        <pre id="out-q10">// Output will appear here</pre>
      </div>
    </div>
  </div>

  <div class="footer">
    T22026 IITM TDS Solver Gateway · Graded Assignment 8 Module
  </div>
</div>

<script>
  function getEmail() {
    return document.getElementById('studentEmail').value.trim() || '23f1000805@ds.study.iitm.ac.in';
  }

  function updateEndpoints() {
    const email = getEmail();
    localStorage.setItem('tds_ga8_email', email);
    const origin = window.location.origin;
    const encEmail = encodeURIComponent(email);
    const base = `${origin}/ga8/${encEmail}`;

    document.getElementById('ep-q1').innerText = base;
    document.getElementById('ep-q2').innerText = base;
    document.getElementById('ep-q3').innerText = base;
    document.getElementById('ep-q4').innerText = base;
    document.getElementById('ep-q5').innerText = base;
    document.getElementById('ep-q6').innerText = base;
    document.getElementById('ep-q7').innerText = base;
  }

  async function solveQ(qId) {
    const email = getEmail();
    const outBox = document.getElementById(`out-${qId}`);
    outBox.innerText = 'Calculating...';
    try {
      const res = await fetch(`/ga8/${encodeURIComponent(email)}/solve/${qId}`);
      const data = await res.json();
      if (qId === 'q8') {
        outBox.innerText = JSON.stringify({
          trainable_params: data.trainable_params,
          adapter_file_size_bytes: data.adapter_file_size_bytes
        }, null, 2);
      } else if (qId === 'q9') {
        outBox.innerText = JSON.stringify({
          final_loss: data.final_loss,
          run_id: data.run_id,
          mean_last_10_loss: data.mean_last_10_loss
        }, null, 2);
      } else if (qId === 'q10') {
        outBox.innerText = `Carbon: ${data.co2_kg} kg CO2eq (${data.energy_kWh} kWh)\n\nYAML Frontmatter:\n${data.yaml_frontmatter}`;
      }
    } catch(err) {
      outBox.innerText = 'Error: ' + err.message;
    }
  }

  function copyText(elemId) {
    const text = document.getElementById(elemId).innerText;
    navigator.clipboard.writeText(text);
    alert('Copied URL: ' + text);
  }

  window.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('tds_ga8_email') || '23f1000805@ds.study.iitm.ac.in';
    document.getElementById('studentEmail').value = saved;
    updateEndpoints();
  });
</script>
</body>
</html>"""
