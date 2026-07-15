# GA3 Questions Details

## Q1: Automated Video Curation Pipeline (q-youtube-metadata-filter-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p>
        The IITM Online Degree Curation Cell is building an automated video recommendation engine.
        Your task is to write a script to filter a list of candidate YouTube videos using their metadata (which you can fetch using <code>yt-dlp</code>) and return a sorted list of URLs.
      </p>

      <svg viewBox="0 0 760 200" width="100%" style="margin: 24px 0; max-width: 960px; display: block; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);" xmlns="http://www.w3.org/2000/svg">
        <!-- Grid pattern background -->
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f1f5f9" stroke-width="1" />
          </pattern>
          <linearGradient id="youtubeGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#ff0000" />
            <stop offset="100%" stop-color="#cc0000" />
          </linearGradient>
          <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.08" />
          </filter>
          <marker id="glow-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
          </marker>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" rx="12" />

        <!-- SECTION 1: YouTube Videos & Playlist Input (Left) -->
        <g transform="translate(25, 20)" filter="url(#shadow)">
          <!-- Playlist Card -->
          <rect x="0" y="0" width="150" height="160" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" />
          <rect x="0" y="0" width="150" height="24" rx="8" fill="#fee2e2" />
          <path d="M0,24 L150,24" stroke="#fca5a5" stroke-width="1" />
          <!-- YouTube Play Icon -->
          <rect x="8" y="5" width="14" height="14" rx="3" fill="url(#youtubeGrad)" />
          <polygon points="13,9 13,15 18,12" fill="#ffffff" transform="scale(0.7) translate(5, 4)" />
          <text x="142" y="16" font-family="system-ui, -apple-system, sans-serif" font-size="9" font-weight="600" fill="#991b1b" text-anchor="end">source_urls</text>

          <!-- Playlist items -->
          <g transform="translate(10, 35)">
            <!-- Item 1 -->
            <rect x="0" y="0" width="130" height="34" rx="4" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />
            <rect x="6" y="6" width="35" height="22" rx="2" fill="#e2e8f0" />
            <polygon points="21,13 21,21 28,17" fill="#64748b" />
            <text x="48" y="15" font-family="system-ui, sans-serif" font-size="8" font-weight="bold" fill="#0f172a">PySpark Tutorial</text>
            <text x="48" y="24" font-family="system-ui, sans-serif" font-size="7" fill="#64748b">freeCodeCamp.org</text>
            <text x="124" y="24" font-family="system-ui, sans-serif" font-size="7" fill="#64748b" text-anchor="end">14:20</text>

            <!-- Item 2 -->
            <rect x="0" y="40" width="130" height="34" rx="4" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />
            <rect x="6" y="6" width="35" height="22" rx="2" fill="#e2e8f0" transform="translate(0, 40)" />
            <polygon points="21,13 21,21 28,17" fill="#64748b" transform="translate(0, 40)" />
            <text x="48" y="55" font-family="system-ui, sans-serif" font-size="8" font-weight="bold" fill="#0f172a">Working with APIs</text>
            <text x="48" y="65" font-family="system-ui, sans-serif" font-size="7" fill="#64748b">John Watson Rooney</text>
            <text x="124" y="64" font-family="system-ui, sans-serif" font-size="7" fill="#64748b" text-anchor="end">02:15</text>

            <!-- Item 3 -->
            <rect x="0" y="80" width="130" height="34" rx="4" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />
            <rect x="6" y="6" width="35" height="22" rx="2" fill="#e2e8f0" transform="translate(0, 80)" />
            <polygon points="21,13 21,21 28,17" fill="#64748b" transform="translate(0, 80)" />
            <text x="48" y="95" font-family="system-ui, sans-serif" font-size="8" font-weight="bold" fill="#0f172a">Logging Basics</text>
            <text x="48" y="105" font-family="system-ui, sans-serif" font-size="7" fill="#64748b">Corey Schafer</text>
            <text x="124" y="104" font-family="system-ui, sans-serif" font-size="7" fill="#64748b" text-anchor="end">45:10</text>
          </g>
        </g>

        <!-- Connection 1 -->
        <path d="M 190 100 L 225 100" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#glow-arrow)" />

        <!-- SECTION 2: Processing Engine (Middle) -->
        <g transform="translate(240, 20)" filter="url(#shadow)">
          <!-- Pipeline Box -->
          <rect x="0" y="0" width="260" height="160" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" />
          <rect x="0" y="0" width="260" height="24" rx="8" fill="#f8fafc" />
          <path d="M0,24 L260,24" stroke="#e2e8f0" stroke-width="1" />
          <text x="15" y="16" font-family="system-ui, sans-serif" font-size="9" font-weight="bold" fill="#475569">LOCAL CURATION PIPELINE</text>
          
          <!-- Steps -->
          <g transform="translate(15, 35)">
            <!-- Step 1 -->
            <rect x="0" y="0" width="230" height="34" rx="4" fill="#f1f5f9" />
            <text x="10" y="15" font-family="system-ui, sans-serif" font-size="9" font-weight="bold" fill="#0f172a">1. yt-dlp Metadata Extraction</text>
            <text x="10" y="27" font-family="monospace" font-size="8" fill="#475569">yt-dlp --dump-json "URL"</text>

            <!-- Step 2 -->
            <rect x="0" y="40" width="230" height="34" rx="4" fill="#f1f5f9" />
            <text x="10" y="55" font-family="system-ui, sans-serif" font-size="9" font-weight="bold" fill="#0f172a">2. Filter: Duration &amp; Keywords</text>
            <text x="10" y="67" font-family="system-ui, sans-serif" font-size="8" fill="#475569">300s &lt;= duration &lt;= 2400s; contains "python"</text>

            <!-- Step 3 -->
            <rect x="0" y="80" width="230" height="34" rx="4" fill="#f1f5f9" />
            <text x="10" y="95" font-family="system-ui, sans-serif" font-size="9" font-weight="bold" fill="#0f172a">3. Sort &amp; Limit Selection</text>
            <text x="10" y="107" font-family="system-ui, sans-serif" font-size="8" fill="#475569">date DESC, id ASC | top N URLs</text>
          </g>
        </g>

        <!-- Connection 2 -->
        <path d="M 515 100 L 545 100" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#glow-arrow)" />

        <!-- SECTION 3: Final Output JSON (Right) -->
        <g transform="translate(560, 25)" filter="url(#shadow)">
          <!-- JSON Card -->
          <rect x="0" y="0" width="175" height="150" rx="8" fill="#0f172a" />
          <rect x="0" y="0" width="175" height="26" rx="8" fill="#1e293b" />
          <text x="15" y="17" font-family="monospace" font-size="10" font-weight="bold" fill="#38bdf8">output.json</text>
          
          <!-- JSON Content -->
          <text x="15" y="50" font-family="monospace" font-size="9" fill="#e2e8f0">{</text>
          <text x="30" y="68" font-family="monospace" font-size="9" fill="#f43f5e">"urls"</text>
          <text x="70" y="68" font-family="monospace" font-size="9" fill="#e2e8f0">:</text>
          <text x="80" y="68" font-family="monospace" font-size="9" fill="#e2e8f0">[</text>
          <text x="45" y="86" font-family="monospace" font-size="9" fill="#34d399">"youtube.com/watch?v=..."</text>
          <text x="45" y="104" font-family="monospace" font-size="9" fill="#34d399">"youtube.com/watch?v=..."</text>
          <text x="30" y="122" font-family="monospace" font-size="9" fill="#e2e8f0">]</text>
          <text x="15" y="140" font-family="monospace" font-size="9" fill="#e2e8f0">}</text>
        </g>
      </svg>

      <p><strong>Curation Rules:</strong></p>
      <ol>
        <li><strong>Metadata Extraction:</strong> Fetch the metadata for every URL in <code>source_urls</code>. <small class="text-muted">(Tip: Use <code>yt-dlp --dump-json "URL"</code> to get metadata without downloading the video.)</small></li>
        <li><strong>Duration:</strong> Keep only videos with a duration (in seconds) between <code>min_duration_seconds</code> and <code>max_duration_seconds</code> (inclusive).</li>
        <li><strong>Inclusion:</strong> Keep only videos where both the <code>title</code> and <code>description</code> (combined, case-insensitive) contain <strong>all</strong> words in <code>required_words</code>.</li>
        <li><strong>Exclusion:</strong> Exclude any video where the <code>title</code> or <code>description</code> (case-insensitive) contains <strong>any</strong> word in <code>forbidden_words</code>.</li>
        <li><strong>Sorting:</strong> Sort the filtered videos by <code>upload_date</code> descending (newest first). Resolve ties by sorting the YouTube video <code>id</code> alphabetically ascending.</li>
        <li><strong>Limit:</strong> Return only the top <code>limit</code> video URLs.</li>
      </ol>

      <p>
        <strong>Step 1:</strong> Download your task parameters:
        <button class="btn btn-sm btn-outline-primary ms-2" type="button" @click=${()=>L(i,t+".json")}>
          Download ${t}.json
        </button>
      </p>

      <p><strong>Step 2:</strong> Run your script locally and generate the final list of URLs.</p>

      <div class="mb-3">
        <label for="${t}" class="form-label"><strong>Step 3: Submit the curated playlist (JSON):</strong></label>
        <textarea class="form-control font-monospace" id="${t}" name="${t}" rows="5" placeholder='{
  "urls": [
    "https://www.youtube.com/watch?v=...",
    "https://www.youtube.com/watch?v=..."
  ]
}'></textarea>
      </div>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:c,weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Unable to verify response.");return s}
}
```

----------------------------------------

## Q2: Multimodal Image Question-Answering API (q-multimodal-image-qa-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p>
        <strong>Scenario:</strong> The <em>IITM Online Degree Curation Cell</em> is automating the extraction of data from scanned academic and administrative documents—including sales charts, receipts, invoices, tables, and pie charts.
        Your task is to build and deploy a <strong>Multimodal QA API</strong> that accepts a base64-encoded image and a question, and returns the answer extracted from the image.
      </p>

      <svg viewBox="0 0 760 200" width="100%" style="margin: 24px 0; max-width: 960px; display: block; background: #fafafa; border: 1px solid #e2e8f0; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);" xmlns="http://www.w3.org/2000/svg">
        <!-- Grid pattern background -->
        <defs>
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f1f5f9" stroke-width="1" />
          </pattern>
          <linearGradient id="blueGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#3b82f6" />
            <stop offset="100%" stop-color="#1d4ed8" />
          </linearGradient>
          <linearGradient id="greenGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#10b981" />
            <stop offset="100%" stop-color="#047857" />
          </linearGradient>
          <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
            <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.08" />
          </filter>
          <marker id="glow-arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
            <path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b" />
          </marker>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" rx="12" />

        <!-- SECTION 1: Document Image (Left) -->
        <g transform="translate(30, 20)" filter="url(#shadow)">
          <!-- Document Card -->
          <rect x="0" y="0" width="140" height="160" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5" />
          <rect x="0" y="0" width="140" height="24" rx="8" fill="#f8fafc" />
          <path d="M0,24 L140,24" stroke="#e2e8f0" stroke-width="1" />
          <circle cx="15" cy="12" r="4" fill="#ef4444" />
          <circle cx="27" cy="12" r="4" fill="#eab308" />
          <circle cx="39" cy="12" r="4" fill="#22c55e" />
          <text x="70" y="16" font-family="system-ui, -apple-system, sans-serif" font-size="9" font-weight="600" fill="#64748b" text-anchor="middle">scanned_doc.png</text>

          <!-- Mini chart inside document -->
          <rect x="12" y="36" width="116" height="74" rx="4" fill="#f8fafc" stroke="#f1f5f9" stroke-width="1" />
          <!-- Y-Axis labels -->
          <text x="21" y="52" font-family="system-ui, sans-serif" font-size="6" fill="#94a3b8" text-anchor="end">100</text>
          <text x="21" y="72" font-family="system-ui, sans-serif" font-size="6" fill="#94a3b8" text-anchor="end">50</text>
          <text x="21" y="92" font-family="system-ui, sans-serif" font-size="6" fill="#94a3b8" text-anchor="end">0</text>
          <line x1="24" y1="49" x2="120" y2="49" stroke="#e2e8f0" stroke-width="0.5" stroke-dasharray="2 1" />
          <line x1="24" y1="69" x2="120" y2="69" stroke="#e2e8f0" stroke-width="0.5" stroke-dasharray="2 1" />
          <line x1="24" y1="89" x2="120" y2="89" stroke="#cbd5e1" stroke-width="1" />

          <!-- Bar chart sketch with labels -->
          <rect x="30" y="69" width="10" height="20" fill="#3b82f6" rx="1" />
          <text x="35" y="98" font-family="system-ui, sans-serif" font-size="6" fill="#64748b" text-anchor="middle">J</text>

          <rect x="48" y="54" width="10" height="35" fill="#ef4444" rx="1" />
          <text x="53" y="98" font-family="system-ui, sans-serif" font-size="6" fill="#64748b" text-anchor="middle">F</text>

          <rect x="66" y="61" width="10" height="28" fill="#10b981" rx="1" />
          <text x="71" y="98" font-family="system-ui, sans-serif" font-size="6" fill="#64748b" text-anchor="middle">M</text>

          <rect x="84" y="44" width="10" height="45" fill="#f59e0b" rx="1" />
          <text x="89" y="98" font-family="system-ui, sans-serif" font-size="6" fill="#64748b" text-anchor="middle">A</text>

          <rect x="102" y="64" width="10" height="25" fill="#8b5cf6" rx="1" />
          <text x="107" y="98" font-family="system-ui, sans-serif" font-size="6" fill="#64748b" text-anchor="middle">M</text>
          
          <!-- Mini invoice text lines -->
          <rect x="15" y="118" width="55" height="5" rx="1" fill="#e2e8f0" />
          <rect x="15" y="128" width="80" height="5" rx="1" fill="#e2e8f0" />
          <rect x="15" y="138" width="40" height="5" rx="1" fill="#e2e8f0" />
          <rect x="105" y="138" width="20" height="5" rx="1" fill="#3b82f6" />
        </g>

        <!-- Connection 1 -->
        <path d="M 185 100 L 225 100" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#glow-arrow)" />

        <!-- SECTION 2: Request Payload (Middle) -->
        <g transform="translate(240, 25)" filter="url(#shadow)">
          <!-- Payload Card -->
          <rect x="0" y="0" width="240" height="150" rx="8" fill="#0f172a" />
          <!-- Header -->
          <rect x="0" y="0" width="240" height="26" rx="8" fill="#1e293b" />
          <text x="15" y="17" font-family="monospace" font-size="10" font-weight="bold" fill="#38bdf8">POST /answer-image</text>
          <text x="225" y="17" font-family="system-ui, sans-serif" font-size="9" fill="#94a3b8" text-anchor="end">JSON</text>
          
          <!-- JSON Content -->
          <text x="15" y="50" font-family="monospace" font-size="10" fill="#e2e8f0">{</text>
          <text x="30" y="70" font-family="monospace" font-size="10" fill="#f43f5e">"image_base64"</text>
          <text x="120" y="70" font-family="monospace" font-size="10" fill="#e2e8f0">:</text>
          <text x="135" y="70" font-family="monospace" font-size="10" fill="#34d399">"iVBORw0KG..."</text>
          
          <text x="30" y="95" font-family="monospace" font-size="10" fill="#f43f5e">"question"</text>
          <text x="95" y="95" font-family="monospace" font-size="10" fill="#e2e8f0">:</text>
          <text x="110" y="95" font-family="monospace" font-size="10" fill="#34d399">"What is the total?"</text>
          <text x="15" y="120" font-family="monospace" font-size="10" fill="#e2e8f0">}</text>
        </g>

        <!-- Connection 2 -->
        <path d="M 495 100 L 535 100" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#glow-arrow)" />

        <!-- SECTION 3: Deployed API Response (Right) -->
        <g transform="translate(550, 35)" filter="url(#shadow)">
          <!-- API Card -->
          <rect x="0" y="0" width="180" height="130" rx="8" fill="#ffffff" stroke="#10b981" stroke-width="2" />
          <rect x="0" y="0" width="180" height="24" rx="8" fill="#ecfdf5" />
          <path d="M0,24 L180,24" stroke="#d1fae5" stroke-width="1" />
          <text x="15" y="16" font-family="system-ui, sans-serif" font-size="9" font-weight="bold" fill="#047857">STUDENT API</text>
          <rect x="135" y="5" width="38" height="14" rx="3" fill="#10b981" />
          <text x="154" y="15" font-family="system-ui, sans-serif" font-size="8" font-weight="bold" fill="#ffffff" text-anchor="middle">ONLINE</text>

          <!-- Response Body -->
          <rect x="10" y="35" width="160" height="85" rx="6" fill="#f8fafc" stroke="#e2e8f0" stroke-width="1" />
          <text x="20" y="55" font-family="monospace" font-size="10" fill="#64748b">Response (200 OK)</text>
          <text x="20" y="75" font-family="monospace" font-size="11" fill="#0f172a">{</text>
          <text x="35" y="92" font-family="monospace" font-size="11" fill="#2563eb">"answer"</text>
          <text x="90" y="92" font-family="monospace" font-size="11" fill="#0f172a">:</text>
          <text x="102" y="92" font-family="monospace" font-size="11" font-weight="bold" fill="#16a34a">"4089.35"</text>
          <text x="20" y="108" font-family="monospace" font-size="11" fill="#0f172a">}</text>
        </g>
      </svg>

      <p><strong>API Specification:</strong></p>
      <ul>
        <li><strong>Endpoint:</strong> <code>POST /answer-image</code></li>
        <li><strong>Request format:</strong> <code>{"image_base64": "...", "question": "..."}</code></li>
        <li><strong>Response format:</strong> <code>{"answer": "..."}</code></li>
      </ul>

      <p><strong>Rules & Requirements:</strong></p>
      <ol>
        <li>The <code>answer</code> field must be a string. For numeric answers, return only the number (e.g. <code>"4089.35"</code>) without currency symbols or units.</li>
        <li>CORS must be enabled so the grader can call your endpoint from a Cloudflare Worker.</li>
        <li>Deploy your service to a public URL (e.g., Vercel, Render, Fly.io, HuggingFace Spaces, or a Cloudflare Tunnel).</li>
      </ol>

      <p>
        <strong>Step 1:</strong> Download the sample task file containing example questions and image descriptions:
        <button class="btn btn-sm btn-outline-primary ms-2" type="button" @click=${()=>L(i,t+"_sample.json")}>
          Download ${t}_sample.json
        </button>
      </p>

      <p><strong>Step 2:</strong> Deploy your service and verify it works with the sample cases.</p>

      <div class="mb-3">
        <label for="${t}" class="form-label"><strong>Step 3: Submit your deployed API base URL:</strong></label>
        <input class="form-control font-monospace" id="${t}" name="${t}" type="url" placeholder="https://my-image-qa.example.workers.dev" />
        <div class="form-text text-muted">The grader will call <code>POST &lt;your-url&gt;/answer-image</code>.</div>
      </div>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=String(c||"").trim();if(!a)throw new Error("Enter your deployed API base URL.");if(!/^https?:\/\//i.test(a))throw new Error("URL must start with http:// or https://.");let s;try{s=new URL(a).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(s))throw new Error("The grader can't reach a private/localhost address \u2014 deploy publicly or use a tunnel.");let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),p=await h.json();if(!h.ok)throw new Error(p.error||"Unable to verify response.");return p}
}
```

