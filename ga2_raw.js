var me=Object.defineProperty;var O=(t,o)=>()=>(t&&(o=t(t=0)),o);var T=(t,o)=>{for(var r in o)me(t,r,{get:o[r],enumerable:!0})};var J={};T(J,{default:()=>ve});import{html as fe}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import ye from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function we(t,o=""){let r="abcdefghijklmnopqrstuvwxyz0123456789",e=ye(`q-fastapi-metrics-cors-server#${(t||"").trim().toLowerCase()}#${o}`);return{allowedOrigin:`https://dash-${(s=>Array.from({length:s},()=>r[Math.floor(e()*r.length)]).join(""))(6)}.example.com`}}async function ve({user:t,weight:o=1.5,version:r=""}){let e="q-fastapi-metrics-cors-server",a="Deploy a CORS-Aware Metrics API",{allowedOrigin:s}=we(t.email,r),c=fe`
    <div class="mb-3">
      <p>
        Build and deploy a <strong>FastAPI</strong> service that computes descriptive statistics and
        enforces a strict per-origin CORS policy. The grader probes your live service with a fresh
        batch of random integers on every check, so you must compute results rather than return
        hard-coded values.
      </p>

      <div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.88rem">
        <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Your assigned values</div>
        <div>
          <span style="color:#94a3b8">Allowed CORS origin</span><br/>
          <code style="color:#6ee7b7;font-size:0.95rem">${s}</code>
        </div>
      </div>

      <p><strong>Endpoint: <code>GET /stats?values=1,2,3,â¦</code></strong></p>
      <ul>
        <li>Parse the comma-separated integers from the <code>values</code> query parameter.</li>
        <li>
          Return JSON: <code>{"email": "&lt;your-email&gt;", "count": N, "sum": S, "min": M, "max": X,
          "mean": F}</code> â mean must be within Â±0.01 of the true value.
        </li>
        <li>Include <code>email</code> exactly as your logged-in address.</li>
      </ul>

      <p><strong>CORS policy</strong></p>
      <ul>
        <li>
          Only your <em>assigned</em> allowed origin (shown above) must receive the
          <code>Access-Control-Allow-Origin</code> header â no wildcards (<code>*</code>).
        </li>
        <li>
          Preflight <code>OPTIONS /stats</code> from the allowed origin must succeed (return ACAO
          header); preflights from any other origin must be rejected (no ACAO header).
        </li>
      </ul>

      <p><strong>Required middleware headers</strong> â every response must carry:</p>
      <ul>
        <li><code>X-Request-ID</code>: a unique identifier for this request (e.g. a UUID).</li>
        <li>
          <code>X-Process-Time</code>: the handler duration in seconds as a non-negative decimal number
          (e.g. <code>0.001234</code>).
        </li>
      </ul>

      <p><strong>What the grader checks</strong></p>
      <ol>
        <li>Preflight from the allowed origin â expects ACAO header.</li>
        <li>Preflight from a random evil origin â must receive no ACAO header.</li>
        <li>
          <code>GET /stats?values=â¦</code> with a fresh random batch â checks all five stat fields plus
          <code>email</code>, <code>X-Request-ID</code>, and <code>X-Process-Time</code>.
        </li>
      </ol>

      <p>
        Deploy to any public host (Vercel, Render, Fly.io, Cloudflare Workers, HF Spaces, etc.) and
        paste your base URL below.
      </p>
      <label for="${e}" class="form-label"><strong>Your deployed service base URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-metrics.example.workers.dev" />
    </div>
  `;return{id:e,title:a,weight:o,question:c,answer:async u=>{let n=String(u||"").trim();if(!n)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(n))throw new Error("URL must start with http:// or https://.");let l;try{l=new URL(n).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(l))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let p=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:t.email,quizSign:t.quizSign,response:n,weight:o,questionId:e,version:r})}),f=await p.json();if(!p.ok)throw new Error(f.error||"Unable to verify.");return f}}}var Y=O(()=>{"use strict"});var K={};T(K,{default:()=>Re});import{html as be}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import ke from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function $e(t,o=""){let r="abcdefghijklmnopqrstuvwxyz0123456789",e=ke(`q-oauth-jwks-verify-server#${(t||"").trim().toLowerCase()}#${o}`),a=s=>Array.from({length:s},()=>r[Math.floor(e()*r.length)]).join("");return{iss:Ee,aud:`tds-${a(8)}.apps.exam.local`,sub:`sub-${a(12)}`}}async function Re({user:t,weight:o=2,version:r=""}){let e="q-oauth-jwks-verify-server",a="OAuth 2.0 / OIDC Token Verification Service",{iss:s,aud:c}=$e(t.email,r),u=be`
    <div class="mb-3">
      <p>
        A mock identity provider (IdP) issues <strong>RS256 JWTs</strong>. Deploy a
        <strong>FastAPI</strong> <code>POST /verify</code> endpoint that validates an incoming token
        and returns a structured result. The grader mints a fresh set of valid, expired,
        wrong-audience, and tampered tokens on every check.
      </p>

      <div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.88rem">
        <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px">Your assigned values</div>
        <div style="display:grid;gap:10px">
          <div>
            <span style="color:#94a3b8">Issuer (iss)</span><br/>
            <code style="color:#6ee7b7;font-size:0.95rem">${s}</code>
          </div>
          <div>
            <span style="color:#94a3b8">Audience (aud)</span><br/>
            <code style="color:#6ee7b7;font-size:0.95rem">${c}</code>
          </div>
          <div>
            <span style="color:#94a3b8">IdP public key (RS256)</span>
            <pre style="${"background:#212529;color:#f8f9fa;padding:8px 10px;border-radius:4px;font-size:0.78rem;margin:4px 0 0;white-space:pre-wrap;word-break:break-all"}">${Se}</pre>
          </div>
        </div>
      </div>

      <p><strong>Endpoint: <code>POST /verify</code></strong></p>
      <ul>
        <li>Request body: <code>{"token": "&lt;JWT string&gt;"}</code></li>
        <li>
          On a <strong>valid token</strong>: respond <code>200</code> with
          <code>{"valid": true, "email": "â¦", "sub": "â¦", "aud": "â¦"}</code> â echo the claims from
          inside the token.
        </li>
        <li>
          On <strong>any invalid token</strong>: respond with a non-200 status (401 recommended) and
          <code>{"valid": false}</code>.
        </li>
      </ul>

      <p><strong>Verification rules â reject the token if any of these fail:</strong></p>
      <ol>
        <li><strong>Signature</strong> â must verify against the RS256 public key shown above.</li>
        <li><strong>Issuer (<code>iss</code>)</strong> â must equal <code>${s}</code>.</li>
        <li><strong>Audience (<code>aud</code>)</strong> â must equal <code>${c}</code>.</li>
        <li><strong>Expiry (<code>exp</code>)</strong> â must be in the future.</li>
      </ol>

      <p><strong>What the grader checks (four probe tokens per verify call):</strong></p>
      <ol>
        <li>A freshly minted valid token â must return 200 + <code>valid: true</code> with correct claims.</li>
        <li>An expired token (exp in the past) â must be rejected.</li>
        <li>A token with the wrong audience â must be rejected.</li>
        <li>A token with a tampered payload and invalid signature â must be rejected.</li>
      </ol>

      <p>
        Deploy to any public host and paste your <code>/verify</code> endpoint URL below
        (include the full path, e.g. <code>https://my-app.example.com/verify</code>).
      </p>
      <label for="${e}" class="form-label"><strong>Your deployed /verify endpoint URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-oauth.example.workers.dev/verify" />
    </div>
  `;return{id:e,title:a,weight:o,question:u,answer:async l=>{let p=String(l||"").trim();if(!p)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(p))throw new Error("URL must start with http:// or https://.");let f;try{f=new URL(p).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(f))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let i=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:t.email,quizSign:t.quizSign,response:p,weight:o,questionId:e,version:r})}),h=await i.json();if(!i.ok)throw new Error(h.error||"Unable to verify.");return h}}}var Ee,xe,Se,G=O(()=>{"use strict";Ee="https://idp.exam.local",xe="MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA2okOHspNjgA+2rTLbeuYcxiP/hG8C6Sb9iwg3yiLAA4HCnpITcbWCSelbvbYGuc3EbNy4xFyf5Cbj5DHJMIDEkryOgyd2giIIIBOUBj8S63uGcnRpOBh9NFatfNwheKuzsPuVNldu6A9cNteNpXcWyJjG2axVfmq7i6SuKr1JoWYG7xTTAvKPujSl4OtsQfO3h5NepzdfXpr28oNnzfWed+zclR6BcmNNo/WVfJ4xyCLSf0BCOgdTgW6PdaChd1l9VDetJZVEgC5tkyvXsfISI6iyrYbKR0NEBSqq4XkadEjsCs4F1RncsS4LlgniT7GlkL9Mce3b0wGLs9/7ZIXdQIDAQAB",Se=`-----BEGIN PUBLIC KEY-----
${xe.match(/.{1,64}/g).join(`
`)}
-----END PUBLIC KEY-----`});var W={};T(W,{default:()=>Ue});import{html as Oe}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import Te from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function B(t,o){return t==="port"||t==="workers"?parseInt(o,10):t==="debug"?/^(1|true|yes|on)$/i.test(String(o)):String(o)}function Ae(t,o=""){let r=Te(`q-config-precedence-server#${(t||"").trim().toLowerCase()}#${o}`),e=i=>i[Math.floor(r()*i.length)],a=(i,h)=>i+Math.floor(r()*(h-i+1)),s={port:8e3,workers:1,debug:!1,log_level:"info",api_key:"default-secret-000"},c=()=>{let i={};for(let h of M)r()<.5&&(h==="port"?i[h]=a(8e3,9e3):h==="workers"?i[h]=a(1,16):h==="debug"?i[h]=r()<.5:h==="log_level"?i[h]=e(j):i[h]=`key-${Ie(r,10)}`);return i},d=c(),u=c(),n=c(),l=i=>Object.fromEntries(Object.entries(i).map(([h,g])=>[h==="num_workers"?"workers":h,g])),p={...s,...l(d),...l(u),...l(n)},f={};for(let i of M)f[i]=B(i,p[i]);return{baseEffective:f,fileYaml:d,dotenv:u,osenv:n}}function Le(t){return Object.entries(t).map(([o,r])=>`${o}: ${typeof r=="boolean"?String(r):r}`).join(`
`)}function Pe(t){return Object.entries(t).map(([o,r])=>`${o==="workers"?"NUM_WORKERS":`APP_${o.toUpperCase()}`}=${r}`).join(`
`)}function Ce(t){return Object.entries(t).map(([o,r])=>`${`APP_${o.toUpperCase()}`}=${r}`).join(`
`)}async function Ue({user:t,weight:o=1,version:r=""}){let e="q-config-precedence-server",a="Resolve 12-Factor Config Precedence",{baseEffective:s,fileYaml:c,dotenv:d,osenv:u}=Ae(t.email,r),n="background:#212529;color:#f8f9fa;padding:8px 10px;border-radius:4px;font-size:0.82rem;margin:4px 0 0;white-space:pre",l=Oe`
    <div class="mb-3">
      <p>
        Deploy a <strong>FastAPI</strong> service that merges four configuration layers â defaults,
        environment-specific YAML, <code>.env</code> file, and OS-level environment variables â then
        applies <strong>CLI overrides</strong> passed as query parameters. The grader sends fresh
        random overrides on every check.
      </p>

      <div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.88rem">
        <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:10px">Your assigned config layers</div>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:12px">
          <div>
            <span style="color:#94a3b8">1. defaults (hardcoded)</span>
            <pre style="${n}">port: 8000\nworkers: 1\ndebug: false\nlog_level: info\napi_key: default-secret-000</pre>
          </div>
          <div>
            <span style="color:#94a3b8">2. config.development.yaml</span>
            <pre style="${n}">${Object.keys(c).length?Le(c):"(empty)"}</pre>
          </div>
          <div>
            <span style="color:#94a3b8">3. .env file</span>
            <pre style="${n}">${Object.keys(d).length?Pe(d):"(empty)"}</pre>
          </div>
          <div>
            <span style="color:#94a3b8">4. OS env vars (APP_* prefix)</span>
            <pre style="${n}">${Object.keys(u).length?Ce(u):"(empty)"}</pre>
          </div>
        </div>
      </div>

      <p><strong>Endpoint: <code>GET /effective-config?set=key=value&amp;set=â¦</code></strong></p>
      <ul>
        <li>
          Merge the four config layers from low to high precedence:
          <strong>defaults â config.&lt;env&gt;.yaml â .env â OS env (APP_* prefix)</strong>.
        </li>
        <li>
          Apply any <code>?set=key=value</code> query parameters as the highest-precedence CLI overrides.
          Multiple <code>set</code> params are allowed.
        </li>
        <li>
          Return JSON: <code>{"port": 8000, "workers": 2, "debug": false, "log_level": "info",
          "api_key": "****"}</code>
        </li>
      </ul>

      <p><strong>Type coercion rules:</strong></p>
      <ul>
        <li><code>port</code>, <code>workers</code> â integer</li>
        <li><code>debug</code> â boolean (<code>true/1/yes/on</code> case-insensitive = <code>true</code>)</li>
        <li><code>log_level</code> and all other keys â string</li>
      </ul>

      <p><strong>Special cases:</strong></p>
      <ul>
        <li>
          <strong>Alias:</strong> <code>NUM_WORKERS</code> in the <code>.env</code> layer maps to the
          <code>workers</code> key.
        </li>
        <li>
          <strong>Secret masking:</strong> <code>api_key</code> must always appear as <code>"****"</code>
          in the response â never expose the real value.
        </li>
        <li>
          <strong>CORS:</strong> your service must allow cross-origin requests from this page so the
          browser can check it directly.
        </li>
      </ul>

      <p><strong>What the grader checks:</strong></p>
      <ol>
        <li>All five keys present with correct types (port as int, debug as bool, etc.).</li>
        <li>Alias <code>NUM_WORKERS â workers</code> correctly resolved.</li>
        <li><code>api_key</code> masked as <code>"****"</code>.</li>
        <li>
          Fresh CLI overrides (e.g. <code>?set=port=9000&amp;set=debug=true</code>) applied correctly
          with highest precedence.
        </li>
      </ol>

      <p>Deploy and paste your <code>/effective-config</code> endpoint URL below.</p>
      <label for="${e}" class="form-label"><strong>Your deployed /effective-config endpoint URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-config.example.workers.dev/effective-config" />
    </div>
  `;return{id:e,title:a,weight:o,question:l,answer:async f=>{let i=String(f||"").trim();if(!i)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(i))throw new Error("URL must start with http:// or https://.");let h;try{h=new URL(i).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(h))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let g=Math.random,v=[...qe].sort(()=>g()-.5).slice(0,1+Math.floor(g()*2)),b={},y=[];for(let m of v){let w;if(m==="port")do w=String(8e3+Math.floor(g()*1e3));while(Number(w)===s.port);else if(m==="workers")do w=String(1+Math.floor(g()*16));while(Number(w)===s.workers);else if(m==="debug")w=s.debug?"false":"true";else do w=j[Math.floor(g()*j.length)];while(w===s.log_level);b[m]=w,y.push(`set=${encodeURIComponent(m)}=${encodeURIComponent(w)}`)}let x={...s};for(let[m,w]of Object.entries(b))x[m]=B(m,w);x.api_key="****";let k=i+(i.includes("?")?"&":"?")+y.join("&"),E;try{E=await fetch(k,{headers:{Accept:"application/json"}})}catch(m){throw new Error(`Could not reach ${i}. Is the service public and CORS enabled? ${m.message||m}`)}if(!E.ok)throw new Error(`GET /effective-config returned HTTP ${E.status}.`);let R;try{R=await E.json()}catch{throw new Error("Response must be a JSON object.")}for(let m of M){let w=R[m],q=x[m];if(typeof w!=typeof q)throw new Error(`"${m}" should be a ${typeof q} (${JSON.stringify(q)}), got ${JSON.stringify(w)} \u2014 check type coercion/masking.`);if(w!==q)throw new Error(`"${m}" should resolve to ${JSON.stringify(q)} (with CLI ${JSON.stringify(b)}), got ${JSON.stringify(w)}.`)}return{correct:!0,score:o,message:"Config precedence, type coercion, alias, and secret masking all verified. \u2705"}}}}var M,qe,j,X,Ie,F=O(()=>{"use strict";M=["port","workers","debug","log_level","api_key"],qe=["port","workers","debug","log_level"],j=["debug","info","warning","error"],X="abcdefghijklmnopqrstuvwxyz0123456789",Ie=(t,o)=>Array.from({length:o},()=>X[Math.floor(t()*X.length)]).join("")});var H={};T(H,{default:()=>Me});import{html as _e}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function Me({user:t,weight:o=2,version:r=""}){let e="q-compose-redis-tunnel-server",a="Multi-Container App via Compose, Exposed by Tunnel",s=_e`
    <div class="mb-3">
      <p>
        Run a <code>docker compose</code> stack that pairs a <strong>FastAPI</strong> API service with a
        <strong>Redis</strong> backend, then expose the API over a public tunnel. The grader hits your
        live service with random hit sequences and expects Redis-backed persistence.
      </p>

      <p><strong>Services in your <code>docker-compose.yml</code>:</strong></p>
      <ul>
        <li><code>api</code> â FastAPI app that talks to redis over the internal compose network.</li>
        <li><code>redis</code> â standard Redis image; no external port needed.</li>
      </ul>

      <p><strong>Endpoints your API must expose:</strong></p>
      <ul>
        <li>
          <code>POST /hit/{key}</code> â atomically increment a Redis counter for
          <code>key</code> and return <code>{"key": "â¦", "count": N}</code>.
        </li>
        <li>
          <code>GET /count/{key}</code> â return the current counter value
          (<code>{"key": "â¦", "count": N}</code>); return 0 for an unseen key.
        </li>
        <li>
          <code>GET /healthz</code> â return <code>{"status": "ok", "redis": "up"}</code>;
          actually ping Redis (not a static response).
        </li>
      </ul>

      <p><strong>Correctness requirements:</strong></p>
      <ul>
        <li>Use Redis <code>INCR</code> â not an in-memory Python dict â so counts survive worker restarts.</li>
        <li>Each key must maintain its own independent counter.</li>
        <li>The count after K hits must equal exactly K.</li>
      </ul>

      <p><strong>What the grader checks:</strong></p>
      <ol>
        <li><code>GET /healthz</code> â <code>{"status": "ok", "redis": "up"}</code>.</li>
        <li>
          A random sequence of <code>POST /hit/{key}</code> calls across two different keys, then
          <code>GET /count/{key}</code> for each â counts must match exactly.
        </li>
        <li>Two different keys must maintain independent counters.</li>
      </ol>

      <p>
        Expose your <code>api</code> service via a tunnel (<code>cloudflared tunnel --url
        http://localhost:8000</code> or <code>lt --port 8000</code>) and paste the tunnel base URL.
      </p>
      <label for="${e}" class="form-label"><strong>Your public tunnel base URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-stack.trycloudflare.com" />
    </div>
  `;return{id:e,title:a,weight:o,question:s,answer:async d=>{let u=String(d||"").trim();if(!u)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(u))throw new Error("URL must start with http:// or https://.");let n;try{n=new URL(u).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(n))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let l=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:t.email,quizSign:t.quizSign,response:u,weight:o,questionId:e,version:r})}),p=await l.json();if(!l.ok)throw new Error(p.error||"Unable to verify.");return p}}}var V=O(()=>{"use strict"});var ee={};T(ee,{default:()=>Ye});import{html as je}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import Ne from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function Z(t,o=""){let r=Ne(`q-deploy-analytics-platform-server#${(t||"").trim().toLowerCase()}#${o}`);return{apiKey:`ak_${De(r,24)}`}}function ze(t){let o={},r=0;for(let s of t){let c=Number(s.amount);c>0&&(r+=c,o[s.user]=(o[s.user]||0)+c)}let e=null,a=-1/0;for(let[s,c]of Object.entries(o))c>a&&(a=c,e=s);return{total_events:t.length,unique_users:new Set(t.map(s=>s.user)).size,revenue:r,top_user:e}}function Je(){let t=Array.from({length:4+Math.floor(Math.random()*3)},(a,s)=>`user-${s+1}`),o=[],r=8+Math.floor(Math.random()*10);for(let a=0;a<r;a++)o.push({user:t[Math.floor(Math.random()*t.length)],amount:Math.floor(Math.random()*551)-50,ts:175e7+Math.floor(Math.random()*1e6)});let e=0;for(;e++<50;){let a={};for(let d of o)d.amount>0&&(a[d.user]=(a[d.user]||0)+d.amount);let s=Object.values(a),c=Math.max(...s,0);if(s.filter(d=>d===c).length===1&&s.length>0)break;o.push({user:t[0],amount:600+e,ts:175e7})}return o}async function Ye({user:t,weight:o=1.5,version:r=""}){let e="q-deploy-analytics-platform-server",a="Deploy a POST Analytics Endpoint",{apiKey:s}=Z(t.email,r),c=je`
    <div class="mb-3">
      <p>
        Deploy a stateless <code>POST /analytics</code> endpoint that authenticates via your assigned API
        key and aggregates a batch of events. The grader sends a fresh randomized
        event batch on every check â you must compute results, not hard-code them.
      </p>

      <div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.88rem">
        <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Your assigned values</div>
        <div>
          <span style="color:#94a3b8">API Key <code style="color:#94a3b8">(X-API-Key header)</code></span><br/>
          <code style="color:#6ee7b7;font-size:0.95rem">${s}</code>
        </div>
      </div>

      <p><strong>Endpoint: <code>POST /analytics</code></strong></p>
      <ul>
        <li>
          <strong>Auth:</strong> require header <code>X-API-Key: &lt;your-assigned-key&gt;</code>.
          Missing or wrong key â HTTP 401.
        </li>
        <li>
          <strong>Request body:</strong>
          <code>{"events": [{"user": "alice", "amount": 42.5, "ts": 1700000000}, â¦]}</code>
        </li>
        <li>
          <strong>Response:</strong>
          <code>{"email": "â¦", "total_events": N, "unique_users": N, "revenue": F, "top_user": "â¦"}</code>
        </li>
        <li>
          <strong>CORS:</strong> your endpoint must allow cross-origin requests from this page so the
          browser can verify it directly (set <code>Access-Control-Allow-Origin: *</code> or the exam
          domain).
        </li>
      </ul>

      <p><strong>Aggregation rules:</strong></p>
      <ul>
        <li><code>total_events</code> â count of all events in the batch.</li>
        <li><code>unique_users</code> â number of distinct <code>user</code> values.</li>
        <li>
          <code>revenue</code> â sum of <code>amount</code> values where <code>amount &gt; 0</code>
          only (ignore zero and negative amounts).
        </li>
        <li>
          <code>top_user</code> â the user whose positive-amount total is highest. The grader ensures
          there are no ties.
        </li>
        <li><code>email</code> â your logged-in email address.</li>
      </ul>

      <p><strong>What the grader checks:</strong></p>
      <ol>
        <li>Missing API key â 401.</li>
        <li>Wrong API key â 401.</li>
        <li>
          Valid key with a fresh 8-17 event batch (4-7 users, mixed positive/negative amounts) â
          checks all five response fields.
        </li>
      </ol>

      <p>Deploy to any public platform and paste your <code>/analytics</code> endpoint URL below.</p>
      <label for="${e}" class="form-label"><strong>Your deployed /analytics endpoint URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-app.vercel.app/analytics" />
    </div>
  `;return{id:e,title:a,weight:o,question:c,answer:async u=>{let n=String(u||"").trim();if(!n)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(n))throw new Error("URL must start with http:// or https://.");let l;try{l=new URL(n).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(l))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let{apiKey:p}=Z(t.email,r),f=(t.email||"").trim().toLowerCase(),i=async(y,x)=>{let k;try{k=await fetch(n,{method:"POST",headers:{"Content-Type":"application/json",...x?{"X-API-Key":x}:{}},body:JSON.stringify({events:y})})}catch(E){throw new Error(`Could not reach ${n}. Is it public with CORS enabled? ${E.message||E}`)}return k};if((await i([{user:"user-1",amount:1,ts:1}],"wrong-key")).status!==401)throw new Error("A wrong X-API-Key must return HTTP 401.");if((await i([{user:"user-1",amount:1,ts:1}],null)).status!==401)throw new Error("A missing X-API-Key must return HTTP 401.");let h=Je(),g=await i(h,p);if(!g.ok)throw new Error(`POST /analytics with the correct key returned HTTP ${g.status}.`);let v;try{v=await g.json()}catch{throw new Error("Response must be a JSON object.")}if(String(v.email||"").trim().toLowerCase()!==f)throw new Error(`Response "email" must equal ${t.email}.`);let b=ze(h);for(let y of["total_events","unique_users","revenue"])if(Number(v[y])!==b[y])throw new Error(`"${y}" should be ${b[y]}, got ${v[y]??"missing"}.`);if(String(v.top_user)!==String(b.top_user))throw new Error(`"top_user" should be ${b.top_user} (highest positive-amount total), got ${v.top_user??"missing"}.`);return{correct:!0,score:o,message:"Auth enforced and analytics aggregates verified on a random batch. \u2705"}}}}var Q,De,te=O(()=>{"use strict";Q="abcdefghijklmnopqrstuvwxyz0123456789",De=(t,o)=>Array.from({length:o},()=>Q[Math.floor(t()*Q.length)]).join("")});var oe={};T(oe,{default:()=>Ge});import{html as Ke}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function Ge({user:t,weight:o=1.5,version:r=""}){let e="q-observability-metrics-server",a="Production Observability: Metrics, Health & Structured Logs",s=Ke`
    <div class="mb-3">
      <p>
        Deploy a <strong>FastAPI</strong> service instrumented with a Prometheus counter, a health
        check endpoint, and structured JSON logs. The grader drives real traffic to <code>/work</code>
        and then verifies that your counter actually increments and your logs record the requests.
      </p>

      <p><strong>Endpoints to implement:</strong></p>
      <ul>
        <li>
          <code>GET /work?n=K</code> â do K units of work, return
          <code>{"email": "â¦", "done": K}</code>. Each call must increment the request counter.
        </li>
        <li>
          <code>GET /metrics</code> â Prometheus text format. Must expose a counter named
          <code>http_requests_total</code> that increases with every request to any endpoint.
        </li>
        <li>
          <code>GET /healthz</code> â return <code>{"status": "ok", "uptime_s": &lt;number&gt;}</code>
          where <code>uptime_s</code> is a non-negative float representing seconds since startup.
        </li>
        <li>
          <code>GET /logs/tail?limit=N</code> â return a JSON array of the last N log entries. Each
          entry must be a JSON object with at minimum: <code>level</code>, <code>ts</code> (timestamp),
          <code>path</code> (request path), <code>request_id</code>.
        </li>
      </ul>

      <p><strong>What the grader checks:</strong></p>
      <ol>
        <li>
          Reads <code>http_requests_total</code> from <code>/metrics</code> as a baseline, then makes
          3-6 random calls to <code>/work?n=K</code>, then reads the counter again â it must have
          increased by at least the number of calls made.
        </li>
        <li>
          <code>/healthz</code> returns <code>status: "ok"</code> and a finite non-negative
          <code>uptime_s</code>.
        </li>
        <li>
          <code>/logs/tail</code> returns a valid JSON array where each object has the four required
          fields, and at least one entry has <code>path</code> containing <code>/work</code>.
        </li>
      </ol>

      <p>
        The counter must be live â a static Prometheus text file that doesn't update will fail. Deploy
        and paste your service base URL.
      </p>
      <label for="${e}" class="form-label"><strong>Your deployed service base URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-observable.example.workers.dev" />
    </div>
  `;return{id:e,title:a,weight:o,question:s,answer:async d=>{let u=String(d||"").trim();if(!u)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(u))throw new Error("URL must start with http:// or https://.");let n;try{n=new URL(u).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(n))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let l=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:t.email,quizSign:t.quizSign,response:u,weight:o,questionId:e,version:r})}),p=await l.json();if(!l.ok)throw new Error(p.error||"Unable to verify.");return p}}}var re=O(()=>{"use strict"});var se={};T(se,{default:()=>Be});import{html as Xe}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function Be({user:t,weight:o=1,version:r=""}){let e="q-ollama-tunnel-llm-server",a="Expose a Local LLM through a Tunnel",s=Xe`
    <div class="mb-3">
      <p>
        Run a local LLM (e.g. <strong>Ollama</strong>) that exposes an
        <strong>OpenAI-compatible</strong> chat completions endpoint, expose it via a public tunnel,
        and submit the endpoint URL plus the model name. The grader sends two fresh prompts every check
        â an echo test and an arithmetic test.
      </p>

      <p><strong>Required setup:</strong></p>
      <ul>
        <li>
          Start Ollama (or any compatible server) so that
          <code>POST /v1/chat/completions</code> is accessible at your tunnel URL.
        </li>
        <li>
          Request format: <code>{"model": "â¦", "messages": [{"role": "user", "content": "â¦"}],
          "stream": false}</code>
        </li>
        <li>
          Response format: standard OpenAI structure â content is read from
          <code>choices[0].message.content</code> (or <code>choices[0].text</code> / top-level
          <code>response</code> as fallback).
        </li>
        <li>
          Enable CORS on your tunnel so this page can reach it directly
          (e.g. <code>OLLAMA_ORIGINS=*</code> for Ollama).
        </li>
      </ul>

      <p><strong>What the grader checks:</strong></p>
      <ol>
        <li>
          <strong>Echo test:</strong> asks the model to repeat a random token (format
          <code>TK&lt;6-hex&gt;</code>). The token must appear somewhere in the response (case-insensitive).
        </li>
        <li>
          <strong>Arithmetic test:</strong> asks "What is A + B?" with random integers (10-89). The
          correct sum must appear as digits in the response.
        </li>
      </ol>

      <p><strong>Submit as JSON:</strong></p>
      <pre style="background:#212529;color:#f8f9fa;padding:8px;border-radius:4px;font-size:0.85rem">{"url": "https://my-llm.trycloudflare.com/v1/chat/completions", "model": "llama3.2"}</pre>
      <ul>
        <li><code>url</code> â the full path to <code>/v1/chat/completions</code> at your tunnel.</li>
        <li><code>model</code> â the exact model name your server is running.</li>
      </ul>

      <label for="${e}" class="form-label"><strong>Your endpoint + model as JSON</strong></label>
      <textarea class="form-control font-monospace" id="${e}" name="${e}" rows="3"
        placeholder='{"url": "https://my-llm.trycloudflare.com/v1/chat/completions", "model": "llama3.2"}'></textarea>
    </div>
  `;return{id:e,title:a,weight:o,question:s,answer:async d=>{let u=String(d||"").trim();if(!u)throw new Error("Enter your answer as JSON.");let n;try{n=JSON.parse(u)}catch(k){throw new Error(`Your answer isn't valid JSON: ${k.message}`)}if(!n||typeof n!="object"||Array.isArray(n))throw new Error("Answer must be a JSON object.");let l=String(n.url||"").trim();if(!/^https?:\/\//i.test(l))throw new Error("`url` must start with http:// or https://.");let p;try{p=new URL(l).hostname}catch{throw new Error("`url` is not a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(p))throw new Error("The grader can't reach a private/localhost address \u2014 expose the model via a tunnel.");let f=String(n.model||"").trim();if(!f)throw new Error("Include the `model` name your server loads.");let i=k=>k?.choices?.[0]?.message?.content??k?.choices?.[0]?.text??k?.message?.content??k?.response??"",h=async k=>{let E;try{E=await fetch(l,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({model:f,messages:[{role:"user",content:k}],stream:!1,temperature:0})})}catch(m){throw new Error(`Could not reach ${l}. Is the tunnel up and CORS enabled (OLLAMA_ORIGINS=*)? ${m.message||m}`)}if(!E.ok)throw new Error(`The endpoint returned HTTP ${E.status}.`);let R;try{R=await E.json()}catch{throw new Error("The endpoint must return JSON.")}return String(i(R)||"")},g=`TK${Math.random().toString(36).slice(2,8).toUpperCase()}`,v=await h(`Output ONLY this exact token and nothing else: ${g}`);if(!v.toUpperCase().includes(g))throw new Error(`Echo test failed: asked for "${g}", model replied "${v.slice(0,80)}".`);let b=10+Math.floor(Math.random()*80),y=10+Math.floor(Math.random()*80),x=await h(`What is ${b} + ${y}? Reply with only the number.`);if(!x.replace(/[^0-9]/g," ").split(/\s+/).includes(String(b+y)))throw new Error(`Reasoning test failed: ${b} + ${y} = ${b+y}, model replied "${x.slice(0,80)}".`);return{correct:!0,score:o,message:"Live local LLM verified: token echo and arithmetic both passed. \u2705"}}}}var ne=O(()=>{"use strict"});var ae={};T(ae,{default:()=>Fe});import{html as We}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function Fe({user:t,weight:o=2,version:r=""}){let e="q-local-llm-structured-server",a="Local LLM Structured-Output Service",s=We`
    <div class="mb-3">
      <p>
        Wrap a local LLM in a <strong>FastAPI</strong> <code>POST /extract</code> endpoint that
        extracts structured invoice fields from free-form text and returns schema-validated JSON. The
        grader sends randomized invoice texts on every check â you must extract the right values, not
        hard-code them.
      </p>

      <p><strong>Endpoint: <code>POST /extract</code></strong></p>
      <ul>
        <li>Request body: <code>{"text": "&lt;invoice text&gt;"}</code></li>
        <li>
          Response: a JSON object with exactly these fields:
          <ul>
            <li><code>vendor</code> â the vendor name as a string.</li>
            <li><code>amount</code> â the total due as a number (float or int).</li>
            <li><code>currency</code> â 3-letter currency code, uppercase (e.g. <code>USD</code>).</li>
            <li><code>date</code> â payment due date as <code>YYYY-MM-DD</code>.</li>
          </ul>
        </li>
      </ul>

      <p><strong>Accuracy requirements:</strong></p>
      <ul>
        <li><code>vendor</code>: extracted value must contain the vendor name (case-insensitive substring match).</li>
        <li><code>amount</code>: within Â±0.01 of the correct value.</li>
        <li><code>currency</code>: exact 3-letter uppercase match.</li>
        <li><code>date</code>: must contain the <code>YYYY-MM-DD</code> substring.</li>
      </ul>

      <p><strong>Error handling:</strong></p>
      <ul>
        <li>
          Malformed or empty input must <strong>not</strong> crash with HTTP 500. Return a 422
          validation error or best-effort valid JSON.
        </li>
      </ul>

      <p><strong>What the grader checks (two randomized invoices per call):</strong></p>
      <ol>
        <li>
          Invoice text contains a planted vendor (e.g. <code>Acme-xxxx Industries Ltd.</code>), amount
          (50-9050), currency (USD/EUR/GBP), and date (2026-MM-DD). All four fields are checked.
        </li>
        <li>Empty/garbage input â must not return HTTP 500.</li>
      </ol>

      <p>
        Use a Pydantic response model to guarantee schema compliance. Deploy and paste your
        <code>/extract</code> endpoint URL.
      </p>
      <label for="${e}" class="form-label"><strong>Your deployed /extract endpoint URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-extractor.example.workers.dev/extract" />
    </div>
  `;return{id:e,title:a,weight:o,question:s,answer:async d=>{let u=String(d||"").trim();if(!u)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(u))throw new Error("URL must start with http:// or https://.");let n;try{n=new URL(u).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(n))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let l=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:t.email,quizSign:t.quizSign,response:u,weight:o,questionId:e,version:r})}),p=await l.json();if(!l.ok)throw new Error(p.error||"Unable to verify.");return p}}}var ie=O(()=>{"use strict"});var ce={};T(ce,{default:()=>Qe});import{html as He}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import Ve from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function le(t,o=""){let r=Ve(`q-api-idempotency-pagination-server#${(t||"").trim().toLowerCase()}#${o}`),e=(a,s)=>a+Math.floor(r()*(s-a+1));return{total:e(40,60),rateLimit:e(15,20)}}async function Qe({user:t,weight:o=2,version:r=""}){let e="q-api-idempotency-pagination-server",a="API Engineering: Idempotency + Pagination + Rate Limit",{total:s,rateLimit:c}=le(t.email,r),d=He`
    <div class="mb-3">
      <p>
        Deploy a <strong>FastAPI</strong> orders API that demonstrates three production-grade API
        engineering patterns: idempotent POST, cursor-based pagination, and per-client rate limiting.
      </p>

      <div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.88rem">
        <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Your assigned values</div>
        <div style="display:flex;gap:24px;flex-wrap:wrap">
          <div><span style="color:#94a3b8">Total orders (T)</span><br/><code style="color:#6ee7b7;font-size:0.95rem">${s}</code></div>
          <div><span style="color:#94a3b8">Rate limit (R requests / 10s)</span><br/><code style="color:#6ee7b7;font-size:0.95rem">${c}</code></div>
        </div>
      </div>

      <p><strong>1. Idempotent order creation</strong></p>
      <ul>
        <li>
          <code>POST /orders</code> with header <code>Idempotency-Key: &lt;k&gt;</code>.
        </li>
        <li>
          On first call: create the order, return <code>{"id": "â¦", â¦}</code> with HTTP 201.
        </li>
        <li>
          On repeat calls with the same key: return the <strong>same</strong> order id â never create
          a duplicate.
        </li>
      </ul>

      <p><strong>2. Cursor pagination</strong></p>
      <ul>
        <li>
          <code>GET /orders?limit=P&amp;cursor=C</code> â return up to <code>P</code> orders from
          your fixed catalog of IDs 1 through T (your assigned total, shown above).
        </li>
        <li>
          Response: <code>{"items": [{"id": 1, â¦}, â¦], "next_cursor": "â¦"}</code> (or
          <code>"next"</code> / <code>"orders"</code> field aliases are accepted).
        </li>
        <li>
          Cursors are opaque â the grader passes back your returned cursor verbatim. Never return more
          than <code>limit</code> items; serve every ID 1..T with no gaps or repeats across pages.
        </li>
      </ul>

      <p><strong>3. Per-client rate limiting</strong></p>
      <ul>
        <li>
          Read the <code>X-Client-Id</code> request header; bucket each client ID independently.
        </li>
        <li>
          Your assigned bucket size is R requests per 10 seconds (shown above).
        </li>
        <li>
          After R requests from the same client ID within the window, return HTTP 429 with a
          <code>Retry-After</code> header. Different client IDs must not share a bucket.
        </li>
        <li>
          <strong>CORS:</strong> your service must allow cross-origin requests from this page so the
          browser can verify it directly.
        </li>
      </ul>

      <p><strong>What the grader checks:</strong></p>
      <ol>
        <li>Same idempotency key used twice â both responses must return the same order id.</li>
        <li>Full paginated scan of orders 1..T â checks no gaps, no repeats, no over-sized pages.</li>
        <li>R+1 requests from the same client ID â the (R+1)th must be HTTP 429 with Retry-After; a different client ID must still be accepted.</li>
      </ol>

      <label for="${e}" class="form-label"><strong>Your deployed orders API base URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-orders.example.workers.dev" />
    </div>
  `;return{id:e,title:a,weight:o,question:d,answer:async n=>{let l=String(n||"").trim();if(!l)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(l))throw new Error("URL must start with http:// or https://.");let p;try{p=new URL(l).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(p))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let{total:f,rateLimit:i}=le(t.email,r),h=l.replace(/\/+$/,""),g=async(S,{method:$="GET",clientId:A="grader",key:I}={})=>{let U={Accept:"application/json","X-Client-Id":A};I&&(U["Idempotency-Key"]=I),$==="POST"&&(U["Content-Type"]="application/json");let L={method:$,headers:U};$==="POST"&&(L.body=JSON.stringify({amount:100}));let N;try{N=await fetch(`${h}${S}`,L)}catch(D){throw new Error(`Could not reach ${h}${S} (${$}). Is it public with CORS enabled? ${D.message||D}`)}return N},v=async S=>{try{return await S.json()}catch{return{}}},b=`idem-${Math.random().toString(36).slice(2,12)}`,y=await g("/orders",{method:"POST",clientId:"grader-idem",key:b});if(!y.ok)throw new Error(`POST /orders returned HTTP ${y.status}.`);let x=(await v(y)).id;if(x==null)throw new Error('POST /orders must return {"id": ...}.');let k=await g("/orders",{method:"POST",clientId:"grader-idem",key:b}),E=(await v(k)).id;if(String(E)!==String(x))throw new Error(`Reusing Idempotency-Key must return the same id (${x}), got ${E} \u2014 you created a duplicate.`);let R=6+Math.floor(Math.random()*5),m=new Set,w="",q=0;for(;q++<=f+3;){let S=`/orders?limit=${R}`+(w?`&cursor=${encodeURIComponent(w)}`:""),$=await g(S,{clientId:"grader-pager"});if(!$.ok)throw new Error(`GET /orders pagination returned HTTP ${$.status}.`);let A=await v($),I=A.items||A.orders||[];if(!Array.isArray(I))throw new Error('GET /orders must return {"items": [...], "next_cursor": ...}.');if(I.length>R)throw new Error(`A page returned ${I.length} items but limit was ${R}.`);for(let U of I){let L=Number(U.id);if(m.has(L))throw new Error(`Order id ${L} appeared on two pages \u2014 pagination must not repeat.`);m.add(L)}if(w=A.next_cursor??A.next??null,!w)break}if(m.size!==f)throw new Error(`Paginating yielded ${m.size} unique orders; expected exactly ${f}.`);for(let S=1;S<=f;S++)if(!m.has(S))throw new Error(`Order id ${S} was missing \u2014 serve ids 1..${f} with no gaps.`);let P=!1,C=!1;for(let S=0;S<i+5;S++){let $=await g("/orders?limit=1",{clientId:"grader-flood"});if($.status===429){P=!0,$.headers.get("retry-after")!==null&&(C=!0);break}}if(!P)throw new Error(`Sending ${i+5} requests from one X-Client-Id should trigger a 429 (limit ${i}/10s).`);if(!C)throw new Error("The 429 response must include a Retry-After header.");return{correct:!0,score:o,message:"Idempotency, cursor pagination, and per-client rate limiting all verified. \u2705"}}}}var de=O(()=>{"use strict"});var pe={};T(pe,{default:()=>tt});import{html as Ze}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import et from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function ue(t,o=""){let r="abcdefghijklmnopqrstuvwxyz0123456789",e=et(`q-middleware-ratelimit-cors-server#${(t||"").trim().toLowerCase()}#${o}`);return{allowedOrigin:`https://app-${(s=>Array.from({length:s},()=>r[Math.floor(e()*r.length)]).join(""))(6)}.example.com`,bucket:8+Math.floor(e()*8)}}async function tt({user:t,weight:o=1.5,version:r=""}){let e="q-middleware-ratelimit-cors-server",a="Middleware Stack: Rate-Limit + CORS + Request Context",{allowedOrigin:s,bucket:c}=ue(t.email,r),d=Ze`
    <div class="mb-3">
      <p>
        Build a <strong>FastAPI</strong> service that composes three middleware layers: a scoped CORS
        policy, a per-client rate limiter, and a request-context propagator.
      </p>

      <div style="background:#1e293b;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.88rem">
        <div style="color:#94a3b8;font-size:0.75rem;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px">Your assigned values</div>
        <div style="display:flex;gap:24px;flex-wrap:wrap">
          <div><span style="color:#94a3b8">Allowed CORS origin</span><br/><code style="color:#6ee7b7;font-size:0.95rem">${s}</code></div>
          <div><span style="color:#94a3b8">Rate-limit bucket (B)</span><br/><code style="color:#6ee7b7;font-size:0.95rem">${c} req / 10s</code></div>
        </div>
      </div>

      <p><strong>Endpoint: <code>GET /ping</code></strong></p>
      <ul>
        <li>
          Return <code>{"email": "â¦", "request_id": "â¦"}</code> where <code>email</code> is your
          logged-in address and <code>request_id</code> is the request's ID (see context middleware
          below).
        </li>
      </ul>

      <p><strong>Middleware 1 â Request context</strong></p>
      <ul>
        <li>
          If the inbound request carries an <code>X-Request-ID</code> header, reuse that value as the
          <code>request_id</code>.
        </li>
        <li>Otherwise generate a fresh unique ID (e.g. UUID4).</li>
        <li>
          Always return the <code>request_id</code> both in the response JSON body and in the
          <code>X-Request-ID</code> response header.
        </li>
      </ul>

      <p><strong>Middleware 2 â CORS</strong></p>
      <ul>
        <li>
          Only your <em>assigned</em> allowed origin (shown above) may receive an
          <code>Access-Control-Allow-Origin</code> header â no wildcards (<code>*</code>).
        </li>
        <li>Preflight (<code>OPTIONS /ping</code>) from the allowed origin must succeed.</li>
        <li>Any other origin must not receive the ACAO header.</li>
        <li>
          <strong>Note:</strong> Also allow this exam page's origin so the browser can reach
          <code>/ping</code> during verification.
        </li>
      </ul>

      <p><strong>Middleware 3 â Per-client rate limiting</strong></p>
      <ul>
        <li>Read the <code>X-Client-Id</code> request header and bucket each ID independently.</li>
        <li>
          Your assigned bucket size is B requests (shown above). After B requests from
          the same client within the window, return HTTP 429. A fresh client ID must still be accepted.
        </li>
      </ul>

      <p><strong>What the grader checks (from your browser):</strong></p>
      <ol>
        <li>
          <code>GET /ping</code> with a supplied <code>X-Request-ID</code> â same value must appear
          in response body and response header.
        </li>
        <li>
          <code>GET /ping</code> without <code>X-Request-ID</code> â a fresh unique ID must be
          generated and appear in both places.
        </li>
        <li>${c+5} requests from the same client ID â must trigger 429; a different client ID must still succeed.</li>
      </ol>

      <label for="${e}" class="form-label"><strong>Your deployed service base URL</strong></label>
      <input class="form-control font-monospace" id="${e}" name="${e}" type="url"
        placeholder="https://my-mw.example.workers.dev" />
    </div>
  `;return{id:e,title:a,weight:o,question:d,answer:async n=>{let l=String(n||"").trim();if(!l)throw new Error("Enter a URL.");if(!/^https?:\/\//i.test(l))throw new Error("URL must start with http:// or https://.");let p;try{p=new URL(l).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(p))throw new Error("The grader can't reach a private/localhost address \u2014 deploy it publicly.");let{bucket:f}=ue(t.email,r),i=(t.email||"").trim().toLowerCase(),h=l.replace(/\/+$/,""),g=async(m,{headers:w={},method:q="GET"}={})=>{let P;try{P=await fetch(`${h}${m}`,{method:q,headers:w})}catch(C){throw new Error(`Could not reach ${h}${m}. Is it public with CORS enabled? ${C.message||C}`)}return P},v=`rid-${Math.random().toString(36).slice(2,12)}`,b=await g("/ping",{headers:{"X-Request-ID":v,"X-Client-Id":"m-ctx1"}});if(!b.ok)throw new Error(`GET /ping returned HTTP ${b.status}.`);let y={};try{y=await b.json()}catch{throw new Error("GET /ping must return a JSON object.")}if(String(y.email||"").trim().toLowerCase()!==i)throw new Error(`GET /ping "email" must equal ${t.email}.`);if(y.request_id!==v)throw new Error(`When X-Request-ID is supplied, echo it in request_id (sent ${v}, got ${y.request_id}).`);if(b.headers.get("x-request-id")!==v)throw new Error("Echo the inbound X-Request-ID in the response header too.");let x=await g("/ping",{headers:{"X-Client-Id":"m-ctx2"}}),k=await x.json().catch(()=>({}));if(!k.request_id||k.request_id===v)throw new Error("Without an inbound X-Request-ID, generate a fresh non-empty request_id.");if(!x.headers.get("x-request-id"))throw new Error("Always set the X-Request-ID response header.");let E=!1;for(let m=0;m<f+5;m++)if((await g("/ping",{headers:{"X-Client-Id":"m-flood"}})).status===429){E=!0;break}if(!E)throw new Error(`More than ${f} requests from one X-Client-Id should return 429.`);if((await g("/ping",{headers:{"X-Client-Id":"m-fresh"}})).status===429)throw new Error("A different X-Client-Id must not be rate-limited (buckets are per-client).");return{correct:!0,score:o,message:"Request-ID propagation and per-client rate limiting verified. \u2705"}}}}var he=O(()=>{"use strict"});import{html as _,render as ge}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function z(t,o){let r=_`<ol class="mt-3">
    ${t.map(({id:s,title:c,weight:d})=>_`<li><a href="#h${s}">${c}</a> (${d} ${d==1?"mark":"marks"})</li>`)}
  </ol>`,e=[_`<h1 class="display-6">Questions</h1>`,r,...t.map(({id:s,title:c,weight:d,question:u,help:n},l)=>(n&&!Array.isArray(n)&&(n=[n]),_`
        <div class="card my-5" data-question="${s}" id="h${s}">
          <div class="card-header">
            <span class="badge text-bg-primary me-2">${l+1}</span>
            ${c} (${d} ${d==1?"mark":"marks"})
          </div>
          ${n?n.map(p=>_`<div class="card-body border-bottom">${p}</div>`):""}
          <div class="card-body">${u}</div>
          <div class="card-footer d-flex">
            <button type="button" class="btn btn-primary check-answer" data-question="${s}">Check</button>
          </div>
        </div>
      `))],a={index:r,questions:e};for(let[s,c]of o)ge(a[c],s)}async function Et(t,o){let r=[{...await Promise.resolve().then(()=>(Y(),J)).then(e=>e.default({user:t,weight:1.5}))},{...await Promise.resolve().then(()=>(G(),K)).then(e=>e.default({user:t,weight:2}))},{...await Promise.resolve().then(()=>(F(),W)).then(e=>e.default({user:t,weight:1}))},{...await Promise.resolve().then(()=>(V(),H)).then(e=>e.default({user:t,weight:2}))},{...await Promise.resolve().then(()=>(te(),ee)).then(e=>e.default({user:t,weight:1.5}))},{...await Promise.resolve().then(()=>(re(),oe)).then(e=>e.default({user:t,weight:1.5}))},{...await Promise.resolve().then(()=>(ne(),se)).then(e=>e.default({user:t,weight:1}))},{...await Promise.resolve().then(()=>(ie(),ae)).then(e=>e.default({user:t,weight:2}))},{...await Promise.resolve().then(()=>(de(),ce)).then(e=>e.default({user:t,weight:2}))},{...await Promise.resolve().then(()=>(he(),pe)).then(e=>e.default({user:t,weight:1.5}))}];return z(r,o),Object.fromEntries(r.map(({id:e,...a})=>[e,a]))}export{Et as questions};
