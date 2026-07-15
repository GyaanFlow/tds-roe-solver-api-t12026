var mt=Object.create;var W=Object.defineProperty;var ft=Object.getOwnPropertyDescriptor;var wt=Object.getOwnPropertyNames;var yt=Object.getPrototypeOf,gt=Object.prototype.hasOwnProperty;var g=(e,n)=>()=>(e&&(n=e(e=0)),n);var C=(e,n)=>()=>(n||e((n={exports:{}}).exports,n),n.exports),k=(e,n)=>{for(var r in n)W(e,r,{get:n[r],enumerable:!0})},bt=(e,n,r,t)=>{if(n&&typeof n=="object"||typeof n=="function")for(let d of wt(n))!gt.call(e,d)&&d!==r&&W(e,d,{get:()=>n[d],enumerable:!(t=ft(n,d))||t.enumerable});return e};var Q=(e,n,r)=>(r=e!=null?mt(yt(e)):{},bt(n||!e||!e.__esModule?W(r,"default",{value:e,enumerable:!0}):r,e));function L(e,n){let r=URL.createObjectURL(e),t=document.createElement("a");t.href=r,t.download=n,document.body.appendChild(t),t.click(),document.body.removeChild(t),URL.revokeObjectURL(r)}var z=g(()=>{"use strict"});var ie,ce=g(()=>{"use strict";ie=function(e,n){for(let r=e.length-1;r>0;r--){let t=Math.floor(n()*(r+1));[e[r],e[t]]=[e[t],e[r]]}return e}});var de={};k(de,{default:()=>Lt,generateYoutubeMetadataTask:()=>le});import{html as It}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import qt from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function le(e,n=""){let r=String(e||"").trim().toLowerCase(),t=qt(`${Tt}#${r}#${n}`),d=ie([...Ot],t).slice(0,20+Math.floor(t()*11)),u=[300,420,600],i=[1800,2100,2400,3e3];return{source_urls:d,min_duration_seconds:u[Math.floor(t()*u.length)],max_duration_seconds:i[Math.floor(t()*i.length)],required_words:["python"],forbidden_words:["shorts","live"],limit:8+Math.floor(t()*8)}}async function Lt({user:e,weight:n=1,version:r=""}){let t=At,d="Automated Video Curation Pipeline (IITM Curation Cell)",u=le(e.email,r),i=new Blob([JSON.stringify(u,null,2)],{type:"application/json"}),o=It`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:c,weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Unable to verify response.");return s}}}var Tt,At,Ot,ue=g(()=>{"use strict";z();ce();Tt="tds-2026-05-ga3-youtube-metadata-filter-v1",At="q-youtube-metadata-filter-server",Ot=["https://www.youtube.com/watch?v=_C8kWso4ne4","https://www.youtube.com/watch?v=_K_QIx1KGuA","https://www.youtube.com/watch?v=-2uyzAqefyE","https://www.youtube.com/watch?v=-aKFBoZpiqA","https://www.youtube.com/watch?v=-ARI4Cz-awo","https://www.youtube.com/watch?v=-oPuGc05Lxs","https://www.youtube.com/watch?v=-s7e_Fy6NRU","https://www.youtube.com/watch?v=-tyBEsHSv7w","https://www.youtube.com/watch?v=0K_eZGS5NsU","https://www.youtube.com/watch?v=1PkNiYlkkjo","https://www.youtube.com/watch?v=2HfSFdPEFRg","https://www.youtube.com/watch?v=3-4qAkFRpAk","https://www.youtube.com/watch?v=3aVqWaLjqS4","https://www.youtube.com/watch?v=3dt4OGnU5sM","https://www.youtube.com/watch?v=3ohzBxoFHAY","https://www.youtube.com/watch?v=44PvX0Yv368","https://www.youtube.com/watch?v=4P4UxXK7WE8","https://www.youtube.com/watch?v=5cvM-crlDvg","https://www.youtube.com/watch?v=5i15qFTOk9A","https://www.youtube.com/watch?v=5iWhQWVXosU","https://www.youtube.com/watch?v=5pf0_bpNbkw","https://www.youtube.com/watch?v=5PrZvPeUw60","https://www.youtube.com/watch?v=6DI_7Zja8Zc","https://www.youtube.com/watch?v=6fzep1rdQwg","https://www.youtube.com/watch?v=6iF8Xb7Z3wQ","https://www.youtube.com/watch?v=6tNS--WetLI","https://www.youtube.com/watch?v=7DK70jLZBzY","https://www.youtube.com/watch?v=803Ei2Sq-Zs","https://www.youtube.com/watch?v=83-_3x2AjXI","https://www.youtube.com/watch?v=8dTpNajxaH0","https://www.youtube.com/watch?v=8v3how07th4","https://www.youtube.com/watch?v=8xHT7GZndJA","https://www.youtube.com/watch?v=8YbIwueDQx4","https://www.youtube.com/watch?v=9-vOd0UzHKY","https://www.youtube.com/watch?v=9N6a-VLBa2I","https://www.youtube.com/watch?v=9Os0o3wzS_I","https://www.youtube.com/watch?v=a48xeeo5Vnk","https://www.youtube.com/watch?v=A5AcNuXPefY","https://www.youtube.com/watch?v=acOktTcTVEQ","https://www.youtube.com/watch?v=aCULcv_IQYw","https://www.youtube.com/watch?v=afITiFR6vfw","https://www.youtube.com/watch?v=aHC3uTkT9r8","https://www.youtube.com/watch?v=ajrtAuDg3yw","https://www.youtube.com/watch?v=aRQxMYoCOuI","https://www.youtube.com/watch?v=au8xkSQW1kE","https://www.youtube.com/watch?v=bD05uGo_sVI","https://www.youtube.com/watch?v=bDhvCp3_lYw","https://www.youtube.com/watch?v=BJ-VvGyQxho","https://www.youtube.com/watch?v=bkpLhQd6YQM","https://www.youtube.com/watch?v=Blw7OF_-hXk","https://www.youtube.com/watch?v=bTMPwUgLZf0","https://www.youtube.com/watch?v=ByGJQzlzxQg","https://www.youtube.com/watch?v=BYpSfx7I6x4","https://www.youtube.com/watch?v=cLNOADl17b4","https://www.youtube.com/watch?v=cnjhHZNJEDk","https://www.youtube.com/watch?v=CQ90L5jfldw","https://www.youtube.com/watch?v=CqvZ3vGoGs0","https://www.youtube.com/watch?v=crJVzc5Ct_s","https://www.youtube.com/watch?v=CSHx6eCkmv0","https://www.youtube.com/watch?v=cY2NXB_Tqq0","https://www.youtube.com/watch?v=cYWiDiIUxQc","https://www.youtube.com/watch?v=D0iCHFXHb_g","https://www.youtube.com/watch?v=D2lwk1Ukgz0","https://www.youtube.com/watch?v=D3JvDWO-BY4","https://www.youtube.com/watch?v=D4IjxVPzb7k","https://www.youtube.com/watch?v=daefaLgNkw0","https://www.youtube.com/watch?v=dcqPhpY7tWk","https://www.youtube.com/watch?v=DEwgZNC-KyE","https://www.youtube.com/watch?v=Dh-0lAyc3Bc","https://www.youtube.com/watch?v=DjEuROpsvp4","https://www.youtube.com/watch?v=DkjCaAMBGWM","https://www.youtube.com/watch?v=DZwmZ8Usvnk","https://www.youtube.com/watch?v=e1skexBUb1M","https://www.youtube.com/watch?v=e53tmzo-U3g","https://www.youtube.com/watch?v=ecZZ8CvNQ6M","https://www.youtube.com/watch?v=eirjjyP2qcQ","https://www.youtube.com/watch?v=eXBD2bB9-RA","https://www.youtube.com/watch?v=FdVuKt_iuSI","https://www.youtube.com/watch?v=FKLr3ft8ea0","https://www.youtube.com/watch?v=FPkHecI3y_4","https://www.youtube.com/watch?v=FsAPt_9Bf3U","https://www.youtube.com/watch?v=FVpho_UiDAY","https://www.youtube.com/watch?v=g2eEQc1qEq0","https://www.youtube.com/watch?v=g33-tYIs7zU","https://www.youtube.com/watch?v=Gdys9qPjuKs","https://www.youtube.com/watch?v=GfxJYp9_nJA","https://www.youtube.com/watch?v=GkgMTyiLtWk","https://www.youtube.com/watch?v=goToXTC96Co","https://www.youtube.com/watch?v=gtjxAH8uaP0","https://www.youtube.com/watch?v=Gxpg9vvT8hE","https://www.youtube.com/watch?v=HAxm8n9QY50","https://www.youtube.com/watch?v=HW29067qVWk","https://www.youtube.com/watch?v=HYV81L7qd6M","https://www.youtube.com/watch?v=IbUa1tTT-7k","https://www.youtube.com/watch?v=iNEwkaYmPqY","https://www.youtube.com/watch?v=IolxqkL7cD8","https://www.youtube.com/watch?v=iv5m0c-8Opc","https://www.youtube.com/watch?v=iWS9ogMPOI0","https://www.youtube.com/watch?v=j4bhmlkpLfc","https://www.youtube.com/watch?v=jCzT9XFZ5bw","https://www.youtube.com/watch?v=JVQNywo4AbU","https://www.youtube.com/watch?v=jxmzY9soFXg","https://www.youtube.com/watch?v=k8asfUbWbI4","https://www.youtube.com/watch?v=K8L6KVGG-7o","https://www.youtube.com/watch?v=k9TUPpGqYTo","https://www.youtube.com/watch?v=KB2CtEDrglY","https://www.youtube.com/watch?v=KgCgpCIOkIs","https://www.youtube.com/watch?v=khKv-8q7YmY","https://www.youtube.com/watch?v=KlBPCzcQNU8","https://www.youtube.com/watch?v=kt3ZtW9MXhw","https://www.youtube.com/watch?v=KzqSDvzOFNA","https://www.youtube.com/watch?v=lbY9r0rHTQc","https://www.youtube.com/watch?v=Liv6eeb1VfE","https://www.youtube.com/watch?v=Lu8lXXlstvM","https://www.youtube.com/watch?v=LUFn-QVcmB8","https://www.youtube.com/watch?v=m42FB3RY0TQ","https://www.youtube.com/watch?v=M54UFvJqQ5I","https://www.youtube.com/watch?v=mB0EBW-vDSQ","https://www.youtube.com/watch?v=mkYBJwX_dMs","https://www.youtube.com/watch?v=MwZwr5Tvyxo","https://www.youtube.com/watch?v=mXR47qiTdWQ","https://www.youtube.com/watch?v=N5vscPTWKOk","https://www.youtube.com/watch?v=Na8h09Goovk","https://www.youtube.com/watch?v=NDFbXIiqT4o","https://www.youtube.com/watch?v=NDFMa5FSQuI","https://www.youtube.com/watch?v=NeJKaolLQqU","https://www.youtube.com/watch?v=ng2o98k983k","https://www.youtube.com/watch?v=nghuHvKLhJA","https://www.youtube.com/watch?v=NhidVhNHfeU","https://www.youtube.com/watch?v=NIWwJbo-9_8","https://www.youtube.com/watch?v=OdIHeg4jj2c","https://www.youtube.com/watch?v=OebyvmZo3w0","https://www.youtube.com/watch?v=OEJv74QnduA","https://www.youtube.com/watch?v=Oh2Dkkswy30","https://www.youtube.com/watch?v=pd-0G0MigUA","https://www.youtube.com/watch?v=PSNXoAs2FtQ","https://www.youtube.com/watch?v=PSWf2TjTGNY","https://www.youtube.com/watch?v=PUIE7CPANfo","https://www.youtube.com/watch?v=q4jPR-M0TAQ","https://www.youtube.com/watch?v=q5uM4VKywbA","https://www.youtube.com/watch?v=q7Bo_J8x_dw","https://www.youtube.com/watch?v=qbLc5a9jdXo","https://www.youtube.com/watch?v=qDwdMDQ8oX4","https://www.youtube.com/watch?v=QErlGfPRoUU","https://www.youtube.com/watch?v=qfWpPEgea2A","https://www.youtube.com/watch?v=qJPw_IVEyfc","https://www.youtube.com/watch?v=QnDWIZuWYW0","https://www.youtube.com/watch?v=QVdf0LgmICw","https://www.youtube.com/watch?v=QyhqzaMiFxk","https://www.youtube.com/watch?v=r-uOLxNrNk8","https://www.youtube.com/watch?v=R67XuYc9NQ4","https://www.youtube.com/watch?v=rkzpx5Bkbek","https://www.youtube.com/watch?v=roTZJaxjnJc","https://www.youtube.com/watch?v=rq8cL2XMM5M","https://www.youtube.com/watch?v=RSl87lqOXDE","https://www.youtube.com/watch?v=S5Dn1HjBPA4","https://www.youtube.com/watch?v=Sa_kQheCnds","https://www.youtube.com/watch?v=St48epdRDZw","https://www.youtube.com/watch?v=sugvnHA7ElY","https://www.youtube.com/watch?v=Sw79_adeUR0","https://www.youtube.com/watch?v=SwSbnmqk3zY","https://www.youtube.com/watch?v=T6y2LRcX9qM","https://www.youtube.com/watch?v=t8hG0WnyHgU","https://www.youtube.com/watch?v=T9Jh_X134l4","https://www.youtube.com/watch?v=tf3ezjeTpfI","https://www.youtube.com/watch?v=tiBeLLv5GJo","https://www.youtube.com/watch?v=TIZRskDMyA4","https://www.youtube.com/watch?v=tJxcKyFMTGo","https://www.youtube.com/watch?v=u0oDDZrDz9U","https://www.youtube.com/watch?v=U2ZN104hIcc","https://www.youtube.com/watch?v=Uh2ebFW8OYM","https://www.youtube.com/watch?v=uHd7KDesmkM","https://www.youtube.com/watch?v=UIJKdCIEXUQ","https://www.youtube.com/watch?v=uL0-6kfiH3g","https://www.youtube.com/watch?v=UlygQI2eSdg","https://www.youtube.com/watch?v=UmljXZIypDc","https://www.youtube.com/watch?v=uVNfQDohYNI","https://www.youtube.com/watch?v=Vde5SH8e1OQ","https://www.youtube.com/watch?v=ve2pmm5JqmI","https://www.youtube.com/watch?v=vTX3IwquFkc","https://www.youtube.com/watch?v=vuDCndpkutQ","https://www.youtube.com/watch?v=vutyTx7IaAI","https://www.youtube.com/watch?v=W8KRzm-HUcc","https://www.youtube.com/watch?v=WbTOutpwPHs","https://www.youtube.com/watch?v=Wfx4YBzg16s","https://www.youtube.com/watch?v=WXsD0ZgxjRw","https://www.youtube.com/watch?v=x3v9zMX1s4s","https://www.youtube.com/watch?v=XBksHCvObhQ","https://www.youtube.com/watch?v=xFciV6Ew5r4","https://www.youtube.com/watch?v=XGa4onZP66Q","https://www.youtube.com/watch?v=xLw9wf9uNuw","https://www.youtube.com/watch?v=XMmfJFS_MFQ","https://www.youtube.com/watch?v=Xnbef8F_Yfc","https://www.youtube.com/watch?v=XrW2RaQnJYw","https://www.youtube.com/watch?v=xwPWcFKeIac","https://www.youtube.com/watch?v=xXibS9832FM","https://www.youtube.com/watch?v=YJC6ldI3hWk","https://www.youtube.com/watch?v=YST1sWFPDh4","https://www.youtube.com/watch?v=YYXdXT2l-Gg","https://www.youtube.com/watch?v=Z81JW1NTsO8"]});var he={};k(he,{default:()=>$t});import{html as _t}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import Ct from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function Mt(e,n=""){let r=String(e||"").trim().toLowerCase(),t=Ct(`${Et}#${r}#${n}`),d=[...zt];for(let i=d.length-1;i>0;i--){let o=Math.floor(t()*(i+1));[d[i],d[o]]=[d[o],d[i]]}let u=d.slice(0,3);return{description:"Sample images for local testing. The grader uses DIFFERENT hidden images with the same categories.",endpoint_spec:{method:"POST",path:"/answer-image",content_type:"application/json",request_body:{image_base64:"<base64-encoded PNG image>",question:"<natural-language question about the image>"},response_body:{answer:"<string or number answer extracted from the image>"},notes:["The 'answer' field must always be a string.","For numeric answers, return the number as a string (e.g. '4089.35').","Do not include units or extra text \u2014 just the raw answer value.","Enable CORS: the grader sends requests from a Cloudflare Worker.","Use any multimodal model (e.g. Gemini, GPT-4o, Claude) or OCR pipeline."]},sample_images:u.map((i,o)=>({image_id:`sample_${String(o+1).padStart(3,"0")}`,type:i.type,description:i.description,sample_question:i.sample_question}))}}async function $t({user:e,weight:n=1,version:r=""}){let t=Nt,d="Multimodal Image Question-Answering API (NovaCorp Analytics)",u=Mt(e.email,r),i=new Blob([JSON.stringify(u,null,2)],{type:"application/json"}),o=_t`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=String(c||"").trim();if(!a)throw new Error("Enter your deployed API base URL.");if(!/^https?:\/\//i.test(a))throw new Error("URL must start with http:// or https://.");let s;try{s=new URL(a).hostname}catch{throw new Error("That doesn't look like a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(s))throw new Error("The grader can't reach a private/localhost address \u2014 deploy publicly or use a tunnel.");let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),p=await h.json();if(!h.ok)throw new Error(p.error||"Unable to verify response.");return p}}}var Et,Nt,zt,pe=g(()=>{"use strict";z();Et="tds-2026-05-ga3-multimodal-image-qa-client-v1",Nt="q-multimodal-image-qa-server",zt=[{type:"bar_chart",description:"A bar chart showing monthly sales figures for a retail store. Each bar is labelled with a month name and a numeric value.",sample_question:"What is the total sales value across all months shown in the chart?"},{type:"receipt",description:"A printed receipt from a grocery store listing item names, quantities, unit prices, and a total at the bottom.",sample_question:"What is the grand total on the receipt?"},{type:"data_table",description:"A plain table with 3\u20135 columns and 5\u201310 rows, containing numeric data (e.g. student scores, stock prices).",sample_question:"What is the maximum value in the 'Score' column?"},{type:"invoice",description:"A business invoice with vendor name, invoice number, line items (description, qty, unit price, subtotal), tax, and grand total.",sample_question:"What is the invoice grand total including tax?"},{type:"pie_chart",description:"A pie chart showing the percentage breakdown of a budget across named categories (e.g. Housing, Food, Transport).",sample_question:"Which category has the largest share of the budget?"}]});var me={};k(me,{default:()=>Jt});import{html as Dt}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import Pt from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function Ht(e,n=""){let r=Pt(`${Rt}#${String(e||"").trim().toLowerCase()}#${n}`),t=[0,1,2].sort(()=>r()-.5).slice(0,2);return{description:"Sample invoice texts for local testing. The grader uses DIFFERENT hidden invoices.",output_schema:{invoice_no:"string (null if not found)",date:"string YYYY-MM-DD (null if not found)",vendor:"string (null if not found)",amount:"number \u2014 subtotal before tax (null if not found)",tax:"number \u2014 tax amount (null if not found)",currency:"string e.g. INR, USD (null if not found)"},samples:t.map(d=>({invoice_text:jt[d].invoice_text}))}}async function Jt({user:e,weight:n=1,version:r=""}){let t=Ut,d="Fixed Schema Invoice Extraction API (IITM Finance Cell)",u=Ht(e.email,r),i=new Blob([JSON.stringify(u,null,2)],{type:"application/json"}),o=Dt`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=String(c||"").trim();if(!a)throw new Error("Enter your deployed API base URL.");if(!/^https?:\/\//i.test(a))throw new Error("URL must start with http:// or https://.");let s;try{s=new URL(a).hostname}catch{throw new Error("Not a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(s))throw new Error("The grader can't reach a localhost address \u2014 deploy publicly or use a tunnel.");let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),p=await h.json();if(!h.ok)throw new Error(p.error||"Unable to verify.");return p}}}var Rt,Ut,jt,fe=g(()=>{"use strict";z();Rt="tds-2026-05-ga3-invoice-extract-client-v1",Ut="q-invoice-extract-server",jt=[{invoice_text:`INVOICE
Invoice No: INV-2026-0041
Date: 15 March 2026
Vendor: TechParts Pvt Ltd
Bill To: IITM Procurement Dept

Items:
  USB-C Hub (x2) ............. Rs. 1,299.00
  HDMI Cable (x3) ............. Rs.   450.00
                                ----------
  Subtotal ...................  Rs. 2,199.00
  GST (18%) ..................  Rs.   395.82
                                ----------
  TOTAL ......................  Rs. 2,594.82
Currency: INR`,expected:{invoice_no:"INV-2026-0041",date:"2026-03-15",vendor:"TechParts Pvt Ltd",amount:2199,tax:395.82,currency:"INR"}},{invoice_text:`NovaSoft Solutions \u2014 Tax Invoice
Ref: NS/2026/778
Issued: 2026-01-22
Client: DataFlow Analytics

Service: API Integration & Consulting \u2014 40 hrs @ Rs. 3,500/hr
Subtotal: Rs. 1,40,000.00
IGST (18%): Rs. 25,200.00
Total Due: Rs. 1,65,200.00
Currency: INR`,expected:{invoice_no:"NS/2026/778",date:"2026-01-22",vendor:"NovaSoft Solutions",amount:14e4,tax:25200,currency:"INR"}},{invoice_text:`COMMERCIAL INVOICE
Invoice #: 2026-MKT-009
Date: April 3, 2026
Seller: Bright Displays Ltd

Description: LED Monitor 27" (qty 5) @ USD 320 each
Subtotal: USD 1,600.00
VAT (10%): USD 160.00
Grand Total: USD 1,760.00`,expected:{invoice_no:"2026-MKT-009",date:"2026-04-03",vendor:"Bright Displays Ltd",amount:1600,tax:160,currency:"USD"}}]});var ye={};k(ye,{default:()=>Vt});import{html as Yt}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import Ft from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function Bt(e,n=""){let r=Ft(`${Wt}#${String(e||"").trim().toLowerCase()}#${n}`),t=[0,1,2].sort(()=>r()-.5).slice(0,2);return{description:"Sample (text, schema) pairs for local testing. The grader uses DIFFERENT hidden pairs.",supported_types:["string","integer","float","boolean","date","array[string]","array[integer]"],type_notes:{date:"Return as ISO format: YYYY-MM-DD",float:"Return as a JSON number (not a string)",integer:"Return as a JSON integer",boolean:"Return true or false","array[string]":"Return as a JSON array of strings"},samples:t.map(d=>({text:we[d].text,schema:we[d].schema}))}}async function Vt({user:e,weight:n=1,version:r=""}){let t=Qt,d="Dynamic Schema Structured Extraction API (DataBridge Inc.)",u=Bt(e.email,r),i=new Blob([JSON.stringify(u,null,2)],{type:"application/json"}),o=Yt`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=String(c||"").trim();if(!a)throw new Error("Enter your deployed API base URL.");if(!/^https?:\/\//i.test(a))throw new Error("URL must start with http:// or https://.");let s;try{s=new URL(a).hostname}catch{throw new Error("Not a valid URL.")}if(/^(localhost|127\.|0\.0\.0\.0|10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.|\[?::1\]?)/i.test(s))throw new Error("The grader can't reach a localhost address \u2014 deploy publicly or use a tunnel.");let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),p=await h.json();if(!h.ok)throw new Error(p.error||"Unable to verify.");return p}}}var Wt,Qt,we,ge=g(()=>{"use strict";z();Wt="tds-2026-05-ga3-dynamic-extract-client-v1",Qt="q-dynamic-extract-server",we=[{text:"Rahul bought 3 notebooks for Rs. 240 on 12 June 2026 from Alpha Store.",schema:{customer_name:"string",item:"string",quantity:"integer",amount:"float",purchase_date:"date",store:"string"},expected:{customer_name:"Rahul",item:"notebooks",quantity:3,amount:240,purchase_date:"2026-06-12",store:"Alpha Store"}},{text:"The server went down at 14:32 on 2026-05-20. Root cause: disk full. Severity: critical. Team: infrastructure.",schema:{event_time:"string",root_cause:"string",severity:"string",team:"string"},expected:{event_time:"14:32",root_cause:"disk full",severity:"critical",team:"infrastructure"}},{text:"Order #ORD-5521 placed on 3rd March 2026. Items: 2 USB hubs and 5 HDMI cables. Total: $89.50. Shipped to: Bangalore.",schema:{order_id:"string",order_date:"date",total_amount:"float",city:"string"},expected:{order_id:"ORD-5521",order_date:"2026-03-03",total_amount:89.5,city:"Bangalore"}}]});var ve={};k(ve,{default:()=>ao});import{html as Xt}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";import Gt from"https://cdn.jsdelivr.net/npm/seedrandom@3.0.5/+esm";function eo(e){let n=0,r=0;for(;n===0;)n=e();for(;r===0;)r=e();return Math.sqrt(-2*Math.log(n))*Math.cos(2*Math.PI*r)}function xe(e,n){let r=Array.from({length:n},()=>eo(e)),t=Math.sqrt(r.reduce((d,u)=>d+u*u,0));return r.map(d=>d/t)}function be(e,n,r){let t=xe(e,r),d=n.map((i,o)=>i*.85+t[o]*.15),u=Math.sqrt(d.reduce((i,o)=>i+o*o,0));return d.map(i=>i/u)}function to(e,n,r=""){let t=Gt(`${e}#${String(n||"").trim().toLowerCase()}#${r}`),d={};for(let o of U)d[o]=xe(t,M);let u=[];for(let o=0;o<H;o++){let l=U[o%U.length],c=be(t,d[l],M),a=B[l],s=Array.from({length:4},()=>a[Math.floor(t()*a.length)]);u.push({doc_id:`D${String(o+1).padStart(6,"0")}`,topic:l,title:s.join(" ")+" overview",embedding:c})}let i=[];for(let o=0;o<J;o++){let l=U[o%U.length],c=be(t,d[l],M),a=B[l],s=Array.from({length:3},()=>a[Math.floor(t()*a.length)]);i.push({query_id:`Q${String(o+1).padStart(3,"0")}`,query_text:s.join(" ")+" techniques",embedding:c})}return{documents:u,queries:i}}function oo(e,n=""){let{documents:r,queries:t}=to(Kt,e,n);return{description:["Your task: for each query, find the top 5 most similar documents by cosine similarity.",`Documents: ${H} | Queries: ${J} | Embedding dimension: ${M}`,"Submit a JSON object mapping each query_id to a list of 5 doc_ids (ordered by similarity, highest first).","Tie-break rule: if two documents have equal similarity, the one with the smaller doc_id comes first."].join(`
`),num_documents:H,num_queries:J,embedding_dim:M,documents:r.map(({doc_id:d,title:u,embedding:i})=>({doc_id:d,title:u,embedding:i})),queries:t.map(({query_id:d,query_text:u,embedding:i})=>({query_id:d,query_text:u,embedding:i})),expected_answer_format:{Q001:["D000001","D000002","D000003","D000004","D000005"],"...":"..."}}}async function ao({user:e,weight:n=1,version:r=""}){let t=Zt,d="Cosine Similarity Search (VecSearch Labs)",u=oo(e.email,r),i=new Blob([JSON.stringify(u,null,2)],{type:"application/json"}),o=Xt`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a;try{a=JSON.parse(String(c||"").trim())}catch{throw new Error("Answer must be valid JSON.")}if(typeof a!="object"||Array.isArray(a))throw new Error("Answer must be a JSON object mapping query IDs to arrays of doc IDs.");let s=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),h=await s.json();if(!s.ok)throw new Error(h.error||"Unable to verify.");return h}}}var Kt,Zt,B,U,M,H,J,ke=g(()=>{"use strict";z();Kt="tds-2026-05-ga3-cosine-sim-client-v1",Zt="q-cosine-similarity-server",B={ML:["neural","gradient","backprop","loss","epoch","batch","model","train","feature","weight","activation","layer","dropout","learning","inference","embedding","transformer","attention"],DATA:["query","database","index","schema","table","row","column","join","aggregate","filter","pipeline","etl","warehouse","stream","batch","partition","shard","replica"],WEB:["http","request","response","cache","cookie","session","token","api","endpoint","rest","graphql","websocket","latency","throughput","bandwidth","proxy","cdn","tls"],MATH:["vector","matrix","eigenvalue","integral","derivative","probability","distribution","variance","covariance","correlation","regression","hypothesis","bayes","entropy","gradient","manifold"],CLOUD:["container","kubernetes","docker","pod","service","deployment","scaling","ingress","node","cluster","autoscale","loadbalancer","microservice","serverless","function","bucket","volume"]},U=Object.keys(B),M=64,H=250,J=10});var Se={};k(Se,{default:()=>ro});import{html as no}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function ro({user:e,weight:n=3,version:r=""}){let t="q-korean-audio-dataset-server",d="\u97D3\u56FD\u8A9E\u97F3\u58F0\u30C7\u30FC\u30BF\u30BB\u30C3\u30C8API\u691C\u8A3C",i=no`
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
  `;return{id:t,title:d,weight:n,question:i,answer:async l=>{let c=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:{url:l,phase:"preview"},weight:n,questionId:t,version:r})}),a=await c.json();if(!c.ok)throw new Error(a.error||"\u691C\u8A3C\u306B\u5931\u6557\u3057\u307E\u3057\u305F\u3002");return a}}}var Ie=g(()=>{"use strict"});var qe={};k(qe,{default:()=>io});import{html as so}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function io({user:e,weight:n=3,version:r=""}){let t="q-structured-extraction-server",d="Invoice Intelligence \u2014 Structured Extraction API",u={document_id:"doc0",text:"INVOICE from Acme Industrial Supply. ...",schema:{type:"object",properties:{"...":"(JSON Schema describing the exact output)"}}},i={vendor:"Acme Industrial Supply",currency:"USD",total_amount:12480,invoice_date:"2024-03-03",due_in_days:30,is_paid:!1,priority:"high",contact_email:"ap@acme.com",line_items:[{sku:"WIDGET-204",quantity:12,unit_price:40},{sku:"BOLT-118",quantity:200,unit_price:5}],item_count:2},o=so`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:{url:c,phase:"preview"},weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}}}var Te=g(()=>{"use strict"});var Ae={};k(Ae,{default:()=>lo});import{html as co}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function lo({user:e,weight:n=3,version:r=""}){let t="q-semantic-rank-server",d="Semantic Search \u2014 Top-K Ranking API",u={query_id:"q0",query:"How do I automatically scale the number of pods when CPU usage rises?",candidates:["A valley fold creases the paper so the crease points toward you.","Horizontal Pod Autoscaler adds or removes pods based on observed CPU or custom metrics.","... (18 candidate paragraphs in total) ..."]},i={ranking:[1,7,12]},o=co`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:{url:c,phase:"preview"},weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}}}var Oe=g(()=>{"use strict"});var Le={};k(Le,{default:()=>ho});import{html as uo}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function ho({user:e,weight:n=3,version:r=""}){let t="q-cot-math-verifier-server",d="Reliable Reasoning \u2014 Word-Problem Solver API",u={problem_id:"p0",problem:"A workshop orders 150 tiles at 8 dollars each. Any order of more than 50 units earns a 25% bulk discount ..."},i={reasoning:"Base = 150 * 8 = 1200. Order > 50 so apply 25% discount: 1200 * 0.75 = 900. Add 5% tax: 900 * 1.05 = 945. The km and product-line counts are irrelevant.",answer:945},o=uo`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:{url:c,phase:"preview"},weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}}}var _e=g(()=>{"use strict"});var Ce={};k(Ce,{default:()=>mo});import{html as po}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function mo({user:e,weight:n=3,version:r=""}){let t="q-proof-of-work-server",d="Proof-of-Work \u2014 Nonce Hunt",u=`./questionData?email=${encodeURIComponent(e.email)}&quizSign=${encodeURIComponent(e.quizSign||"")}&questionId=${encodeURIComponent(t)}&version=${encodeURIComponent(r)}`,i=po`
    <div class="mb-3">
      <p class="lead text-primary">
        <strong>Scenario:</strong> Mine a proof-of-work. Your token and difficulty are assigned below (unique to you).
      </p>
      <p>
        Find a non-negative integer <strong>nonce</strong> such that the SHA-256 hash of the exact UTF-8 string
        <code>&lt;token&gt;:&lt;nonce&gt;</code> has at least the required number of <strong>leading zero bits</strong>
        (the 256-bit big-endian digest must start with that many zero bits). Submit the nonce.
      </p>
      <ul>
        <li>Hash spec: <code>sha256(f"{token}:{nonce}")</code>, leading zero <em>bits</em> of the raw 32-byte digest.</li>
        <li>Expected work ≈ 2<sup>difficulty</sup> hashes — write a fast miner (e.g. <code>hashlib</code> + multiprocessing).</li>
        <li>There is no shortcut (SHA-256 can't be reversed), and a nonce mined for someone else's token will not validate for yours.</li>
      </ul>

      <iframe
        title="Your assigned token and difficulty"
        src="${u}"
        style="width:100%;height:380px;border:1px solid #dee2e6;border-radius:12px;background:#1e1e2e"
      ></iframe>

      <label for="${t}" class="form-label mt-3"><strong>Your nonce</strong></label>
      <input
        class="form-control font-monospace"
        id="${t}"
        name="${t}"
        type="text"
        inputmode="numeric"
        placeholder="e.g. 48217734"
      />
    </div>
  `;return{id:t,title:d,weight:n,question:i,answer:async l=>{let c=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:l,weight:n,questionId:t,version:r})}),a=await c.json();if(!c.ok)throw new Error(a.error||"Verification failed.");return a}}}var Ee=g(()=>{"use strict"});var ze=C((Ne,V)=>{(function(e,n,r){function t(o){var l=this,c=i();l.next=function(){var a=2091639*l.s0+l.c*23283064365386963e-26;return l.s0=l.s1,l.s1=l.s2,l.s2=a-(l.c=a|0)},l.c=1,l.s0=c(" "),l.s1=c(" "),l.s2=c(" "),l.s0-=c(o),l.s0<0&&(l.s0+=1),l.s1-=c(o),l.s1<0&&(l.s1+=1),l.s2-=c(o),l.s2<0&&(l.s2+=1),c=null}function d(o,l){return l.c=o.c,l.s0=o.s0,l.s1=o.s1,l.s2=o.s2,l}function u(o,l){var c=new t(o),a=l&&l.state,s=c.next;return s.int32=function(){return c.next()*4294967296|0},s.double=function(){return s()+(s()*2097152|0)*11102230246251565e-32},s.quick=s,a&&(typeof a=="object"&&d(a,c),s.state=function(){return d(c,{})}),s}function i(){var o=4022871197,l=function(c){c=String(c);for(var a=0;a<c.length;a++){o+=c.charCodeAt(a);var s=.02519603282416938*o;o=s>>>0,s-=o,s*=o,o=s>>>0,s-=o,o+=s*4294967296}return(o>>>0)*23283064365386963e-26};return l}n&&n.exports?n.exports=u:r&&r.amd?r(function(){return u}):this.alea=u})(Ne,typeof V=="object"&&V,typeof define=="function"&&define)});var $e=C((Me,X)=>{(function(e,n,r){function t(i){var o=this,l="";o.x=0,o.y=0,o.z=0,o.w=0,o.next=function(){var a=o.x^o.x<<11;return o.x=o.y,o.y=o.z,o.z=o.w,o.w^=o.w>>>19^a^a>>>8},i===(i|0)?o.x=i:l+=i;for(var c=0;c<l.length+64;c++)o.x^=l.charCodeAt(c)|0,o.next()}function d(i,o){return o.x=i.x,o.y=i.y,o.z=i.z,o.w=i.w,o}function u(i,o){var l=new t(i),c=o&&o.state,a=function(){return(l.next()>>>0)/4294967296};return a.double=function(){do var s=l.next()>>>11,h=(l.next()>>>0)/4294967296,p=(s+h)/(1<<21);while(p===0);return p},a.int32=l.next,a.quick=a,c&&(typeof c=="object"&&d(c,l),a.state=function(){return d(l,{})}),a}n&&n.exports?n.exports=u:r&&r.amd?r(function(){return u}):this.xor128=u})(Me,typeof X=="object"&&X,typeof define=="function"&&define)});var Pe=C((De,G)=>{(function(e,n,r){function t(i){var o=this,l="";o.next=function(){var a=o.x^o.x>>>2;return o.x=o.y,o.y=o.z,o.z=o.w,o.w=o.v,(o.d=o.d+362437|0)+(o.v=o.v^o.v<<4^(a^a<<1))|0},o.x=0,o.y=0,o.z=0,o.w=0,o.v=0,i===(i|0)?o.x=i:l+=i;for(var c=0;c<l.length+64;c++)o.x^=l.charCodeAt(c)|0,c==l.length&&(o.d=o.x<<10^o.x>>>4),o.next()}function d(i,o){return o.x=i.x,o.y=i.y,o.z=i.z,o.w=i.w,o.v=i.v,o.d=i.d,o}function u(i,o){var l=new t(i),c=o&&o.state,a=function(){return(l.next()>>>0)/4294967296};return a.double=function(){do var s=l.next()>>>11,h=(l.next()>>>0)/4294967296,p=(s+h)/(1<<21);while(p===0);return p},a.int32=l.next,a.quick=a,c&&(typeof c=="object"&&d(c,l),a.state=function(){return d(l,{})}),a}n&&n.exports?n.exports=u:r&&r.amd?r(function(){return u}):this.xorwow=u})(De,typeof G=="object"&&G,typeof define=="function"&&define)});var Ue=C((Re,K)=>{(function(e,n,r){function t(i){var o=this;o.next=function(){var c=o.x,a=o.i,s,h,p;return s=c[a],s^=s>>>7,h=s^s<<24,s=c[a+1&7],h^=s^s>>>10,s=c[a+3&7],h^=s^s>>>3,s=c[a+4&7],h^=s^s<<7,s=c[a+7&7],s=s^s<<13,h^=s^s<<9,c[a]=h,o.i=a+1&7,h};function l(c,a){var s,h,p=[];if(a===(a|0))h=p[0]=a;else for(a=""+a,s=0;s<a.length;++s)p[s&7]=p[s&7]<<15^a.charCodeAt(s)+p[s+1&7]<<13;for(;p.length<8;)p.push(0);for(s=0;s<8&&p[s]===0;++s);for(s==8?h=p[7]=-1:h=p[s],c.x=p,c.i=0,s=256;s>0;--s)c.next()}l(o,i)}function d(i,o){return o.x=i.x.slice(),o.i=i.i,o}function u(i,o){i==null&&(i=+new Date);var l=new t(i),c=o&&o.state,a=function(){return(l.next()>>>0)/4294967296};return a.double=function(){do var s=l.next()>>>11,h=(l.next()>>>0)/4294967296,p=(s+h)/(1<<21);while(p===0);return p},a.int32=l.next,a.quick=a,c&&(c.x&&d(c,l),a.state=function(){return d(l,{})}),a}n&&n.exports?n.exports=u:r&&r.amd?r(function(){return u}):this.xorshift7=u})(Re,typeof K=="object"&&K,typeof define=="function"&&define)});var He=C((je,Z)=>{(function(e,n,r){function t(i){var o=this;o.next=function(){var c=o.w,a=o.X,s=o.i,h,p;return o.w=c=c+1640531527|0,p=a[s+34&127],h=a[s=s+1&127],p^=p<<13,h^=h<<17,p^=p>>>15,h^=h>>>12,p=a[s]=p^h,o.i=s,p+(c^c>>>16)|0};function l(c,a){var s,h,p,b,T,A=[],$=128;for(a===(a|0)?(h=a,a=null):(a=a+"\0",h=0,$=Math.max($,a.length)),p=0,b=-32;b<$;++b)a&&(h^=a.charCodeAt((b+32)%a.length)),b===0&&(T=h),h^=h<<10,h^=h>>>15,h^=h<<4,h^=h>>>13,b>=0&&(T=T+1640531527|0,s=A[b&127]^=h+T,p=s==0?p+1:0);for(p>=128&&(A[(a&&a.length||0)&127]=-1),p=127,b=512;b>0;--b)h=A[p+34&127],s=A[p=p+1&127],h^=h<<13,s^=s<<17,h^=h>>>15,s^=s>>>12,A[p]=h^s;c.w=T,c.X=A,c.i=p}l(o,i)}function d(i,o){return o.i=i.i,o.w=i.w,o.X=i.X.slice(),o}function u(i,o){i==null&&(i=+new Date);var l=new t(i),c=o&&o.state,a=function(){return(l.next()>>>0)/4294967296};return a.double=function(){do var s=l.next()>>>11,h=(l.next()>>>0)/4294967296,p=(s+h)/(1<<21);while(p===0);return p},a.int32=l.next,a.quick=a,c&&(c.X&&d(c,l),a.state=function(){return d(l,{})}),a}n&&n.exports?n.exports=u:r&&r.amd?r(function(){return u}):this.xor4096=u})(je,typeof Z=="object"&&Z,typeof define=="function"&&define)});var Ye=C((Je,ee)=>{(function(e,n,r){function t(i){var o=this,l="";o.next=function(){var a=o.b,s=o.c,h=o.d,p=o.a;return a=a<<25^a>>>7^s,s=s-h|0,h=h<<24^h>>>8^p,p=p-a|0,o.b=a=a<<20^a>>>12^s,o.c=s=s-h|0,o.d=h<<16^s>>>16^p,o.a=p-a|0},o.a=0,o.b=0,o.c=-1640531527,o.d=1367130551,i===Math.floor(i)?(o.a=i/4294967296|0,o.b=i|0):l+=i;for(var c=0;c<l.length+20;c++)o.b^=l.charCodeAt(c)|0,o.next()}function d(i,o){return o.a=i.a,o.b=i.b,o.c=i.c,o.d=i.d,o}function u(i,o){var l=new t(i),c=o&&o.state,a=function(){return(l.next()>>>0)/4294967296};return a.double=function(){do var s=l.next()>>>11,h=(l.next()>>>0)/4294967296,p=(s+h)/(1<<21);while(p===0);return p},a.int32=l.next,a.quick=a,c&&(typeof c=="object"&&d(c,l),a.state=function(){return d(l,{})}),a}n&&n.exports?n.exports=u:r&&r.amd?r(function(){return u}):this.tychei=u})(Je,typeof ee=="object"&&ee,typeof define=="function"&&define)});var Fe=C(()=>{});var Qe=C((We,Y)=>{(function(e,n,r){var t=256,d=6,u=52,i="random",o=r.pow(t,d),l=r.pow(2,u),c=l*2,a=t-1,s;function h(m,f,x){var y=[];f=f==!0?{entropy:!0}:f||{};var w=A(T(f.entropy?[m,D(n)]:m??$(),3),y),S=new p(y),q=function(){for(var I=S.g(d),_=o,O=0;I<l;)I=(I+O)*t,_*=t,O=S.g(1);for(;I>=c;)I/=2,_/=2,O>>>=1;return(I+O)/_};return q.int32=function(){return S.g(4)|0},q.quick=function(){return S.g(4)/4294967296},q.double=q,A(D(S.S),n),(f.pass||x||function(I,_,O,E){return E&&(E.S&&b(E,S),I.state=function(){return b(S,{})}),O?(r[i]=I,_):I})(q,w,"global"in f?f.global:this==r,f.state)}function p(m){var f,x=m.length,y=this,w=0,S=y.i=y.j=0,q=y.S=[];for(x||(m=[x++]);w<t;)q[w]=w++;for(w=0;w<t;w++)q[w]=q[S=a&S+m[w%x]+(f=q[w])],q[S]=f;(y.g=function(I){for(var _,O=0,E=y.i,j=y.j,P=y.S;I--;)_=P[E=a&E+1],O=O*t+P[a&(P[E]=P[j=a&j+_])+(P[j]=_)];return y.i=E,y.j=j,O})(t)}function b(m,f){return f.i=m.i,f.j=m.j,f.S=m.S.slice(),f}function T(m,f){var x=[],y=typeof m,w;if(f&&y=="object")for(w in m)try{x.push(T(m[w],f-1))}catch{}return x.length?x:y=="string"?m:m+"\0"}function A(m,f){for(var x=m+"",y,w=0;w<x.length;)f[a&w]=a&(y^=f[a&w]*19)+x.charCodeAt(w++);return D(f)}function $(){try{var m;return s&&(m=s.randomBytes)?m=m(t):(m=new Uint8Array(t),(e.crypto||e.msCrypto).getRandomValues(m)),D(m)}catch{var f=e.navigator,x=f&&f.plugins;return[+new Date,e,x,e.screen,D(n)]}}function D(m){return String.fromCharCode.apply(0,m)}if(A(r.random(),n),typeof Y=="object"&&Y.exports){Y.exports=h;try{s=Fe()}catch{}}else typeof define=="function"&&define.amd?define(function(){return h}):r["seed"+i]=h})(typeof self<"u"?self:We,[],Math)});var F=C((ba,Be)=>{var fo=ze(),wo=$e(),yo=Pe(),go=Ue(),bo=He(),xo=Ye(),N=Qe();N.alea=fo;N.xor128=wo;N.xorwow=yo;N.xorshift7=go;N.xor4096=bo;N.tychei=xo;Be.exports=N});function Io(e){let n=2166136261;for(let r=0;r<e.length;r++)n^=e.charCodeAt(r),n=Math.imul(n,16777619);return(n>>>0).toString(16).padStart(8,"0")}function qo(e,n,r){let t=e.filter(d=>d!==n);return t[Math.floor(r()*t.length)]}function To(e,n){let r=Ve[Math.floor(n()*Ve.length)],t=Math.floor(n()*900+100),d=Math.floor(n()*90+10);return`Operational note ${String(e+1).padStart(4,"0")}: The ${r} audit for lane ${t} records shard ${d}. This paragraph is deliberately ordinary context. It mentions retrieval, chunking, summaries, ranking, model calls, and token budgets, but it does not answer any of the ten numbered questions. Keep it only if your pipeline believes it is useful evidence.`}function Ao(e,n=""){let t=`${String(e||"").trim().toLowerCase()}#${Xe}#${n}`,d=(0,te.default)(t),u=Io(t),i=8e3+Math.floor(d()*22001),o=So.map(l=>{let c=l.values[Math.floor(d()*l.values.length)],a=qo(l.values,c,d);return{...l,answer:c,staleAnswer:a}});return{seedHash:u,targetTokens:i,tokenLimitPerCall:vo,totalTokenBudget:ko,facts:o}}function Ge(e,n=""){let r=Ao(e,n),t=(0,te.default)(`${String(e).trim().toLowerCase()}#${Xe}#haystack#${n}`),d=Math.ceil(r.targetTokens/38),u=Array.from({length:d},(c,a)=>To(a,t)),i=Math.max(8,Math.floor(d/(r.facts.length+2)));r.facts.forEach((c,a)=>{let s=Math.min(d-2,2+a*i+Math.floor(t()*Math.max(2,i/3))),h=Math.min(d-1,s+Math.max(5,Math.floor(i/2))+Math.floor(t()*i));u[s]+=`

${c.stale(c.staleAnswer)}`,u[h]+=`

${c.current(c.answer)}`});let o=r.facts.map((c,a)=>`${a+1}. ${c.question}`),l=["# Context Window Heist","",`Seed hash: ${r.seedHash}`,`Document length target: about ${r.targetTokens.toLocaleString("en-US")} tokens.`,"Instruction: answer using the latest fact when older and newer statements contradict each other.","","## Questions",o.join(`
`),"","## Haystack",u.join(`

`)].join(`
`);return{...r,questions:o,haystack:l}}var te,Xe,vo,ko,So,Ve,Ke=g(()=>{"use strict";te=Q(F(),1),Xe="q-context-window-heist-server",vo=4e3,ko=18e3,So=[{key:"q1",label:"active retrieval strategy",question:"What is the current active retrieval strategy?",stale:e=>`Earlier planning memo: the active retrieval strategy was ${e}. This line is stale.`,current:e=>`LATEST FACT [Q1]: The current active retrieval strategy is ${e}. Use this value.`,values:["sliding-window-v2","hybrid-rerank-v4","map-reduce-summaries","entity-anchor-scan"]},{key:"q2",label:"reranker model code",question:"What is the current reranker model code?",stale:e=>`Archive note: the reranker model code was ${e}. This has been superseded.`,current:e=>`LATEST FACT [Q2]: The reranker model code is ${e}. Use this value.`,values:["rrk-17b","rrk-29c","rrk-41d","rrk-53f"]},{key:"q3",label:"chunk overlap",question:"What is the current chunk overlap in tokens?",stale:e=>`Prototype setting: chunk overlap was ${e} tokens. This value is obsolete.`,current:e=>`LATEST FACT [Q3]: The chunk overlap is ${e} tokens. Use this value.`,values:["96","128","160","192"]},{key:"q4",label:"summary budget",question:"What is the current per-section summary budget in tokens?",stale:e=>`Old summarizer card: per-section summaries were capped at ${e} tokens. Do not use it.`,current:e=>`LATEST FACT [Q4]: The per-section summary budget is ${e} tokens. Use this value.`,values:["220","260","300","340"]},{key:"q5",label:"citation tag",question:"What is the current citation tag prefix?",stale:e=>`Legacy citation convention: evidence tags began with ${e}. It is no longer valid.`,current:e=>`LATEST FACT [Q5]: The citation tag prefix is ${e}. Use this value.`,values:["CTX","WIN","HEIST","ANCHOR"]},{key:"q6",label:"recency rule",question:"What is the current recency rule?",stale:e=>`Retired conflict policy: the recency rule was ${e}. Ignore this stale policy.`,current:e=>`LATEST FACT [Q6]: The recency rule is ${e}. Use this value.`,values:["latest-wins","timestamp-wins","revision-wins","suffix-wins"]},{key:"q7",label:"needle namespace",question:"What is the current needle namespace?",stale:e=>`Deprecated namespace registry: needles were stored under ${e}. This was replaced.`,current:e=>`LATEST FACT [Q7]: The needle namespace is ${e}. Use this value.`,values:["alpha-ledger","bravo-capsule","delta-vault","kappa-index"]},{key:"q8",label:"compression ratio",question:"What is the current target compression ratio?",stale:e=>`Old compression worksheet: target compression ratio was ${e}. Treat as stale.`,current:e=>`LATEST FACT [Q8]: The target compression ratio is ${e}. Use this value.`,values:["6:1","8:1","10:1","12:1"]},{key:"q9",label:"answer checksum",question:"What is the current answer checksum?",stale:e=>`Dry-run checksum: answer checksum was ${e}. The dry run has expired.`,current:e=>`LATEST FACT [Q9]: The answer checksum is ${e}. Use this value.`,values:["CWH-2149","CWH-3581","CWH-6927","CWH-8043"]},{key:"q10",label:"dispatch queue",question:"What is the current dispatch queue name?",stale:e=>`Previous queue bulletin: dispatch queue was ${e}. This bulletin is stale.`,current:e=>`LATEST FACT [Q10]: The dispatch queue name is ${e}. Use this value.`,values:["queue-indigo","queue-meridian","queue-pulsar","queue-topaz"]}],Ve=["chunk boundaries","metadata filters","retrieval traces","summary drift","sliding windows","prompt packing","recency conflicts","evidence ledgers","reranking scores","token accounting"]});var Ze={};k(Ze,{default:()=>Lo});import{html as Oo}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function Lo({user:e,weight:n=1,version:r=""}){let t="q-context-window-heist-server",d="Context Window Heist \u2014 Context Engineering",{haystack:u}=Ge(e.email,r),i=u.replace(/^Seed hash:.*\n/m,""),o=Oo`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:c,weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}}}var et=g(()=>{"use strict";Ke()});function ot(e){let n=2166136261;for(let r=0;r<e.length;r++)n^=e.charCodeAt(r),n=Math.imul(n,16777619);return(n>>>0).toString(16).padStart(8,"0")}function oe(e,n){return e[Math.floor(n()*e.length)]}function No(e,n){for(let r=e.length-1;r>0;r--){let t=Math.floor(n()*(r+1));[e[r],e[t]]=[e[t],e[r]]}return e}function nt(e,n=""){let t=`${String(e||"").trim().toLowerCase()}#${_o}#${n}`,d=(0,at.default)(t),u=`SPINCLI_${ot(t).toUpperCase()}`,i=[];for(let a=0;a<50;a++){let s=tt[Math.floor(d()*tt.length)],h=String(10+Math.floor(d()*18)).padStart(2,"0"),p=String(Math.floor(d()*24)).padStart(2,"0"),b=String(Math.floor(d()*60)).padStart(2,"0"),T=String(Math.floor(d()*60)).padStart(2,"0");i.push({id:`log-${String(a+1).padStart(3,"0")}`,ts:`2026-05-${h}T${p}:${b}:${T}Z`,region:oe(Eo,d),service:s.service,severity:oe(Co,d),message:oe(s.messages,d),label:s.label})}No(i,d);let o=i.map(({label:a,...s})=>s),l=o.map(a=>JSON.stringify(a)).join(`
`)+`
`,c=[...i].sort((a,s)=>a.id.localeCompare(s.id)).map(a=>JSON.stringify({id:a.id,label:a.label})).join(`
`)+`
`;return{seedHash:ot(t),marker:u,datasetRows:o,dataset:l,expectedOutput:c}}var at,_o,tt,Co,Eo,rt=g(()=>{"use strict";at=Q(F(),1),_o="q-spin-up-cli-server",tt=[{label:"auth_failure",service:"auth-gateway",messages:["password spray detected for tenant login","MFA challenge failed after repeated attempts","expired SSO token rejected during session refresh","impossible travel login blocked by policy"]},{label:"payment_error",service:"billing-api",messages:["card processor declined settlement batch","invoice webhook returned duplicate charge warning","refund queue stalled after gateway timeout","subscription renewal failed during payment capture"]},{label:"data_quality",service:"warehouse-loader",messages:["CSV ingest rejected rows with missing customer_id","schema drift detected nullable column mismatch","dedupe job found conflicting product keys","daily export contained invalid UTF-8 payload"]},{label:"deploy_event",service:"release-bot",messages:["canary deploy promoted after health check passed","feature flag rollout advanced to production cohort","container image pinned for blue green release","migration completed before service restart"]},{label:"support_noise",service:"helpdesk-sync",messages:["customer asked for invoice copy in chat","agent added internal note to resolved ticket","weekly satisfaction survey digest delivered","knowledge base article linked in reply"]}],Co=["debug","info","notice","warning","error"],Eo=["iad","bom","fra","syd","gru","sin"]});var st={};k(st,{default:()=>Mo});import{html as zo}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function Mo({user:e,weight:n=1,version:r=""}){let t="q-spin-up-cli-server",d="Spin Up the CLI \u2014 LLM CLI Tools",{marker:u,dataset:i}=nt(e.email,r),o=zo`
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
  `;return{id:t,title:d,weight:n,question:o,answer:async c=>{let a=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:c,weight:n,questionId:t,version:r})}),s=await a.json();if(!a.ok)throw new Error(s.error||"Verification failed.");return s}}}var it=g(()=>{"use strict";rt()});function Ro(e){let n=2166136261;for(let r=0;r<e.length;r++)n^=e.charCodeAt(r),n=Math.imul(n,16777619);return(n>>>0).toString(16).padStart(8,"0")}function lt(e,n){for(let r=e.length-1;r>0;r--){let t=Math.floor(n()*(r+1));[e[r],e[t]]=[e[t],e[r]]}return e}function ct(e){let n=[];for(let[r,t,d,u,i]of Po)n.push({domain:r,role:"target",text:d,query:t},{domain:r,role:"domain-distractor",text:`routine ${r} note was reviewed without a decision`,query:t},{domain:r,role:"negation-trap",text:u,query:t},{domain:r,role:"distractor",text:i,query:t});return lt(n,e),n.map((r,t)=>({...r,id:`p-${String(t+1).padStart(3,"0")}`}))}function dt(e,n=""){let t=`${String(e||"").trim().toLowerCase()}#${$o}#${n}`,d=(0,ae.default)(t),u=ct(d).map(({id:c,text:a})=>({id:c,text:a})),i=ct((0,ae.default)(`${t}#targets`)).filter(c=>c.role==="target"),o=new Map(u.map(c=>[c.text,c.id]));lt(i,d);let l=i.slice(0,Do).map((c,a)=>({id:`q${a+1}`,text:c.query,domain:c.domain,answer:o.get(c.text)}));return{seedHash:Ro(t),corpus:u,queries:l.map(({answer:c,...a})=>a),answers:Object.fromEntries(l.map(c=>[c.id,c.answer]))}}var ae,$o,Do,Po,ut=g(()=>{"use strict";ae=Q(F(),1),$o="q-embedding-trap-neighbors-server",Do=10,Po=[["medical","patient has low blood sugar","clinical note reports hypoglycemia","clinical note reports hyperglycemia","patient asked for parking validation"],["medical","doctor found a harmless tumor","pathology describes a benign neoplasm","pathology describes a malignant neoplasm","nurse changed the bed linens"],["medical","kidney function suddenly worsened","chart documents acute renal failure","chart documents renal recovery","cafeteria menu lists kidney beans"],["medical","airway tube was removed","respiratory note says the patient was extubated","respiratory note says the patient was intubated","technician removed a printer cable"],["medical","the medicine caused sleepiness","adverse effect recorded as somnolence","adverse effect recorded as insomnia","pharmacy shelf was reorganized"],["legal","court cancelled the previous judgment","appellate panel vacated the ruling","appellate panel affirmed the ruling","clerk replaced the courtroom microphone"],["legal","lawyer gave up the right to object","counsel waived the objection","counsel preserved the objection","counsel printed the trial calendar"],["legal","contract cannot be enforced","agreement is void and unenforceable","agreement is valid and enforceable","agreement uses blue ink signatures"],["legal","judge postponed the hearing","court granted a continuance","court denied a continuance","court opened a new filing window"],["legal","case was sent back to lower court","matter was remanded for further proceedings","matter was dismissed with prejudice","matter was indexed under a new docket"],["finance","loan payments stopped","account entered delinquency","account returned to good standing","account statement changed font size"],["finance","company can pay short term bills","firm has adequate liquidity","firm faces a liquidity crunch","firm renovated the lobby"],["finance","investment lost value","portfolio suffered a drawdown","portfolio reached a new high watermark","portfolio manager joined a webinar"],["finance","bank reversed the card charge","issuer processed a chargeback","issuer approved the charge","issuer mailed a replacement card"],["finance","auditor found revenue booked too early","report flags premature revenue recognition","report clears revenue recognition","report includes a new cover page"],["cloud","service can create more containers automatically","autoscaler increases pod replicas","autoscaler decreases pod replicas","cluster dashboard switched to dark mode"],["cloud","server stopped responding to health checks","instance failed liveness probes","instance passed liveness probes","instance label changed color"],["cloud","database copy is behind the primary","replica lag exceeded threshold","replica caught up with primary","replica name contains a hyphen"],["cloud","secret key was accidentally exposed","credential leakage was detected","credential rotation completed safely","credential file used Unix newlines"],["cloud","traffic was moved back to old release","deployment rolled back to previous version","deployment promoted new version","deployment notes mention canary birds"],["support","customer is angry about delay","ticket shows escalated frustration","ticket shows customer satisfaction","ticket includes a shipping address"],["support","agent solved the issue during first reply","case achieved first contact resolution","case required multiple follow ups","case was tagged with a green label"],["support","customer wants to stop using the service","account is at churn risk","account is likely to renew","account owner updated their avatar"],["support","reply promised money back","agent offered a refund","agent refused a refund","agent copied the help center URL"],["support","ticket should go to the security team","case requires security escalation","case requires billing escalation","case includes a screenshot attachment"],["logistics","package arrived later than planned","shipment missed its delivery SLA","shipment met its delivery SLA","shipment label printed in landscape mode"],["logistics","warehouse has no units left","inventory is out of stock","inventory is fully replenished","inventory sheet used comma separators"],["logistics","driver changed the route to avoid traffic","dispatcher rerouted the delivery","dispatcher kept the original route","dispatcher changed the radio volume"],["logistics","cold truck became too warm","refrigerated chain was breached","refrigerated chain remained intact","refrigerated truck was painted white"],["logistics","customs papers were missing","shipment lacked clearance documentation","shipment cleared customs","shipment was weighed on Tuesday"],["manufacturing","machine stopped because it overheated","equipment triggered thermal shutdown","equipment resumed normal temperature","equipment manual was spiral bound"],["manufacturing","batch failed quality checks","lot was rejected by QA","lot was approved by QA","lot number ended with seven"],["manufacturing","sensor reading jumped outside limits","telemetry showed an out-of-spec spike","telemetry stayed within specification","telemetry chart used thin gridlines"],["manufacturing","production line slowed down","throughput dropped below target","throughput exceeded target","throughput report used a pie chart"],["manufacturing","replacement part was installed before failure","preventive maintenance was completed","preventive maintenance was skipped","maintenance team ordered coffee"],["education","student turned in work after deadline","submission was late","submission was on time","submission used a PDF filename"],["education","exam answer copied from another student","response was flagged for plagiarism","response was cleared of plagiarism","response used a blue pen"],["education","learner mastered the prerequisite","student demonstrated prerequisite competency","student lacked prerequisite competency","student changed profile photo"],["education","teacher allowed extra time","instructor granted an extension","instructor denied an extension","instructor updated the seating chart"],["education","course registration is full","class has reached enrollment capacity","class has open seats","class meets on the third floor"],["insurance","claim should be paid","adjuster approved the claim","adjuster denied the claim","adjuster scanned the claim form"],["insurance","policy ended because bill was unpaid","coverage lapsed for nonpayment","coverage renewed after payment","coverage document used serif type"],["insurance","damage happened before coverage began","loss predates policy inception","loss occurred during active coverage","loss photo was taken outdoors"],["insurance","customer hid important facts","application contained material misrepresentation","application disclosed all material facts","application was signed electronically"],["insurance","insurer must not collect the deductible","deductible was waived","deductible was applied","deductible field appeared on page two"],["energy","grid has too much demand","load exceeded generation capacity","generation exceeded load","grid map used orange markers"],["energy","solar panel output fell suddenly","photovoltaic yield dropped","photovoltaic yield increased","solar panel frame was aluminum"],["energy","battery is almost empty","state of charge is critically low","state of charge is fully topped up","battery label included a QR code"],["energy","turbine was stopped for safety","wind unit entered protective shutdown","wind unit returned to service","wind unit cast a long shadow"],["energy","meter was reading too high","meter overreported consumption","meter underreported consumption","meter display used seven segments"]]});var ht={};k(ht,{default:()=>jo});import{html as Uo}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function jo({user:e,weight:n=1,version:r=""}){let t="q-embedding-trap-neighbors-server",d="Embedding Trapdoors \u2014 Nearest Neighbor Search",{queries:u,corpus:i}=dt(e.email,r),o=JSON.stringify({queries:u,corpus:i},null,2),l=Uo`
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
  `;return{id:t,title:d,weight:n,question:l,answer:async a=>{let s=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:e.email,quizSign:e.quizSign,response:a,weight:n,questionId:t,version:r})}),h=await s.json();if(!s.ok)throw new Error(h.error||"Verification failed.");return h}}}var pt=g(()=>{"use strict";ut()});import{html as R,render as xt}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function ne(e,n){let r=R`<ol class="mt-3">
    ${e.map(({id:u,title:i,weight:o})=>R`<li><a href="#h${u}">${i}</a> (${o} ${o==1?"mark":"marks"})</li>`)}
  </ol>`,t=[R`<h1 class="display-6">Questions</h1>`,r,...e.map(({id:u,title:i,weight:o,question:l,help:c},a)=>(c&&!Array.isArray(c)&&(c=[c]),R`
        <div class="card my-5" data-question="${u}" id="h${u}">
          <div class="card-header">
            <span class="badge text-bg-primary me-2">${a+1}</span>
            ${i} (${o} ${o==1?"mark":"marks"})
          </div>
          ${c?c.map(s=>R`<div class="card-body border-bottom">${s}</div>`):""}
          <div class="card-body">${l}</div>
          <div class="card-footer d-flex">
            <button type="button" class="btn btn-primary check-answer" data-question="${u}">Check</button>
          </div>
        </div>
      `))],d={index:r,questions:t};for(let[u,i]of n)xt(d[i],u)}import{unsafeHTML as vt}from"https://cdn.jsdelivr.net/npm/lit-html@3/directives/unsafe-html.js";import{Marked as kt}from"https://cdn.jsdelivr.net/npm/marked@13/+esm";var re="https://tds.s-anand.net",se=e=>e&&!e.match(/^(https?|mailto):/),St=new kt({renderer:{image(e,n,r){return se(e)&&(e=`${re}/${e}`),`<img src="${e}" alt="${r}" ${n?`title="${n}"`:""} class="img-fluid" loading="lazy">`},link(e,n,r){return se(e)&&(e=`${re}/${e.endsWith(".md")?`#/${e.replace(/\.md$/,"")}`:e}`),`<a href="${e}" ${n?`title="${n}"`:""} target="_blank">${r}</a>`}}}),v=e=>vt(St.parse(e));async function Ca(e,n){let r=[{...await Promise.resolve().then(()=>(ue(),de)).then(t=>t.default({user:e,weight:1})),help:[v(`
### Ask AI

- [How do I use yt-dlp to extract metadata for a YouTube video in JSON format without downloading it?](#askai)
- [What are the most common yt-dlp command-line options for fast metadata extraction?](#askai)
- [How do I write a Python script to filter a list of YouTube videos based on keyword inclusion and exclusion in their titles and descriptions?](#askai)
- [How do I sort a list of video objects by upload date (descending) and break ties using their video ID (ascending) in Python?](#askai)
- [How do I parse a JSON file containing YouTube metadata and filter videos by duration in Python?](#askai)
        `)]},{...await Promise.resolve().then(()=>(pe(),he)).then(t=>t.default({user:e,weight:1})),help:[v(`
### Ask AI

- [How do I decode a base64-encoded image in Python and pass it to a multimodal LLM like Gemini or GPT-5?](#askai)
- [How to use ollama gemm4:e2b locally with images using fastapi & use Cloudflare tunnel to serve publicly?](#askai)
- [How do I build a FastAPI endpoint that receives a base64 image and a question, then returns a JSON answer?](#askai)
- [What is the best multimodal model to use for extracting numbers from charts, receipts, and invoices?](#askai)
- [How do I enable CORS in a Python FastAPI app so that it accepts requests from any origin?](#askai)
- [How do I deploy a Python API to a public URL using Cloudflare Tunnel?](#askai)
        `)]},{...await Promise.resolve().then(()=>(fe(),me)).then(t=>t.default({user:e,weight:1})),help:[v(`
### Ask AI

- [How do I build a FastAPI endpoint that parses invoice text and extracts structured JSON fields?](#askai)
- [How do I use an LLM with structured output (JSON mode) to extract invoice fields reliably?](#askai)
- [How do I handle date parsing and convert date strings like "15 March 2026" to ISO format YYYY-MM-DD in Python?](#askai)
- [How do I distinguish subtotal, tax, and grand total in invoice text using regex or LLM prompting?](#askai)
- [How do I enable CORS in FastAPI so a Cloudflare Worker can call my endpoint?](#askai)
        `)]},{...await Promise.resolve().then(()=>(ge(),ye)).then(t=>t.default({user:e,weight:1})),help:[v(`
### Ask AI

- [How do I build a FastAPI endpoint that accepts a dynamic Pydantic schema at runtime and uses an LLM to extract matching fields?](#askai)
- [How do I prompt an LLM to return only the fields defined in a user-provided schema, with correct types?](#askai)
- [How do I validate that LLM output matches a dynamic JSON schema (correct keys, correct types, no extras)?](#askai)
- [How do I convert extracted string values to the correct Python types (int, float, bool, date) before returning?](#askai)
- [How do I make my FastAPI app return null for schema fields that couldn't be found in the text?](#askai)
        `)]},{...await Promise.resolve().then(()=>(ke(),ve)).then(t=>t.default({user:e,weight:1})),help:[v(`
### Ask AI

- [How do I load a JSON file with precomputed embeddings and compute cosine similarity using NumPy efficiently?](#askai)
- [How do I find the top-5 most similar documents for each query using numpy argsort?](#askai)
- [How do I implement the cosine similarity tie-breaking rule: if two documents have equal similarity, pick the one with the smaller doc_id?](#askai)
- [Why are precomputed unit-normalised embeddings useful \u2014 and why does cosine similarity reduce to a dot product for them?](#askai)
- [How do I vectorise the cosine similarity computation so it runs fast for 250 documents \xD7 10 queries?](#askai)
        `)]},{...await Promise.resolve().then(()=>(Ie(),Se)).then(t=>t.default({user:e,weight:1,version:"v1"})),help:[v(`
### Ask AI

- [How do I decode a base64 audio string in Python and save it as a WAV or MP3 file?](#askai)
- [How do I use the Whisper model to transcribe audio in Python?](#askai)
- [How do I build a FastAPI server that accepts a JSON body with base64-encoded audio and returns JSON statistics?](#askai)
- [How do I compute statistics (mean, std, variance, min, max, median, mode, range) on a pandas DataFrame in Python?](#askai)
- [How do I expose a local Python server to the internet using a tunnel (e.g. ngrok or cloudflared)?](#askai)
        `)]},{...await Promise.resolve().then(()=>(Te(),qe)).then(t=>t.default({user:e,weight:1,version:"v1"})),help:[v(`
### Ask AI

- [How do I get an LLM to return strict JSON matching a JSON Schema (structured output / function calling)?](#askai)
- [How do I build a FastAPI endpoint that calls an LLM and returns the parsed JSON?](#askai)
- [How do I convert amounts written in words or with K/M suffixes into plain integers?](#askai)
- [How do I normalize varied date formats to ISO 8601 (YYYY-MM-DD) in Python?](#askai)
- [How do I validate that an LLM's JSON output has exactly the expected keys before returning it?](#askai)
        `)]},{...await Promise.resolve().then(()=>(Oe(),Ae)).then(t=>t.default({user:e,weight:1,version:"v1"})),help:[v(`
### Ask AI

- [How do I call text-embedding-3-small to embed a list of strings in Python?](#askai)
- [How do I compute cosine similarity between embedding vectors with numpy?](#askai)
- [How do I rank a list of candidate texts against a query by similarity and return the top 3 indices?](#askai)
- [How do I build a FastAPI POST endpoint that accepts a query and a list of candidates and returns JSON?](#askai)
- [How do I batch embedding requests efficiently for many short texts?](#askai)
        `)]},{...await Promise.resolve().then(()=>(_e(),Le)).then(t=>t.default({user:e,weight:1,version:"v1"})),help:[v(`
### Ask AI

- [How do I prompt an LLM to solve a word problem step by step and return a final integer?](#askai)
- [How do I make an LLM return strict JSON with exactly the keys "reasoning" and "answer"?](#askai)
- [How do I ignore irrelevant distractor numbers when solving a math word problem?](#askai)
- [How do I validate that a JSON field is an integer (not a string or float) in Python?](#askai)
- [How do I build a FastAPI endpoint that solves a problem and returns {reasoning, answer}?](#askai)
        `)]},{...await Promise.resolve().then(()=>(Ee(),Ce)).then(t=>t.default({user:e,weight:1,version:"v1"})),help:[v(`
### Ask AI

- [How do I compute a SHA-256 hash of a string in Python with hashlib?](#askai)
- [How do I count the number of leading zero bits in a hash digest?](#askai)
- [How do I write a fast proof-of-work miner that searches for a nonce?](#askai)
- [How do I speed up a brute-force hashing loop with multiprocessing in Python?](#askai)
- [What does "leading zero bits" mean for a SHA-256 digest and how hard is it to find?](#askai)
        `)]},{...await Promise.resolve().then(()=>(et(),Ze)).then(t=>t.default({user:e,weight:1,version:"v1"})),help:[v(`
### Ask AI

- [How do I chunk a long Markdown document for retrieval when a model has a 4k context window?](#askai)
- [How do I build a lightweight reranker that finds the latest statement when a document contains stale contradictory facts?](#askai)
- [How do I track context tokens sent to an LLM for each query in Python?](#askai)
- [How do I use sliding windows plus keyword search to answer questions from a long document efficiently?](#askai)
- [How do I make an LLM answer from retrieved evidence only and return strict JSON?](#askai)
        `)]},{...await Promise.resolve().then(()=>(it(),st)).then(t=>t.default({user:e,weight:1,version:"v1"})),help:[v(`
### Ask AI

- [How do I use Simon Willison's llm CLI in a Unix pipeline to classify JSONL records?](#askai)
- [How do I use jq to convert JSONL logs into compact prompts for an LLM command-line tool?](#askai)
- [How do I normalize LLM classification output back into sorted JSONL with id and label fields?](#askai)
- [How do I record a terminal session with asciinema and save the .cast file?](#askai)
- [How do I compute SHA-256 for a file using sha256sum or shasum on macOS/Linux?](#askai)
        `)]},{...await Promise.resolve().then(()=>(pt(),ht)).then(t=>t.default({user:e,weight:1,version:"v1"})),help:[v(`
### Ask AI

- [How do I embed a JSON corpus and query list, then find the nearest neighbor by cosine similarity in Python?](#askai)
- [How do I avoid lexical-overlap traps when building semantic search with embeddings?](#askai)
- [How do I use sentence-transformers or OpenAI embeddings to rank short phrases by meaning?](#askai)
- [How do I normalize embedding vectors and compute cosine similarity with NumPy?](#askai)
- [How do I return a JSON object mapping query IDs to nearest corpus IDs?](#askai)
        `)]}];return ne(r,n),Object.fromEntries(r.map(({id:t,...d})=>[t,d]))}export{Ca as questions};