----------------------------------------

## Q3: Fixed Schema Invoice Extraction API (q-invoice-extract-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p>
        <strong>Scenario:</strong> The <em>IITM Finance Cell</em> receives hundreds of invoices in varied plain-text formats every month.
        Your task is to build and deploy an API that reads raw invoice text and extracts a fixed set of structured fields.
      </p>

      <svg viewBox="0 0 760 160" width="100%" style="margin:20px 0;max-width: 960px;display:block;background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 4px 6px -1px rgba(0,0,0,.05)" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid-inv" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f1f5f9" stroke-width="1"/></pattern>
          <filter id="sh-inv"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#0f172a" flood-opacity=".08"/></filter>
          <marker id="arr-inv" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b"/></marker>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid-inv)" rx="12"/>
        <!-- Invoice text box -->
        <g transform="translate(25,20)" filter="url(#sh-inv)">
          <rect x="0" y="0" width="190" height="120" rx="8" fill="#fff" stroke="#cbd5e1" stroke-width="1.5"/>
          <rect x="0" y="0" width="190" height="22" rx="8" fill="#fef9c3"/>
          <text x="10" y="15" font-family="system-ui,sans-serif" font-size="9" font-weight="bold" fill="#854d0e">RAW INVOICE TEXT</text>
          <text x="12" y="38" font-family="monospace" font-size="8" fill="#374151">Invoice No: INV-2026-0041</text>
          <text x="12" y="51" font-family="monospace" font-size="8" fill="#374151">Date: 15 March 2026</text>
          <text x="12" y="64" font-family="monospace" font-size="8" fill="#374151">Vendor: TechParts Pvt Ltd</text>
          <text x="12" y="77" font-family="monospace" font-size="8" fill="#374151">Subtotal: Rs. 2,199.00</text>
          <text x="12" y="90" font-family="monospace" font-size="8" fill="#374151">GST (18%): Rs. 395.82</text>
          <text x="12" y="103" font-family="monospace" font-size="8" fill="#374151">TOTAL: Rs. 2,594.82</text>
        </g>
        <!-- Arrow -->
        <path d="M 230 80 L 270 80" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#arr-inv)"/>
        <!-- API box -->
        <g transform="translate(280,25)" filter="url(#sh-inv)">
          <rect x="0" y="0" width="200" height="110" rx="8" fill="#1e293b"/>
          <rect x="0" y="0" width="200" height="24" rx="8" fill="#0f172a"/>
          <text x="12" y="16" font-family="monospace" font-size="10" font-weight="bold" fill="#38bdf8">POST /extract</text>
          <text x="12" y="45" font-family="monospace" font-size="9" fill="#94a3b8">{"invoice_text": "..."}</text>
          <line x1="10" y1="58" x2="190" y2="58" stroke="#334155" stroke-width="1"/>
          <text x="12" y="72" font-family="monospace" font-size="9" fill="#34d399">{"invoice_no": "INV-2026-0041",</text>
          <text x="12" y="85" font-family="monospace" font-size="9" fill="#34d399"> "date": "2026-03-15",</text>
          <text x="12" y="98" font-family="monospace" font-size="9" fill="#34d399"> "amount": 2199.00}</text>
        </g>
        <!-- Arrow -->
        <path d="M 495 80 L 525 80" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#arr-inv)"/>
        <!-- Result box -->
        <g transform="translate(535,30)" filter="url(#sh-inv)">
          <rect x="0" y="0" width="195" height="100" rx="8" fill="#fff" stroke="#10b981" stroke-width="2"/>
          <rect x="0" y="0" width="195" height="22" rx="8" fill="#ecfdf5"/>
          <text x="10" y="15" font-family="system-ui,sans-serif" font-size="9" font-weight="bold" fill="#047857">EXTRACTED FIELDS</text>
          <text x="10" y="38" font-family="monospace" font-size="8.5" fill="#0f172a">invoice_no: "INV-2026-0041"</text>
          <text x="10" y="52" font-family="monospace" font-size="8.5" fill="#0f172a">date:       "2026-03-15"</text>
          <text x="10" y="66" font-family="monospace" font-size="8.5" fill="#0f172a">amount:     2199.00</text>
          <text x="10" y="80" font-family="monospace" font-size="8.5" fill="#0f172a">tax:        395.82</text>
        </g>
      </svg>

      <p><strong>API Specification:</strong></p>
      <ul>
        <li><strong>Endpoint:</strong> <code>POST /extract</code></li>
        <li><strong>Input:</strong> <code>{"invoice_text": "..."}</code></li>
        <li><strong>Output (always return all 6 keys):</strong></li>
      </ul>
      <pre style="font-size:0.82rem;border:1px solid #e2e8f0;border-radius:6px;padding:10px">{
  "invoice_no": "INV-2026-0041",
  "date": "2026-03-15",
  "vendor": "TechParts Pvt Ltd",
  "amount": 2199.00,
  "tax": 395.82,
  "currency": "INR"
}</pre>

      <p><strong>Rules:</strong></p>
      <ol>
        <li>Always return all 6 keys; use <code>null</code> if a field cannot be found.</li>
        <li><code>date</code> must be ISO format <code>YYYY-MM-DD</code>.</li>
        <li><code>amount</code> is the subtotal <em>before</em> tax; <code>tax</code> is the tax amount only.</li>
        <li>CORS must be enabled; the grader calls your endpoint from a Cloudflare Worker.</li>
        <li>Deploy to any public URL or expose via Cloudflare Tunnel.</li>
      </ol>

      <p>
        <strong>Step 1:</strong> Download sample invoices to test locally:
        <button class="btn btn-sm btn-outline-primary ms-2" type="button" @click=${()=>L(i,t+"_sample.json")}>
          Download ${t}_sample.json
        </button>
      </p>
      <p><strong>Step 2:</strong> Deploy your <code>POST /extract</code> endpoint publicly.</p>
      <div class="mb-3">
        <label for="${t}" class="form-label"><strong>Step 3: Submit your API base URL:</strong></label>
        <input class="form-control font-monospace" id="${t}" name="${t}" type="url" placeholder="https://my-invoice-api.example.workers.dev"/>
        <div class="form-text text-muted">The grader will call <code>POST &lt;your-url&gt;/extract</code> with hidden invoice texts.</div>
      </div>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=String(c||"").trim();if(!a)throw new Error("Enter your deployed API base URL.");if(!/^https?:\/\//i.test(a))throw new Error("URL must start with http:// or https://.");let s;try{s=new URL(a).hostname}catch{throw new Error("Not a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(s))throw new Error("The grader can't reach a localhost address \u2014 deploy publicly or use a tunnel.");let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),p=await h.json();if(!h.ok)throw new Error(p.error||"Unable to verify.");return p}
}
```

----------------------------------------

## Q4: Dynamic Schema Structured Extraction API (q-dynamic-extract-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p>
        <strong>Scenario:</strong> <em>DataBridge Inc.</em> builds intelligent ETL pipelines that extract
        structured data from raw text at runtime. Unlike fixed-schema extractors, their system accepts a
        <strong>dynamic schema</strong> per request — the caller defines which fields to extract and what
        types they should be.
      </p>

      <svg viewBox="0 0 760 175" width="100%" style="margin:20px 0;max-width: 960px;display:block;background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 4px 6px -1px rgba(0,0,0,.05)" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid-dyn" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f1f5f9" stroke-width="1"/></pattern>
          <filter id="sh-dyn"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#0f172a" flood-opacity=".08"/></filter>
          <marker id="arr-dyn" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b"/></marker>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid-dyn)" rx="12"/>
        <!-- Text input box -->
        <g transform="translate(20,20)" filter="url(#sh-dyn)">
          <rect width="195" height="135" rx="8" fill="#fff" stroke="#cbd5e1" stroke-width="1.5"/>
          <rect width="195" height="22" rx="8" fill="#fef3c7"/>
          <text x="10" y="15" font-family="system-ui,sans-serif" font-size="9" font-weight="bold" fill="#92400e">REQUEST BODY</text>
          <text x="10" y="38" font-family="monospace" font-size="8" fill="#0f172a">{"text": "Rahul bought</text>
          <text x="10" y="51" font-family="monospace" font-size="8" fill="#0f172a"> 3 notebooks for Rs.240</text>
          <text x="10" y="64" font-family="monospace" font-size="8" fill="#0f172a"> on 12 June 2026...",</text>
          <text x="10" y="80" font-family="monospace" font-size="8" fill="#7c3aed"> "schema": {</text>
          <text x="10" y="93" font-family="monospace" font-size="8" fill="#7c3aed">  "customer_name":"string",</text>
          <text x="10" y="106" font-family="monospace" font-size="8" fill="#7c3aed">  "quantity": "integer",</text>
          <text x="10" y="119" font-family="monospace" font-size="8" fill="#7c3aed">  "amount": "float"</text>
          <text x="10" y="130" font-family="monospace" font-size="8" fill="#7c3aed"> }}</text>
        </g>
        <!-- Arrow -->
        <path d="M 228 87 L 268 87" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#arr-dyn)"/>
        <!-- API box -->
        <g transform="translate(278,28)" filter="url(#sh-dyn)">
          <rect width="200" height="120" rx="8" fill="#1e293b"/>
          <rect width="200" height="24" rx="8" fill="#0f172a"/>
          <text x="12" y="16" font-family="monospace" font-size="10" font-weight="bold" fill="#a78bfa">POST /dynamic-extract</text>
          <text x="12" y="43" font-family="monospace" font-size="8.5" fill="#94a3b8">LLM parses text +</text>
          <text x="12" y="56" font-family="monospace" font-size="8.5" fill="#94a3b8">validates schema types</text>
          <line x1="10" y1="68" x2="190" y2="68" stroke="#334155" stroke-width="1"/>
          <text x="12" y="82" font-family="monospace" font-size="8.5" fill="#34d399">{"customer_name": "Rahul",</text>
          <text x="12" y="95" font-family="monospace" font-size="8.5" fill="#34d399"> "quantity": 3,</text>
          <text x="12" y="108" font-family="monospace" font-size="8.5" fill="#34d399"> "amount": 240.0}</text>
        </g>
        <!-- Arrow -->
        <path d="M 490 87 L 520 87" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#arr-dyn)"/>
        <!-- Validation box -->
        <g transform="translate(530,32)" filter="url(#sh-dyn)">
          <rect width="205" height="112" rx="8" fill="#fff" stroke="#7c3aed" stroke-width="2"/>
          <rect width="205" height="22" rx="8" fill="#f5f3ff"/>
          <text x="10" y="15" font-family="system-ui,sans-serif" font-size="9" font-weight="bold" fill="#5b21b6">SCHEMA VALIDATED</text>
          <text x="10" y="38" font-family="monospace" font-size="8.5" fill="#374151">✔ customer_name → string</text>
          <text x="10" y="52" font-family="monospace" font-size="8.5" fill="#374151">✔ quantity → integer</text>
          <text x="10" y="66" font-family="monospace" font-size="8.5" fill="#374151">✔ amount → float</text>
          <text x="10" y="82" font-family="monospace" font-size="8.5" fill="#047857">✔ types match</text>
          <text x="10" y="96" font-family="monospace" font-size="8.5" fill="#047857">✔ no extra keys</text>
        </g>
      </svg>

      <p><strong>API Specification:</strong></p>
      <ul>
        <li><strong>Endpoint:</strong> <code>POST /dynamic-extract</code></li>
        <li><strong>Input:</strong></li>
      </ul>
      <pre style="font-size:0.82rem;border:1px solid #e2e8f0;border-radius:6px;padding:10px">{
  "text": "Rahul bought 3 notebooks for Rs. 240 on 12 June 2026 from Alpha Store.",
  "schema": {
    "customer_name": "string",
    "quantity": "integer",
    "amount": "float",
    "purchase_date": "date",
    "store": "string"
  }
}</pre>
      <p><strong>Output:</strong> Strict JSON matching the requested schema exactly:</p>
      <pre style="font-size:0.82rem;border:1px solid #e2e8f0;border-radius:6px;padding:10px">{
  "customer_name": "Rahul",
  "quantity": 3,
  "amount": 240.0,
  "purchase_date": "2026-06-12",
  "store": "Alpha Store"
}</pre>

      <p><strong>Rules:</strong></p>
      <ol>
        <li>Return exactly the keys from <code>schema</code> — no extras, no missing.</li>
        <li>Use <code>null</code> for fields that cannot be extracted from the text.</li>
        <li>Dates must be ISO format <code>YYYY-MM-DD</code>; floats/integers must be JSON numbers (not strings).</li>
        <li>CORS must be enabled. Deploy publicly or use a Cloudflare Tunnel.</li>
      </ol>

      <p>
        <strong>Step 1:</strong> Download sample pairs to test your endpoint locally:
        <button class="btn btn-sm btn-outline-primary ms-2" type="button" @click=${()=>L(i,t+"_sample.json")}>
          Download ${t}_sample.json
        </button>
      </p>
      <p><strong>Step 2:</strong> Deploy your <code>POST /dynamic-extract</code> endpoint publicly.</p>
      <div class="mb-3">
        <label for="${t}" class="form-label"><strong>Step 3: Submit your API base URL:</strong></label>
        <input class="form-control font-monospace" id="${t}" name="${t}" type="url" placeholder="https://my-dynamic-extract-api.example.workers.dev"/>
        <div class="form-text text-muted">The grader will call <code>POST &lt;your-url&gt;/dynamic-extract</code> with hidden (text, schema) pairs.</div>
      </div>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=String(c||"").trim();if(!a)throw new Error("Enter your deployed API base URL.");if(!/^https?:\/\//i.test(a))throw new Error("URL must start with http:// or https://.");let s;try{s=new URL(a).hostname}catch{throw new Error("Not a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(s))throw new Error("The grader can't reach a localhost address \u2014 deploy publicly or use a tunnel.");let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),p=await h.json();if(!h.ok)throw new Error(p.error||"Unable to verify.");return p}
}
```

----------------------------------------

## Q5: Cosine Similarity Search (q-cosine-similarity-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p>
        <strong>Scenario:</strong> <em>VecSearch Labs</em> is building a lightweight semantic search engine
        over a corpus of technical documents. Instead of calling an embedding API, the embeddings are
        precomputed and provided directly. Your task is to implement the <strong>cosine similarity ranking</strong>
        that powers the search results.
      </p>

      <svg viewBox="0 0 760 175" width="100%" style="margin:20px 0;max-width: 960px;display:block;background:#fafafa;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 4px 6px -1px rgba(0,0,0,.05)" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid-cs" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="#f1f5f9" stroke-width="1"/></pattern>
          <filter id="sh-cs"><feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="#0f172a" flood-opacity=".08"/></filter>
          <marker id="arr-cs" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M 0 1 L 10 5 L 0 9 z" fill="#64748b"/></marker>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid-cs)" rx="12"/>
        <!-- Document corpus box -->
        <g transform="translate(18,20)" filter="url(#sh-cs)">
          <rect width="185" height="135" rx="8" fill="#fff" stroke="#cbd5e1" stroke-width="1.5"/>
          <rect width="185" height="22" rx="8" fill="#e0f2fe"/>
          <text x="10" y="15" font-family="system-ui,sans-serif" font-size="9" font-weight="bold" fill="#0369a1">250 DOCUMENTS (64-dim)</text>
          <text x="10" y="38" font-family="monospace" font-size="8" fill="#0f172a">D000001: [0.12, -0.34, ...]</text>
          <text x="10" y="51" font-family="monospace" font-size="8" fill="#0f172a">D000002: [0.89,  0.11, ...]</text>
          <text x="10" y="64" font-family="monospace" font-size="8" fill="#64748b">D000003: [0.45, -0.67, ...]</text>
          <text x="10" y="77" font-family="monospace" font-size="8" fill="#64748b">...  (250 rows)</text>
          <line x1="10" y1="90" x2="175" y2="90" stroke="#e2e8f0" stroke-width="1"/>
          <text x="10" y="105" font-family="system-ui,sans-serif" font-size="8" font-weight="bold" fill="#0369a1">10 QUERIES</text>
          <text x="10" y="118" font-family="monospace" font-size="8" fill="#0f172a">Q001: [0.22,  0.71, ...]</text>
          <text x="10" y="131" font-family="monospace" font-size="8" fill="#64748b">...  (10 queries)</text>
        </g>
        <!-- Arrow -->
        <path d="M 215 87 L 255 87" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#arr-cs)"/>
        <!-- Cosine computation box -->
        <g transform="translate(265,28)" filter="url(#sh-cs)">
          <rect width="215" height="120" rx="8" fill="#1e293b"/>
          <rect width="215" height="24" rx="8" fill="#0f172a"/>
          <text x="12" y="16" font-family="monospace" font-size="10" font-weight="bold" fill="#38bdf8">Cosine Similarity</text>
          <text x="12" y="42" font-family="monospace" font-size="8.5" fill="#94a3b8">cos(q, d) = q·d / (|q| × |d|)</text>
          <line x1="10" y1="55" x2="205" y2="55" stroke="#334155" stroke-width="1"/>
          <text x="12" y="70" font-family="monospace" font-size="8.5" fill="#fcd34d">import numpy as np</text>
          <text x="12" y="83" font-family="monospace" font-size="8.5" fill="#fcd34d">sims = D_emb @ q_emb</text>
          <text x="12" y="96" font-family="monospace" font-size="8.5" fill="#fcd34d">top5 = np.argsort(-sims)[:5]</text>
          <text x="12" y="109" font-family="monospace" font-size="8.5" fill="#34d399">→ sort desc, tie-break by id</text>
        </g>
        <!-- Arrow -->
        <path d="M 492 87 L 522 87" stroke="#64748b" stroke-width="2" stroke-dasharray="4 3" fill="none" marker-end="url(#arr-cs)"/>
        <!-- Result box -->
        <g transform="translate(532,30)" filter="url(#sh-cs)">
          <rect width="208" height="115" rx="8" fill="#fff" stroke="#0ea5e9" stroke-width="2"/>
          <rect width="208" height="22" rx="8" fill="#f0f9ff"/>
          <text x="10" y="15" font-family="system-ui,sans-serif" font-size="9" font-weight="bold" fill="#0369a1">TOP-5 RESULTS (JSON)</text>
          <text x="10" y="37" font-family="monospace" font-size="8.5" fill="#0f172a">{"Q001": ["D000151",</text>
          <text x="10" y="50" font-family="monospace" font-size="8.5" fill="#0f172a">  "D000146", "D000166",</text>
          <text x="10" y="63" font-family="monospace" font-size="8.5" fill="#0f172a">  "D000091", "D000126"],</text>
          <text x="10" y="76" font-family="monospace" font-size="8.5" fill="#64748b"> "Q002": ["D000097",</text>
          <text x="10" y="89" font-family="monospace" font-size="8.5" fill="#64748b">  "D000012", ...],</text>
          <text x="10" y="102" font-family="monospace" font-size="8.5" fill="#64748b"> ... 10 queries total}</text>
        </g>
      </svg>

      <p><strong>Your task:</strong></p>
      <ol>
        <li>Load the downloaded JSON file — it contains <strong>${H} documents</strong> and <strong>${J} queries</strong>, each with a precomputed ${M}-dimensional embedding.</li>
        <li>For each query, compute the <strong>cosine similarity</strong> to all 250 documents.</li>
        <li>Return the <strong>top 5 document IDs</strong> per query, sorted by similarity descending.</li>
        <li>Tie-break rule: if two documents have equal similarity, the one with the <strong>smaller doc_id</strong> comes first.</li>
      </ol>

      <p><strong>Answer format:</strong></p>
      <pre style="font-size:0.82rem;border:1px solid #e2e8f0;border-radius:6px;padding:10px">{
  "Q001": ["D000151", "D000146", "D000166", "D000091", "D000126"],
  "Q002": ["D000097", "D000012", "D000092", "D000232", "D000177"],
  ...
}</pre>

      <p>
        <strong>Step 1:</strong> Download your personalised task file:
        <button class="btn btn-sm btn-outline-primary ms-2" type="button" @click=${()=>L(i,t+".json")}>
          Download ${t}.json
        </button>
      </p>
      <p class="text-muted" style="font-size:0.85rem">
        Hint: Use <code>numpy</code> — <code>D_emb @ q_emb</code> gives all cosine similarities at once if embeddings are already unit-normalised (they are).
      </p>
      <div class="mb-3">
        <label for="${t}" class="form-label"><strong>Step 2: Paste your JSON answer:</strong></label>
        <textarea class="form-control font-monospace" id="${t}" name="${t}" rows="6"
          placeholder='{"Q001": ["D000001", ...], "Q002": [...], ...}'></textarea>
      </div>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a;try{a=JSON.parse(String(c||"").trim())}catch{throw new Error("Answer must be valid JSON.")}if(typeof a!="object"||Array.isArray(a))throw new Error("Answer must be a JSON object mapping query IDs to arrays of doc IDs.");let s=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),h=await s.json();if(!s.ok)throw new Error(h.error||"Unable to verify.");return h}
}
```

----------------------------------------

## Q6: Korean Audio Dataset API (q-korean-audio-dataset-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p>
        あなたの提出は <strong>APIエンドポイントURLのみ</strong> です。サーバーはそのURLに対して
        音声（base64）を送信し、返されたJSONを厳密一致で検証します。
      </p>
      <p>
        1人あたり4件の音声をサーバー側で固定シード抽出し、すべて一致した場合のみ正解です。
      </p>

      <h6>受信リクエスト</h6>
      <pre><code>{"audio_id":"q0","audio_base64":"..."}</code></pre>

      <h6>返却JSONの必須構造</h6>
      <pre><code>${JSON.stringify({rows:0,columns:[],mean:{},std:{},variance:{},min:{},max:{},median:{},mode:{},range:{},allowed_values:{},value_range:{},correlation:[]},null,2)}</code></pre>
      <p class="form-text">
        各音声に対して、上記キーを含むJSONを返してください（値は音声ごとの仕様に一致させること）。
      </p>

      <label for="${t}" class="form-label"><strong>APIエンドポイントURL</strong></label>
      <textarea
        class="form-control font-monospace"
        id="${t}"
        name="${t}"
        rows="3"
        placeholder="https://example.com/your-api"
      ></textarea>
    </div>
```

### Grader Verification JS Code:
```javascript
async (l) => {
let c=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:{url:l,phase:"preview"},weight:n,questionId:t,version:r})}),a=await c.json();if(!c.ok)throw new Error(a.error||"\u691C\u8A3C\u306B\u5931\u6557\u3057\u307E\u3057\u305F\u3002");return a}
}
```

----------------------------------------

## Q7: Invoice Intelligence Structured Extraction (q-structured-extraction-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p class="lead text-primary">
        <strong>Scenario:</strong> The finance team at a logistics firm receives invoices as messy free-text.
        Build an API that reads each document and returns clean, strongly-typed JSON for their ERP.
      </p>
      <p>
        Your submission is <strong>only the API endpoint URL</strong>. The grader sends a few documents
        (seeded to you) and checks every returned JSON against the ground truth with an <strong>exact match</strong>.
      </p>

      <div class="card my-3 border-secondary bg-dark text-white">
        <div class="card-body">
          <h5 class="card-title text-dark"><strong>Extraction rules — read carefully</strong></h5>
          <ul class="mb-0">
            <li><code>vendor</code>: the biller's proper name, exactly as written.</li>
            <li><code>currency</code>: the <strong>ISO 4217 code</strong> (<code>USD</code>, <code>EUR</code>, <code>GBP</code>, <code>INR</code>, <code>JPY</code>) — the text may say "euros", "₹", "pounds sterling", etc.</li>
            <li><code>total_amount</code>: integer in the main unit, <strong>no separators or symbols</strong>. The text may spell it out ("twelve thousand four hundred eighty"), use <code>12,480</code>, Indian grouping <code>1,24,800</code>, or a <code>12K</code> suffix.</li>
            <li><code>invoice_date</code>: normalize to <code>YYYY-MM-DD</code>.</li>
            <li><code>due_in_days</code>: integer (e.g. "Net 30", "payable within 45 days", "due in two weeks" → 14).</li>
            <li><code>is_paid</code>: boolean inferred from wording ("paid in full" → true, "awaiting payment" → false).</li>
            <li><code>priority</code>: one of <code>low</code>, <code>normal</code>, <code>high</code>, <code>urgent</code>.</li>
            <li><code>contact_email</code>: <strong>lowercased</strong>.</li>
            <li><code>line_items</code>: array of <code>{ sku, quantity, unit_price }</code> in the order they appear; <code>unit_price</code> is an integer.</li>
            <li><code>item_count</code>: number of line items.</li>
          </ul>
        </div>
      </div>

      <h6>Request your endpoint receives (POST, JSON):</h6>
      <pre><code>${JSON.stringify(u,null,2)}</code></pre>

      <h6>Exact JSON you must return:</h6>
      <pre><code>${JSON.stringify(i,null,2)}</code></pre>
      <p class="form-text">
        Return <strong>exactly</strong> these keys — no more, no less. The grader compares numbers, strings,
        booleans and array order strictly. A reliable approach is an LLM call with JSON-schema / structured output
        using the <code>schema</code> we send you.
      </p>

      <label for="${t}" class="form-label"><strong>API endpoint URL</strong></label>
      <textarea
        class="form-control font-monospace"
        id="${t}"
        name="${t}"
        rows="2"
        placeholder="https://your-service.example.com/extract"
      ></textarea>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:{url:c,phase:"preview"},weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}
}
```

----------------------------------------

## Q8: Semantic Search passage ranking (q-semantic-rank-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p class="lead text-primary">
        <strong>Scenario:</strong> You are building the retrieval core of a semantic search engine.
        Given a query and a list of candidate passages, return the most relevant ones.
      </p>
      <p>
        Your submission is <strong>only the API endpoint URL</strong>. The grader sends several
        <em>(query, candidates)</em> pairs (seeded to you) and checks that you pick the right passages.
      </p>

      <div class="card my-3 border-secondary bg-dark text-white">
        <div class="card-body">
          <h5 class="card-title text-dark"><strong>Rules</strong></h5>
          <ul class="mb-0">
            <li>Embed the <code>query</code> and each <code>candidates[i]</code> with
              <strong><code>text-embedding-3-small</code></strong> (the ranking is defined by this model).</li>
            <li>Score candidates by <strong>cosine similarity</strong> to the query.</li>
            <li>Return the <strong>indices of the 3 most similar candidates</strong> as
              <code>{"ranking": [i, j, k]}</code>. Indices are positions in the <code>candidates</code> array.</li>
            <li>Order within the three does <strong>not</strong> matter; they must be the correct three.</li>
          </ul>
        </div>
      </div>

      <h6>Request your endpoint receives (POST, JSON):</h6>
      <pre><code>${JSON.stringify(u,null,2)}</code></pre>

      <h6>Exact JSON you must return:</h6>
      <pre><code>${JSON.stringify(i,null,2)}</code></pre>
      <p class="form-text">
        The three correct passages are clearly separated from the rest, so a correct cosine-similarity
        implementation over <code>text-embedding-3-small</code> embeddings will rank them unambiguously.
      </p>

      <label for="${t}" class="form-label"><strong>API endpoint URL</strong></label>
      <textarea
        class="form-control font-monospace"
        id="${t}"
        name="${t}"
        rows="2"
        placeholder="https://your-service.example.com/rank"
      ></textarea>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:{url:c,phase:"preview"},weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}
}
```

----------------------------------------

## Q9: Word-Problem Solver API (q-cot-math-verifier-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p class="lead text-primary">
        <strong>Scenario:</strong> You are shipping a "solver" microservice that must answer multi-step
        arithmetic word problems <em>reliably</em> and in a <em>strictly controlled output format</em>.
      </p>
      <p>
        Your submission is <strong>only the API endpoint URL</strong>. The grader POSTs several problems
        (seeded to you) and checks both the answer <strong>and</strong> the output contract.
      </p>

      <div class="card my-3 border-secondary bg-dark text-white">
        <div class="card-body">
          <h5 class="card-title text-dark"><strong>Rules</strong></h5>
          <ul class="mb-0">
            <li>Each problem has a <strong>single integer answer</strong>.</li>
            <li>Problems contain <strong>distractor numbers</strong> that are irrelevant — reason carefully.</li>
            <li>Respond with JSON containing <strong>exactly</strong> two keys:
              <code>reasoning</code> (a string, ≥ 80 chars, showing your steps) and
              <code>answer</code> (a JSON <strong>integer</strong> — not a string, not a float).</li>
            <li>No extra keys. No markdown. No currency symbols in <code>answer</code>.</li>
          </ul>
        </div>
      </div>

      <h6>Request your endpoint receives (POST, JSON):</h6>
      <pre><code>${JSON.stringify(u,null,2)}</code></pre>

      <h6>Exact JSON you must return:</h6>
      <pre><code>${JSON.stringify(i,null,2)}</code></pre>
      <p class="form-text">
        A robust approach is to prompt an LLM with a chain-of-thought instruction and a strict JSON schema,
        then validate the shape before responding. The grader rejects wrong answers, missing/extra keys,
        non-integer answers, and reasoning shorter than 80 characters.
      </p>

      <label for="${t}" class="form-label"><strong>API endpoint URL</strong></label>
      <textarea
        class="form-control font-monospace"
        id="${t}"
        name="${t}"
        rows="2"
        placeholder="https://your-service.example.com/solve"
      ></textarea>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:{url:c,phase:"preview"},weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}
}
```

----------------------------------------

## Q10: Proof-of-Work Nonce Hunt (q-proof-of-work-server)
### Question Description HTML:
```html
./questionData?email=${encodeURIComponent(e.email)}&quizSign=${encodeURIComponent(e.quizSign||"")}&questionId=${encodeURIComponent(t)}&version=${encodeURIComponent(r)}
```

### Grader Verification JS Code:
```javascript
async (l) => {
let c=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:l,weight:n,questionId:t,version:r})}),a=await c.json();if(!c.ok)throw new Error(a.error||"Verification failed.");return a}
}
```

----------------------------------------

## Q11: Context Window Heist (q-context-window-heist-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p class="lead text-primary">
        <strong>Scenario:</strong> You receive a long seeded document with ten planted facts. Some old facts are
        contradicted later by newer facts. Build a context engineering pipeline that finds the latest correct answers
        while respecting a context-window limit.
      </p>
      <ul>
        <li>The haystack is unique to your email and is shown below.</li>
        <li>Assume your model can see at most <strong>4,000 context tokens per call</strong>.</li>
        <li>Your total context sent across all ten questions must be at most <strong>18,000 tokens</strong>.</li>
        <li>Use any strategy: chunking, reranking, summaries, sliding windows, or a hybrid.</li>
        <li>When facts conflict, submit the <strong>latest</strong> fact in the document.</li>
      </ul>

      <details class="my-3" open>
        <summary><strong>Your seeded context heist document</strong></summary>
        <button
          class="btn btn-sm btn-outline-primary my-2"
          type="button"
          @click=${()=>navigator.clipboard.writeText(i)}
        >
          Copy document
        </button>
        <pre
          class="p-3 text-light"
          style="max-height:520px;overflow:auto;background:#111827;border-radius:8px;white-space:pre-wrap"
        ><code>${i}</code></pre>
      </details>

      <p class="mt-3"><strong>Submit JSON only</strong> in this shape:</p>
      <pre><code>{
  "answers": {
    "q1": "latest answer to question 1",
    "q2": "latest answer to question 2",
    "...": "...",
    "q10": "latest answer to question 10"
  },
  "token_counts": {
    "q1": 1200,
    "q2": 1350,
    "...": 1000,
    "q10": 1250
  },
  "pipeline_code": "Paste the code, prompt, or compact pseudocode for your retrieval pipeline here."
}</code></pre>

      <label for="${t}" class="form-label"><strong>Your JSON submission</strong></label>
      <textarea
        class="form-control font-monospace"
        id="${t}"
        name="${t}"
        rows="14"
        placeholder='{"answers":{"q1":"..."},"token_counts":{"q1":1200},"pipeline_code":"..."}'
      ></textarea>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:c,weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}
}
```

----------------------------------------

## Q12: Spin Up the CLI (q-spin-up-cli-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p class="lead text-primary">
        <strong>Scenario:</strong> Your incident team has 50 short log lines. Use a real LLM command-line tool
        together with Unix pipes to classify each line and produce a reproducible output file.
      </p>

      <div class="alert alert-info">
        <strong>What you are practicing:</strong> LLM CLI tools are useful because they fit into normal shell
        workflows. You can use <code>jq</code>, <code>grep</code>, <code>awk</code>, or <code>sed</code> to shape data,
        send focused text to an LLM CLI such as <code>llm</code> or <code>ollama</code>, then post-process the model's
        response into a machine-checkable file.
      </div>

      <ol>
        <li>Open the dataset below and save it as <code>spinup_logs.jsonl</code>.</li>
        <li>Record your work with asciinema: <code>uvx asciinema rec session.cast</code>.</li>
        <li>Inside the recording, echo the personalized marker shown in the dataset panel.</li>
        <li>
          Show your LLM CLI setup or model check, for example <code>uvx --from llm llm --version</code>,
          <code>llm models</code>, or <code>ollama pull ...</code>.
        </li>
        <li>
          Run a pipe-based classification workflow. Your final file must be <code>classified.jsonl</code>, sorted by
          <code>id</code>, with exactly one object per line:
          <code>{"id":"log-001","label":"auth_failure"}</code>.
        </li>
        <li>
          Print the final hash using <code>sha256sum classified.jsonl</code> or
          <code>shasum -a 256 classified.jsonl</code>.
        </li>
        <li>Stop recording with <kbd>Ctrl+D</kbd> and submit the full contents of <code>session.cast</code>.</li>
      </ol>

      <h6>Allowed labels</h6>
      <ul>
        <li><code>auth_failure</code>: login, MFA, token, SSO, or access rejection problems.</li>
        <li><code>payment_error</code>: billing, invoice, card, refund, subscription, or payment gateway failures.</li>
        <li><code>data_quality</code>: bad rows, schema drift, dedupe conflicts, invalid encodings, or ingest issues.</li>
        <li><code>deploy_event</code>: releases, canaries, feature flags, migrations, or service restarts.</li>
        <li><code>support_noise</code>: helpdesk notes, customer replies, surveys, or knowledge-base updates.</li>
      </ul>

      <details class="my-3" open>
        <summary><strong>Your dataset and marker</strong></summary>
        <p class="mt-2 mb-1">Personalized marker: <code>${u}</code></p>
        <button
          class="btn btn-sm btn-outline-primary my-2"
          type="button"
          @click=${()=>navigator.clipboard.writeText(i)}
        >
          Copy dataset
        </button>
        <pre
          class="p-3 text-light"
          style="max-height:430px;overflow:auto;background:#101827;border-radius:8px;white-space:pre-wrap"
        ><code>${i}</code></pre>
      </details>

      <details class="my-3">
        <summary><strong>Example shape, not a required command</strong></summary>
        <pre><code>uvx asciinema rec session.cast
echo "YOUR_MARKER"
uvx --from llm llm --version
cat spinup_logs.jsonl \\
  | jq -r '[.id,.service,.message] | @tsv' \\
  | while IFS=$'\\t' read -r id service message; do
      # call your LLM CLI here, then normalize the label
      printf '{"id":"%s","label":"%s"}\\n' "$id" "$label"
    done \\
  | sort > classified.jsonl
sha256sum classified.jsonl
# Ctrl+D</code></pre>
      </details>

      <div class="alert alert-warning">
        The validator checks the asciinema text for your marker, evidence of an LLM CLI, a Unix pipe chain, a SHA-256
        command, and the correct final hash.
      </div>

      <label for="${t}" class="form-label"><strong>Paste <code>session.cast</code></strong></label>
      <textarea
        class="form-control font-monospace"
        id="${t}"
        name="${t}"
        rows="15"
        placeholder='{"version": 2, "width": 80, "height": 24, ...}'
      ></textarea>
    </div>
```

### Grader Verification JS Code:
```javascript
async (c) => {
let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:c,weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}
}
```

----------------------------------------

## Q13: Embedding Trapdoors (q-embedding-trap-neighbors-server)
### Question Description HTML:
```html
<div class="mb-3">
      <p class="lead text-primary">
        <strong>Scenario:</strong> You are testing whether an embedding-based search system understands meaning rather
        than surface words. Your corpus contains 200 short phrases, including synonym pairs that share few words
        and negation traps that share many words but mean the opposite.
      </p>

      <div class="alert alert-info">
        <strong>What you are practicing:</strong> Build a small similarity search loop: embed every corpus phrase, embed
        each query, compute cosine similarity, and return the single nearest corpus ID for each query. A keyword search
        will often pick the wrong phrase because many traps are designed to have misleading lexical overlap.
      </div>

      <ol>
        <li>Copy the JSON below. It contains <code>queries</code> and <code>corpus</code>.</li>
        <li>Use an embedding model (or another semantic retrieval method) to compare each query with the corpus.</li>
        <li>
          For each query <code>q1</code> through <code>q10</code>, identify the corpus phrase that best matches its
          meaning. You may use cosine similarity over embeddings to shortlist candidates and manually verify the
          closest matches.
        </li>
        <li>Submit JSON mapping each query ID to exactly one corpus ID.</li>
      </ol>

      <div class="alert alert-secondary">
        <strong>Note:</strong> Different embedding models may produce slightly different similarity rankings.
        This assignment is graded against the intended semantic match for each query, not the exact ranking produced
        by any particular embedding model.
      </div>

      <details class="my-3" open>
        <summary><strong>Your queries and corpus</strong></summary>
        <button
          class="btn btn-sm btn-outline-primary my-2"
          type="button"
          @click=${()=>navigator.clipboard.writeText(o)}
        >
          Copy JSON
        </button>
        <pre
          class="p-3 text-light"
          style="max-height:460px;overflow:auto;background:#0f172a;border-radius:8px;white-space:pre-wrap"
        ><code>${o}</code></pre>
      </details>

      <p class="mt-3"><strong>Submission format</strong></p>
      <pre><code>{
  "q1": "p-017",
  "q2": "p-104",
  "...": "...",
  "q10": "p-042"
}</code></pre>

      <label for="${t}" class="form-label">
        <strong>Your semantic-match JSON</strong>
      </label>
      <textarea
        class="form-control font-monospace"
        id="${t}"
        name="${t}"
        rows="10"
        placeholder='{"q1":"p-017","q2":"p-104","q3":"p-088"}'
      ></textarea>
    </div>
```

### Grader Verification JS Code:
```javascript
async (a) => {
let s=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),h=await s.json();if(!s.ok)throw new Error(h.error||"Verification failed.");return h}
}
```

----------------------------------------
