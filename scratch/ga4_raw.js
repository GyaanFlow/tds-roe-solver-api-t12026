var tn=Object.create;var de=Object.defineProperty;var nn=Object.getOwnPropertyDescriptor;var on=Object.getOwnPropertyNames;var rn=Object.getPrototypeOf,an=Object.prototype.hasOwnProperty;var A=(n,o)=>()=>(n&&(o=n(n=0)),o);var E=(n,o)=>()=>(o||n((o={exports:{}}).exports,o),o.exports),I=(n,o)=>{for(var i in o)de(n,i,{get:o[i],enumerable:!0})},sn=(n,o,i,s)=>{if(o&&typeof o=="object"||typeof o=="function")for(let m of on(o))!an.call(n,m)&&m!==i&&de(n,m,{get:()=>o[m],enumerable:!(s=nn(o,m))||s.enumerable});return n};var R=(n,o,i)=>(i=n!=null?tn(rn(n)):{},sn(o||!n||!n.__esModule?de(i,"default",{value:n,enumerable:!0}):i,n));var Le=E((Me,he)=>{(function(n,o,i){function s(e){var r=this,c=l();r.next=function(){var t=2091639*r.s0+r.c*23283064365386963e-26;return r.s0=r.s1,r.s1=r.s2,r.s2=t-(r.c=t|0)},r.c=1,r.s0=c(" "),r.s1=c(" "),r.s2=c(" "),r.s0-=c(e),r.s0<0&&(r.s0+=1),r.s1-=c(e),r.s1<0&&(r.s1+=1),r.s2-=c(e),r.s2<0&&(r.s2+=1),c=null}function m(e,r){return r.c=e.c,r.s0=e.s0,r.s1=e.s1,r.s2=e.s2,r}function d(e,r){var c=new s(e),t=r&&r.state,a=c.next;return a.int32=function(){return c.next()*4294967296|0},a.double=function(){return a()+(a()*2097152|0)*11102230246251565e-32},a.quick=a,t&&(typeof t=="object"&&m(t,c),a.state=function(){return m(c,{})}),a}function l(){var e=4022871197,r=function(c){c=String(c);for(var t=0;t<c.length;t++){e+=c.charCodeAt(t);var a=.02519603282416938*e;e=a>>>0,a-=e,a*=e,e=a>>>0,a-=e,e+=a*4294967296}return(e>>>0)*23283064365386963e-26};return r}o&&o.exports?o.exports=d:i&&i.amd?i(function(){return d}):this.alea=d})(Me,typeof he=="object"&&he,typeof define=="function"&&define)});var Fe=E((Je,ue)=>{(function(n,o,i){function s(l){var e=this,r="";e.x=0,e.y=0,e.z=0,e.w=0,e.next=function(){var t=e.x^e.x<<11;return e.x=e.y,e.y=e.z,e.z=e.w,e.w^=e.w>>>19^t^t>>>8},l===(l|0)?e.x=l:r+=l;for(var c=0;c<r.length+64;c++)e.x^=r.charCodeAt(c)|0,e.next()}function m(l,e){return e.x=l.x,e.y=l.y,e.z=l.z,e.w=l.w,e}function d(l,e){var r=new s(l),c=e&&e.state,t=function(){return(r.next()>>>0)/4294967296};return t.double=function(){do var a=r.next()>>>11,h=(r.next()>>>0)/4294967296,u=(a+h)/(1<<21);while(u===0);return u},t.int32=r.next,t.quick=t,c&&(typeof c=="object"&&m(c,r),t.state=function(){return m(r,{})}),t}o&&o.exports?o.exports=d:i&&i.amd?i(function(){return d}):this.xor128=d})(Je,typeof ue=="object"&&ue,typeof define=="function"&&define)});var Pe=E((Be,me)=>{(function(n,o,i){function s(l){var e=this,r="";e.next=function(){var t=e.x^e.x>>>2;return e.x=e.y,e.y=e.z,e.z=e.w,e.w=e.v,(e.d=e.d+362437|0)+(e.v=e.v^e.v<<4^(t^t<<1))|0},e.x=0,e.y=0,e.z=0,e.w=0,e.v=0,l===(l|0)?e.x=l:r+=l;for(var c=0;c<r.length+64;c++)e.x^=r.charCodeAt(c)|0,c==r.length&&(e.d=e.x<<10^e.x>>>4),e.next()}function m(l,e){return e.x=l.x,e.y=l.y,e.z=l.z,e.w=l.w,e.v=l.v,e.d=l.d,e}function d(l,e){var r=new s(l),c=e&&e.state,t=function(){return(r.next()>>>0)/4294967296};return t.double=function(){do var a=r.next()>>>11,h=(r.next()>>>0)/4294967296,u=(a+h)/(1<<21);while(u===0);return u},t.int32=r.next,t.quick=t,c&&(typeof c=="object"&&m(c,r),t.state=function(){return m(r,{})}),t}o&&o.exports?o.exports=d:i&&i.amd?i(function(){return d}):this.xorwow=d})(Be,typeof me=="object"&&me,typeof define=="function"&&define)});var He=E((Ge,pe)=>{(function(n,o,i){function s(l){var e=this;e.next=function(){var c=e.x,t=e.i,a,h,u;return a=c[t],a^=a>>>7,h=a^a<<24,a=c[t+1&7],h^=a^a>>>10,a=c[t+3&7],h^=a^a>>>3,a=c[t+4&7],h^=a^a<<7,a=c[t+7&7],a=a^a<<13,h^=a^a<<9,c[t]=h,e.i=t+1&7,h};function r(c,t){var a,h,u=[];if(t===(t|0))h=u[0]=t;else for(t=""+t,a=0;a<t.length;++a)u[a&7]=u[a&7]<<15^t.charCodeAt(a)+u[a+1&7]<<13;for(;u.length<8;)u.push(0);for(a=0;a<8&&u[a]===0;++a);for(a==8?h=u[7]=-1:h=u[a],c.x=u,c.i=0,a=256;a>0;--a)c.next()}r(e,l)}function m(l,e){return e.x=l.x.slice(),e.i=l.i,e}function d(l,e){l==null&&(l=+new Date);var r=new s(l),c=e&&e.state,t=function(){return(r.next()>>>0)/4294967296};return t.double=function(){do var a=r.next()>>>11,h=(r.next()>>>0)/4294967296,u=(a+h)/(1<<21);while(u===0);return u},t.int32=r.next,t.quick=t,c&&(c.x&&m(c,r),t.state=function(){return m(r,{})}),t}o&&o.exports?o.exports=d:i&&i.amd?i(function(){return d}):this.xorshift7=d})(Ge,typeof pe=="object"&&pe,typeof define=="function"&&define)});var Ve=E((Ue,fe)=>{(function(n,o,i){function s(l){var e=this;e.next=function(){var c=e.w,t=e.X,a=e.i,h,u;return e.w=c=c+1640531527|0,u=t[a+34&127],h=t[a=a+1&127],u^=u<<13,h^=h<<17,u^=u>>>15,h^=h>>>12,u=t[a]=u^h,e.i=a,u+(c^c>>>16)|0};function r(c,t){var a,h,u,g,w,y=[],k=128;for(t===(t|0)?(h=t,t=null):(t=t+"\0",h=0,k=Math.max(k,t.length)),u=0,g=-32;g<k;++g)t&&(h^=t.charCodeAt((g+32)%t.length)),g===0&&(w=h),h^=h<<10,h^=h>>>15,h^=h<<4,h^=h>>>13,g>=0&&(w=w+1640531527|0,a=y[g&127]^=h+w,u=a==0?u+1:0);for(u>=128&&(y[(t&&t.length||0)&127]=-1),u=127,g=512;g>0;--g)h=y[u+34&127],a=y[u=u+1&127],h^=h<<13,a^=a<<17,h^=h>>>15,a^=a>>>12,y[u]=h^a;c.w=w,c.X=y,c.i=u}r(e,l)}function m(l,e){return e.i=l.i,e.w=l.w,e.X=l.X.slice(),e}function d(l,e){l==null&&(l=+new Date);var r=new s(l),c=e&&e.state,t=function(){return(r.next()>>>0)/4294967296};return t.double=function(){do var a=r.next()>>>11,h=(r.next()>>>0)/4294967296,u=(a+h)/(1<<21);while(u===0);return u},t.int32=r.next,t.quick=t,c&&(c.X&&m(c,r),t.state=function(){return m(r,{})}),t}o&&o.exports?o.exports=d:i&&i.amd?i(function(){return d}):this.xor4096=d})(Ue,typeof fe=="object"&&fe,typeof define=="function"&&define)});var We=E((Qe,ge)=>{(function(n,o,i){function s(l){var e=this,r="";e.next=function(){var t=e.b,a=e.c,h=e.d,u=e.a;return t=t<<25^t>>>7^a,a=a-h|0,h=h<<24^h>>>8^u,u=u-t|0,e.b=t=t<<20^t>>>12^a,e.c=a=a-h|0,e.d=h<<16^a>>>16^u,e.a=u-t|0},e.a=0,e.b=0,e.c=-1640531527,e.d=1367130551,l===Math.floor(l)?(e.a=l/4294967296|0,e.b=l|0):r+=l;for(var c=0;c<r.length+20;c++)e.b^=r.charCodeAt(c)|0,e.next()}function m(l,e){return e.a=l.a,e.b=l.b,e.c=l.c,e.d=l.d,e}function d(l,e){var r=new s(l),c=e&&e.state,t=function(){return(r.next()>>>0)/4294967296};return t.double=function(){do var a=r.next()>>>11,h=(r.next()>>>0)/4294967296,u=(a+h)/(1<<21);while(u===0);return u},t.int32=r.next,t.quick=t,c&&(typeof c=="object"&&m(c,r),t.state=function(){return m(r,{})}),t}o&&o.exports?o.exports=d:i&&i.amd?i(function(){return d}):this.tychei=d})(Qe,typeof ge=="object"&&ge,typeof define=="function"&&define)});var Ye=E(()=>{});var Ze=E((Xe,K)=>{(function(n,o,i){var s=256,m=6,d=52,l="random",e=i.pow(s,m),r=i.pow(2,d),c=r*2,t=s-1,a;function h(f,p,x){var v=[];p=p==!0?{entropy:!0}:p||{};var _=y(w(p.entropy?[f,b(o)]:f??k(),3),v),S=new u(v),$=function(){for(var C=S.g(m),N=e,D=0;C<r;)C=(C+D)*s,N*=s,D=S.g(1);for(;C>=c;)C/=2,N/=2,D>>>=1;return(C+D)/N};return $.int32=function(){return S.g(4)|0},$.quick=function(){return S.g(4)/4294967296},$.double=$,y(b(S.S),o),(p.pass||x||function(C,N,D,T){return T&&(T.S&&g(T,S),C.state=function(){return g(S,{})}),D?(i[l]=C,N):C})($,_,"global"in p?p.global:this==i,p.state)}function u(f){var p,x=f.length,v=this,_=0,S=v.i=v.j=0,$=v.S=[];for(x||(f=[x++]);_<s;)$[_]=_++;for(_=0;_<s;_++)$[_]=$[S=t&S+f[_%x]+(p=$[_])],$[S]=p;(v.g=function(C){for(var N,D=0,T=v.i,Z=v.j,J=v.S;C--;)N=J[T=t&T+1],D=D*s+J[t&(J[T]=J[Z=t&Z+N])+(J[Z]=N)];return v.i=T,v.j=Z,D})(s)}function g(f,p){return p.i=f.i,p.j=f.j,p.S=f.S.slice(),p}function w(f,p){var x=[],v=typeof f,_;if(p&&v=="object")for(_ in f)try{x.push(w(f[_],p-1))}catch{}return x.length?x:v=="string"?f:f+"\0"}function y(f,p){for(var x=f+"",v,_=0;_<x.length;)p[t&_]=t&(v^=p[t&_]*19)+x.charCodeAt(_++);return b(p)}function k(){try{var f;return a&&(f=a.randomBytes)?f=f(s):(f=new Uint8Array(s),(n.crypto||n.msCrypto).getRandomValues(f)),b(f)}catch{var p=n.navigator,x=p&&p.plugins;return[+new Date,n,x,n.screen,b(o)]}}function b(f){return String.fromCharCode.apply(0,f)}if(y(i.random(),o),typeof K=="object"&&K.exports){K.exports=h;try{a=Ye()}catch{}}else typeof define=="function"&&define.amd?define(function(){return h}):i["seed"+l]=h})(typeof self<"u"?self:Xe,[],Math)});var O=E((Xo,Ke)=>{var un=Le(),mn=Fe(),pn=Pe(),fn=He(),gn=Ve(),yn=We(),z=Ze();z.alea=un;z.xor128=mn;z.xorwow=pn;z.xorshift7=fn;z.xor4096=gn;z.tychei=yn;Ke.exports=z});var et={};I(et,{default:()=>_n});import bn from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as wn}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function vn(n,o){let i=[...n];for(let s=i.length-1;s>0;s--){let m=Math.floor(o()*(s+1));[i[s],i[m]]=[i[m],i[s]]}return i}function kn(n){let o=String(n||"").trim().toLowerCase(),i=(0,ee.default)(`${ye}#${o}#q-rag-chunking-hybrid-search#data`),s=o.split("").reduce((b,f)=>Math.imul(31,b)+f.charCodeAt(0)|0,0),m=Math.abs(s)%97,d=vn(xn,i),l=[];for(let b=0;b<64;b++){let f=d[b%d.length],p=`DOC_${b+1}`,x=m+b,v=`# ${f.title} (Rev ${b+1}-${m})

`;f.sections.forEach(_=>{v+=`## ${_.header}

`,_.paragraphs.forEach(S=>{let $=S.replace("fifteen percent",`${x%20+8} percent`).replace("two hundred meters",`${x*3%150+100} meters`).replace("twenty percent",`${x%15+10}%`).replace("ninety-five cycles",`${x%15+80} cycles`).replace("five units",`${x%7+2} units`).replace("twelve percent",`${x%10+8} percent`).replace("twenty-five minutes",`${x%20+15} minutes`).replace("ten seconds",`${x%8+5} seconds`);v+=`${$}

`})}),l.push({doc_id:p,title:`${f.title} (V${b+1})`,text:v.trim()})}let e="sentence",r=2+Math.floor(i()*2),c=1,h={strategy:e,chunk_size:r,overlap:c,rrf_k:60,top_k:5},u=[];l.forEach(b=>{let f=b.text.split(/[.!?]\s+/).map(p=>p.trim()).filter(p=>p.length>0);for(let p=0;p<f.length;p+=r-c){let x=f.slice(p,p+r);if(x.length===0||(u.push({chunk_id:`${b.doc_id}_CHUNK_${String(u.length).padStart(3,"0")}`,text:x.join(". ")+"."}),p+r>=f.length))break}});let g={};u.forEach(b=>{let f=[],p=(0,ee.default)(`${ye}#${o}#q1#chunk#${b.chunk_id}`);for(let x=0;x<100;x++)f.push(parseFloat((p()*2-1).toFixed(4)));g[b.chunk_id]=f});let w=[],y={},k=[{text:"How does V2I communication reduce fuel consumption?"},{text:"What happens when an autonomous vehicle departs from its corridor?"},{text:"At what battery charge level should electric vans schedule charging?"},{text:"How fast can DC fast chargers replenish battery capacity?"},{text:"What is the positioning accuracy of ASRS cranes?"},{text:"What triggers the automated quarantine workflow for RFID?"},{text:"When should maintenance be scheduled based on vibration analysis?"},{text:"What does forklift diagnostic code E102 indicate?"},{text:"What is the temperature excursion protocol for seafood?"},{text:"How do ethylene scrubbers affect banana ripening?"}];for(let b=0;b<80;b++){let f=k[b%k.length],p=`Q${String(b+1).padStart(3,"0")}`,x=`${f.text} (Ref: ${p})`;w.push({query_id:p,text:x});let v=[],_=(0,ee.default)(`${ye}#${o}#q1#query#${p}`);for(let S=0;S<100;S++)v.push(parseFloat((_()*2-1).toFixed(4)));y[p]=v}return{documents:l,chunk_rules:h,chunks:u,chunk_embeddings:g,queries:w,query_embeddings:y}}async function _n({user:n,weight:o=2}){let i="q-rag-chunking-hybrid-search-server",s="End-to-End Chunking & Hybrid Retrieval Pipeline",m=kn(n.email),{documents:d,chunk_rules:l,chunk_embeddings:e,queries:r,query_embeddings:c}=m,t=new bn;t.file("documents.jsonl",d.map(w=>JSON.stringify(w)).join(`
`)),t.file("chunk_rules.json",JSON.stringify(l,null,2)),t.file("chunk_embeddings.json",JSON.stringify(e,null,2)),t.file("queries.json",JSON.stringify(r,null,2)),t.file("query_embeddings.json",JSON.stringify(c,null,2)),t.file("README.txt",`LogiSearch Recruitment Challenge - Backend/AI Engineer Intern

Your task is to build a hybrid search pipeline.
Follow the rules specified in the exam interface.
`);let a=await t.generateAsync({type:"blob"}),h=URL.createObjectURL(a),u=wn`
    <div class="mb-4">
      <p class="lead">
        <strong>Scenario:</strong> You are interviewing for an AI Engineer internship at <strong>LogiSearch</strong>, 
        an enterprise search engine for logistics manuals. The team has asked you to implement and evaluate their 
        core hybrid retrieval pipeline.
      </p>

      <!-- SVG Pipeline Diagram -->
      <div class="text-center my-4 p-3 bg-light rounded border border-secondary-subtle">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 240" class="w-100" style="max-width: 650px;">
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#06b6d4;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#8b5cf6;stop-opacity:1" />
            </linearGradient>
            <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8" />
            </marker>
          </defs>
          
          <!-- Document Block -->
          <rect x="10" y="70" width="120" height="80" rx="8" fill="url(#grad1)" />
          <text x="70" y="115" fill="white" font-size="14" font-weight="bold" text-anchor="middle">Documents</text>
          
          <!-- Arrow 1 -->
          <path d="M130 110 L170 110" stroke="#94a3b8" stroke-width="3" fill="none" marker-end="url(#arrow)" />
          
          <!-- Chunking Block -->
          <rect x="170" y="70" width="110" height="80" rx="8" fill="#1e293b" />
          <text x="225" y="115" fill="white" font-size="14" font-weight="bold" text-anchor="middle">Chunking</text>
          
          <!-- Branching Arrows -->
          <path d="M280 110 L310 70 L340 70" stroke="#94a3b8" stroke-width="3" fill="none" />
          <path d="M280 110 L310 150 L340 150" stroke="#94a3b8" stroke-width="3" fill="none" />
          
          <!-- Sparse (BM25) Block -->
          <rect x="340" y="45" width="150" height="50" rx="6" fill="#0ea5e9" />
          <text x="415" y="75" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Sparse (BM25)</text>
          
          <!-- Dense (Cosine) Block -->
          <rect x="340" y="125" width="150" height="50" rx="6" fill="#10b981" />
          <text x="415" y="155" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Dense (Cosine Sim)</text>
          
          <!-- Converging Arrows -->
          <path d="M490 70 L520 70 L540 110" stroke="#94a3b8" stroke-width="3" fill="none" />
          <path d="M490 150 L520 150 L540 110" stroke="#94a3b8" stroke-width="3" fill="none" />
          
          <!-- RRF Fusion Block -->
          <rect x="540" y="85" width="110" height="50" rx="6" fill="url(#grad2)" />
          <text x="595" y="115" fill="white" font-size="13" font-weight="bold" text-anchor="middle">RRF Fusion</text>
          
          <!-- Arrow to Output -->
          <path d="M650 110 L680 110" stroke="#94a3b8" stroke-width="3" fill="none" />
          
          <!-- Output Block -->
          <rect x="680" y="70" width="110" height="80" rx="8" fill="#f43f5e" />
          <text x="735" y="115" fill="white" font-size="14" font-weight="bold" text-anchor="middle">Top-K Chunks</text>
        </svg>
      </div>

      <p><strong>Your Task:</strong></p>
      <ol>
        <li>Download the student-specific dataset zip containing:
          <ul>
            <li><code>documents.jsonl</code>: 64 documents with full text.</li>
            <li><code>chunk_rules.json</code>: Contains chunking parameters (strategy, size, overlap, rrf_k, top_k).</li>
            <li><code>chunk_embeddings.json</code>: Pre-computed 100-dim vectors for each chunk.</li>
            <li><code>queries.json</code>: 80 test queries.</li>
            <li><code>query_embeddings.json</code>: Pre-computed 100-dim vectors for each query.</li>
          </ul>
        </li>
        <li>Split the documents into chunks using the specified <strong>sentence chunking</strong> strategy in <code>chunk_rules.json</code>. A chunk consists of <code>chunk_size</code> sentences, with <code>overlap</code> sentences of overlap. Split sentences using: <code>text.split(/[.!?]\\s+/)</code>.</li>
        <li>For each query, compute the **BM25 score** and **Cosine Similarity** across all chunks.</li>
        <li>Fuse the sparse and dense ranks using **Reciprocal Rank Fusion (RRF)**:
          <pre><code>Score(d) = 1 / (rrf_k + Rank_sparse(d)) + 1 / (rrf_k + Rank_dense(d))</code></pre>
          *(Note: Rank is 1-indexed. If a document is not in the top rankings, ignore or treat it as having rank infinity).*
        </li>
        <li>Return the top <code>top_k</code> chunk IDs for each query. Tie-break by lexicographically smaller chunk ID.</li>
      </ol>

      <div class="my-3">
        <a href="${h}" download="rag_search_pipeline.zip" class="btn btn-primary">
          📥 Download RAG Pipeline Data (ZIP)
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit your ranked chunk IDs (JSON format)</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "Q001": ["DOC_1_CHUNK_000", "DOC_2_CHUNK_003", "..."],\n  "Q002": ["..."]\n}'
          required
        ></textarea>
        <div class="form-text">
          Submit the exact JSON dictionary mapping each query ID to a list of its top 5 chunk IDs in order.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:u,answer:async w=>{let y;try{y=JSON.parse(w)}catch{throw new Error("Invalid JSON format. Please check your syntax.")}let k=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:y,weight:o,questionId:i})}),b=await k.json();if(!k.ok)throw new Error(b.error||"Validation failed.");return b}}}var ee,ye,xn,tt=A(()=>{"use strict";ee=R(O(),1),ye="tds-ga4-q1-data-484877bff41818b2ff1c545a889b81a3a7f9cd8ce89d9d02",xn=[{title:"Autonomous Fleet Routing and Dispatch",sections:[{header:"Dynamic Route Optimization",paragraphs:["Autonomous dispatch systems utilize real-time traffic feeds and weather alerts to recalculate optimal paths. By analyzing congestion patterns, the fleet manager can redirect vehicles to alternative corridors.","Vehicle-to-Infrastructure (V2I) communication allows trucks to receive signal phase and timing data. This minimizes idle time at intersections and reduces fuel consumption by up to fifteen percent.","Route deviation alerts are triggered when an autonomous vehicle departs from its pre-planned corridor by more than two hundred meters. Emergency halting is initiated if telemetry connection is lost for ten seconds."]},{header:"Battery and Charging Management",paragraphs:["Electric delivery vans must schedule charging stops when battery state of charge drops below twenty percent. Smart grid integration ensures vehicles charge during off-peak hours to minimize operational costs.","High-power DC fast chargers can replenish battery capacity from ten to eighty percent in twenty-five minutes. Frequent fast charging, however, accelerates battery degradation by twelve percent annually.","Thermal management systems regulate battery temperature during charging cycles. Optimal performance is maintained between twenty and thirty-five degrees Celsius."]}]},{title:"Automated Warehouse Inventory Control",sections:[{header:"ASRS Integration and Throughput",paragraphs:["Automated Storage and Retrieval Systems (ASRS) optimize vertical warehouse space. High-speed cranes retrieve pallets from double-deep racking systems with a positioning accuracy of two millimeters.","System throughput is measured in dual-cycles per hour, representing simultaneous storage and retrieval operations. The target efficiency is ninety-five cycles per hour under peak loads.","Safety light curtains are installed at all ASRS entry points. Any beam interruption immediately cuts power to the drive motors within fifty milliseconds."]},{header:"RFID Tracking and Discrepancy Resolution",paragraphs:["RFID portals at dock doors scan incoming pallets automatically. The system compares scanned item counts against the digital shipping manifest in real-time.","Discrepancies exceeding five units trigger an automated quarantine workflow. Warehouse staff are notified via handheld terminals to perform a manual count within fifteen minutes.","Metal-mount RFID tags are required for all liquid containers and metallic parts. Standard paper tags suffer from signal attenuation when placed directly on conductive surfaces."]}]},{title:"Predictive Maintenance for Logistics Assets",sections:[{header:"Vibration Analysis on Conveyor Belts",paragraphs:["Accelerometers mounted on conveyor drive shafts monitor vibration frequencies. An increase in the acceleration envelope indicates bearing wear or misalignment.","Spectral analysis identifies outer race defects when frequency peaks match calculated bearing frequencies. Maintenance should be scheduled when amplitude exceeds 0.5 inches per second.","Belt tension is monitored via load cells. Automatic tensioning systems adjust belt slack to maintain a constant tension of four hundred Newtons."]},{header:"Forklift Telemetry and Diagnostic Codes",paragraphs:["On-board diagnostics track forklift operating parameters including hydraulic pressure and motor temperature. Code E102 indicates hydraulic fluid temperature exceeding ninety degrees Celsius.","Forklifts must undergo safety inspections every two hundred operating hours. The system automatically restricts maximum travel speed to three kilometers per hour if inspection is overdue.","Regenerative braking systems recover energy during deceleration. This increases overall battery runtime by eight percent per shift."]}]},{title:"Cold Chain Monitoring and Quality Assurance",sections:[{header:"Temperature Excursion Protocols",paragraphs:["Refrigerated trailers must maintain a constant temperature of minus twenty degrees Celsius for frozen seafood. Temperature sensors log readings every five minutes.","A temperature excursion occurs when the temperature rises above minus fifteen degrees Celsius for more than thirty consecutive minutes. This triggers an audible alarm and SMS notification.","Dry ice sublimation rates are calculated based on external temperature. Standard insulated shippers require two kilograms of dry ice per twenty-four hours of transit."]},{header:"Ethylene Gas and Ripening Control",paragraphs:["Ethylene scrubbers in banana ripening rooms regulate gas concentrations. Maintaining ethylene levels below 0.1 parts per million prevents premature ripening during transport.","Controlled atmosphere containers adjust oxygen and carbon dioxide levels. Reducing oxygen to three percent extends the shelf life of green produce by two weeks.","Relative humidity must be maintained at ninety percent to prevent moisture loss and shriveling. Dehumidification cycles are initiated if humidity exceeds ninety-five percent."]}]}]});var it={};I(it,{default:()=>An});import Sn from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as qn}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function $n(n){let o=String(n||"").trim().toLowerCase(),i=(0,be.default)(`${nt}#${o}#q-rag-evaluation-harness#data`),s=[],m=[],d={},l={};for(let e=0;e<96;e++){let r=`T${String(e+1).padStart(3,"0")}`,c=ot[e%ot.length],t=` (ID: ${r})`,a=c.question.replace("?","")+t+"?",h=c.reference+t,u=c.chunks.map(p=>({chunk_id:p.chunk_id,text:p.text+t})),g=Math.floor(i()*3),w="";g===0?w=c.reference+t:g===1?w=c.chunks[0].text+". However, "+c.chunks[2].text+t:w="The system operates using blockchain technology and quantum computing."+t,s.push({trace_id:r,question:a,retrieved_chunks:u,generated_answer:w}),m.push({trace_id:r,reference_answer:h,relevant_chunk_ids:c.correct_chunks});let y=[],k=[],b=(0,be.default)(`${nt}#${o}#q2#embed#${r}`),f=g===2?.3:.85;for(let p=0;p<50;p++){let x=b()*2-1;y.push(parseFloat(x.toFixed(4)));let v=(b()*2-1)*(1-f);k.push(parseFloat((x*f+v).toFixed(4)))}d[r]=y,l[r]=k}return{traces:s,ground_truth:m,question_embeddings:d,answer_embeddings:l}}async function An({user:n,weight:o=2}){let i="q-rag-evaluation-harness-server",s="RAG Evaluation Harness (RAGAS-style Metrics)",m=$n(n.email),{traces:d,ground_truth:l,question_embeddings:e,answer_embeddings:r}=m,c=new Sn;c.file("traces.jsonl",d.map(g=>JSON.stringify(g)).join(`
`)),c.file("ground_truth.jsonl",l.map(g=>JSON.stringify(g)).join(`
`)),c.file("question_embeddings.json",JSON.stringify(e,null,2)),c.file("answer_embeddings.json",JSON.stringify(r,null,2)),c.file("README.txt",`RAG Evaluation Challenge - QA Engineer / AI Engineer Intern

Your task is to calculate RAGAS-style metrics for the provided traces.
Follow the exact formulas specified in the exam interface.
`);let t=await c.generateAsync({type:"blob"}),a=URL.createObjectURL(t),h=qn`
    <div class="mb-4">
      <p class="lead">
        <strong>Scenario:</strong> You are an AI Platform Engineer at <strong>EvalAI</strong>. The product team needs 
        to evaluate a newly deployed RAG application. Your task is to build an offline evaluation harness that calculates 
        four key RAGAS-style quality metrics.
      </p>

      <!-- SVG Evaluation Diagram -->
      <div class="text-center my-4 p-3 bg-light rounded border border-secondary-subtle">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 240" class="w-100" style="max-width: 650px;">
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#2563eb;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
            </linearGradient>
          </defs>

          <!-- Input Blocks -->
          <rect x="10" y="20" width="160" height="40" rx="6" fill="url(#grad1)" />
          <text x="90" y="45" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Question</text>

          <rect x="10" y="100" width="160" height="40" rx="6" fill="url(#grad1)" />
          <text x="90" y="125" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Retrieved Context</text>

          <rect x="10" y="180" width="160" height="40" rx="6" fill="url(#grad1)" />
          <text x="90" y="205" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Generated Answer</text>

          <!-- Evaluator Block -->
          <rect x="270" y="80" width="160" height="80" rx="8" fill="#1e293b" />
          <text x="350" y="125" fill="white" font-size="15" font-weight="bold" text-anchor="middle">Eval Harness</text>

          <!-- Connecting lines -->
          <path d="M170 40 L220 40 L270 100" stroke="#94a3b8" stroke-width="2" fill="none" />
          <path d="M170 120 L270 120" stroke="#94a3b8" stroke-width="2" fill="none" />
          <path d="M170 200 L220 200 L270 140" stroke="#94a3b8" stroke-width="2" fill="none" />

          <!-- Output Metrics -->
          <path d="M430 120 L480 120" stroke="#94a3b8" stroke-width="3" fill="none" />

          <rect x="480" y="20" width="180" height="40" rx="6" fill="url(#grad2)" />
          <text x="570" y="45" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Faithfulness</text>

          <rect x="480" y="70" width="180" height="40" rx="6" fill="url(#grad2)" />
          <text x="570" y="95" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Answer Relevance</text>

          <rect x="480" y="120" width="180" height="40" rx="6" fill="url(#grad2)" />
          <text x="570" y="145" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Context Recall</text>

          <rect x="480" y="170" width="180" height="40" rx="6" fill="url(#grad2)" />
          <text x="570" y="195" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Context Precision</text>
        </svg>
      </div>

      <p><strong>Your Task:</strong></p>
      <p>Compute the following four metrics for each of the 96 traces in the dataset:</p>
      
      <div class="table-responsive">
        <table class="table table-bordered table-striped">
          <thead>
            <tr>
              <th>Metric</th>
              <th>Calculation Method</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>Faithfulness</strong></td>
              <td>
                1. Split the <code>generated_answer</code> into sentences (split on <code>[.!?]\\s+</code>, ignoring sentences &le; 5 characters).<br>
                2. For each sentence, tokenize it and find the maximum token overlap with any individual chunk in <code>retrieved_chunks</code>.<br>
                3. A sentence is <em>faithful</em> if the maximum token overlap is &ge; 0.5.<br>
                4. Faithfulness = (Number of faithful sentences) / (Total sentences in generated answer).
              </td>
            </tr>
            <tr>
              <td><strong>Answer Relevance</strong></td>
              <td>
                Compute the cosine similarity between the <code>question_embedding</code> and the <code>answer_embedding</code> using the provided 50-dimensional vectors.
              </td>
            </tr>
            <tr>
              <td><strong>Context Recall</strong></td>
              <td>
                1. Split the <code>reference_answer</code> into sentences (split on <code>[.!?]\\s+</code>, ignoring sentences &le; 5 characters).<br>
                2. For each sentence, compute its token overlap with the <em>concatenated text</em> of all <code>retrieved_chunks</code>.<br>
                3. A sentence is <em>recalled</em> if the overlap is &ge; 0.5.<br>
                4. Context Recall = (Number of recalled sentences) / (Total sentences in reference answer).
              </td>
            </tr>
            <tr>
              <td><strong>Context Precision</strong></td>
              <td>
                <code>CP = (&Sigma; (Precision@i &times; rel_i)) / Total Relevant</code><br>
                Where:<br>
                - <code>i</code> is the 0-based index of the retrieved chunk.<br>
                - <code>Precision@i</code> = (Number of relevant chunks in positions 0 to i) / (i + 1).<br>
                - <code>rel_i</code> = 1 if the chunk's ID is in <code>relevant_chunk_ids</code>, else 0.<br>
                - <code>Total Relevant</code> is the length of <code>relevant_chunk_ids</code>. If 0, precision is 0.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p><strong>Token Overlap Formula:</strong></p>
      <pre><code>overlap(A, B) = |tokens(A) ∩ tokens(B)| / |tokens(A)|</code></pre>
      <p>Tokenize by converting to lowercase and matching words: <code>text.toLowerCase().match(/\\b[a-z0-9]+\\b/g) || []</code>.</p>

      <div class="my-3">
        <a href="${a}" download="rag_evaluation_data.zip" class="btn btn-primary">
          📥 Download Eval Harness Data (ZIP)
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit your calculated metrics (JSON format)</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "T001": {\n    "faithfulness": 1.00,\n    "answer_relevance": 0.92,\n    "context_recall": 0.85,\n    "context_precision": 0.75\n  },\n  "T002": ...\n}'
          required
        ></textarea>
        <div class="form-text">
          Submit the exact JSON dictionary mapping each trace ID to its four calculated metrics. Round all floats to exactly 2 decimal places.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:h,answer:async g=>{let w;try{w=JSON.parse(g)}catch{throw new Error("Invalid JSON format. Please check your syntax.")}let y=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:w,weight:o,questionId:i})}),k=await y.json();if(!y.ok)throw new Error(k.error||"Validation failed.");return k}}}var be,nt,ot,rt=A(()=>{"use strict";be=R(O(),1),nt="tds-ga4-q2-data-f7adee089cc927803d18f5dd04b18879c5cf11a0a4e3b081",ot=[{question:"What is the primary benefit of using V2I communication in autonomous trucking?",reference:"V2I communication allows trucks to receive signal phase and timing data, which reduces idle time at intersections and cuts fuel consumption by fifteen percent.",chunks:[{chunk_id:"C1",text:"V2I communication allows trucks to receive signal phase and timing data."},{chunk_id:"C2",text:"By minimizing idle time at intersections, V2I reduces fuel consumption by fifteen percent."},{chunk_id:"C3",text:"Autonomous trucks use lidar and radar for obstacle detection."}],correct_chunks:["C1","C2"]},{question:"How does ASRS improve warehouse storage efficiency?",reference:"ASRS optimizes vertical warehouse space by using high-speed cranes to retrieve pallets from double-deep racking systems with two millimeter accuracy.",chunks:[{chunk_id:"C1",text:"ASRS optimizes vertical warehouse space using high-speed cranes."},{chunk_id:"C2",text:"Cranes retrieve pallets from double-deep racking systems with two millimeter accuracy."},{chunk_id:"C3",text:"Manual forklifts are still used for short distance transport."}],correct_chunks:["C1","C2"]},{question:"What is the protocol for temperature excursions in seafood cold chains?",reference:"A temperature excursion occurs when the temperature rises above minus fifteen degrees Celsius for over thirty minutes, triggering an audible alarm and SMS.",chunks:[{chunk_id:"C1",text:"Frozen seafood must be maintained at constant temperature of minus twenty degrees Celsius."},{chunk_id:"C2",text:"An excursion is triggered if temperature rises above minus fifteen degrees for over thirty minutes."},{chunk_id:"C3",text:"SMS and audible alarms are sent immediately upon excursion detection."}],correct_chunks:["C2","C3"]},{question:"How do ethylene scrubbers prevent premature ripening of bananas?",reference:"Ethylene scrubbers maintain ethylene levels below 0.1 parts per million in ripening rooms, preventing premature ripening during transit.",chunks:[{chunk_id:"C1",text:"Banana ripening is accelerated by ethylene gas concentrations."},{chunk_id:"C2",text:"Scrubbers maintain ethylene levels below 0.1 parts per million."},{chunk_id:"C3",text:"Relative humidity must be kept at ninety percent to prevent moisture loss."}],correct_chunks:["C2"]}]});var at={};I(at,{default:()=>Cn});import{html as In}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function Cn({user:n,weight:o=2}){let i="q-grounded-answer-api-server",s="Anti-Hallucination Grounded Answer API with Confidence",m=In`
    <div class="mb-4">
      <p class="lead">
        <strong>Scenario:</strong> You are a Senior AI Engineer at <strong>SafeAnswer AI</strong>. The company is building 
        a high-reliability RAG system for medical and legal compliance. Your task is to build a production-grade 
        <strong>Grounded QA API</strong> that answers questions strictly from provided context chunks, cites the source chunks, 
        and calculates a calibrated confidence score.
      </p>

      <!-- SVG Grounded QA Diagram -->
      <div class="text-center my-4 p-3 bg-light rounded border border-secondary-subtle">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 240" class="w-100" style="max-width: 650px;">
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#f59e0b;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#d97706;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#8b5cf6;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#6d28d9;stop-opacity:1" />
            </linearGradient>
          </defs>

          <!-- Input Blocks -->
          <rect x="10" y="45" width="160" height="50" rx="6" fill="url(#grad1)" />
          <text x="90" y="75" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Question</text>

          <rect x="10" y="145" width="160" height="50" rx="6" fill="url(#grad1)" />
          <text x="90" y="175" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Context Chunks</text>

          <!-- API Block -->
          <rect x="290" y="70" width="180" height="100" rx="8" fill="#1e293b" />
          <text x="380" y="115" fill="white" font-size="16" font-weight="bold" text-anchor="middle">Your API</text>
          <text x="380" y="140" fill="#94a3b8" font-size="11" text-anchor="middle">Grounded QA + Citations</text>

          <!-- Connecting lines -->
          <path d="M170 70 L230 70 L290 100" stroke="#94a3b8" stroke-width="2" fill="none" />
          <path d="M170 170 L230 170 L290 140" stroke="#94a3b8" stroke-width="2" fill="none" />

          <!-- Output Metrics -->
          <path d="M470 120 L530 120" stroke="#94a3b8" stroke-width="3" fill="none" />

          <rect x="530" y="30" width="240" height="40" rx="6" fill="url(#grad2)" />
          <text x="650" y="55" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Grounded Answer</text>

          <rect x="530" y="80" width="240" height="40" rx="6" fill="url(#grad2)" />
          <text x="650" y="105" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Citations (Chunk IDs)</text>

          <rect x="530" y="130" width="240" height="40" rx="6" fill="url(#grad2)" />
          <text x="650" y="155" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Confidence &amp; Answerability</text>
        </svg>
      </div>

      <p><strong>API Endpoint Specification:</strong></p>
      <p>Your API must expose a <code>POST</code> endpoint at the path you submit below. It will receive a list of context chunks and a question, and must return the grounded answer with citations.</p>

      <h6>Request Format (JSON):</h6>
      <pre><code>{
  "question": "What year was FAISS released?",
  "chunks": [
    {"chunk_id": "C1", "text": "FAISS was developed by Facebook AI Research and open-sourced in 2017."},
    {"chunk_id": "C2", "text": "Qdrant is a vector database written in Rust, released in 2021."},
    {"chunk_id": "C3", "text": "ChromaDB is an open-source embedding database."}
  ]
}</code></pre>

      <h6>Response Format (JSON):</h6>
      <pre><code>{
  "answer": "FAISS was open-sourced in 2017.",
  "citations": ["C1"],
  "confidence": 0.95,
  "answerable": true
}</code></pre>

      <p><strong>Rules your API must follow:</strong></p>
      <ol>
        <li>If the question **cannot be answered from the provided chunks**, the API must return:
          <ul>
            <li><code>"answerable": false</code></li>
            <li><code>"answer": "I don't know"</code> (exact case-insensitive match)</li>
            <li><code>"citations": []</code> (empty array)</li>
            <li><code>"confidence"</code> &le; 0.3</li>
          </ul>
        </li>
        <li>Your API must never use outside knowledge — only information present in the chunks.</li>
        <li>Citations must reference real provided chunk IDs only (e.g., <code>"C1"</code>). No hallucinated IDs.</li>
        <li>Ensure your API handles CORS, has response times under 5 seconds, and handles empty or malformed inputs gracefully.</li>
      </ol>

      <div class="alert alert-info">
        <strong>💡 Testing tip:</strong> You can deploy this using FastAPI / Flask / Express, and expose it using 
        <code>ngrok</code> or <code>localtunnel</code>. Provide the full public URL below.
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Enter your public API URL</strong></label>
        <input
          type="url"
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          placeholder="https://your-app.ngrok-free.app/grounded-answer"
          required
        />
        <div class="form-text">
          The server will send several test cases (both answerable and adversarial unanswerable questions) to verify your API's robustness.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:m,answer:async l=>{let e=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:{url:l,phase:"submit"},weight:o,questionId:i})}),r=await e.json();if(!e.ok)throw new Error(r.error||"Validation failed.");return r}}}var st=A(()=>{"use strict"});var dt={};I(dt,{default:()=>Nn});import On from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as Rn}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function Dn(n){let o=String(n||"").trim().toLowerCase(),i=(0,te.default)(`${we}#${o}#q-vector-search-rerank-api#data`),s=[],m={};for(let l=1;l<=500;l++){let e=`D${String(l).padStart(3,"0")}`,r=ct[Math.floor(i()*ct.length)],c=lt[Math.floor(i()*lt.length)],t=2020+Math.floor(i()*7);s.push({doc_id:e,title:`Document Title ${e} (${r})`,department:r,year:t,region:c,text:`This is the body text of document ${e} in department ${r} for region ${c} and year ${t}.`});let a=[],h=(0,te.default)(`${we}#${o}#q4#doc#${e}`);for(let u=0;u<100;u++)a.push(parseFloat((h()*2-1).toFixed(4)));m[e]=a}let d={};for(let l=1;l<=10;l++){let e=`Q${String(l).padStart(3,"0")}`,r={},c=(0,te.default)(`${we}#${o}#q4#query#${e}`);for(let t=1;t<=500;t++){let a=`D${String(t).padStart(3,"0")}`;r[a]=parseFloat(c().toFixed(4))}d[e]=r}return{documents:s,embeddings:m,reranker_scores:d}}async function Nn({user:n,weight:o=2}){let i="q-vector-search-rerank-api-server",s="Production Vector Search API with Re-ranking",m=Dn(n.email),{documents:d,embeddings:l,reranker_scores:e}=m,t=[["doc_id","title","department","year","region","text"].join(","),...d.map(y=>[y.doc_id,`"${y.title}"`,y.department,y.year,y.region,`"${y.text}"`].join(","))].join(`
`),a=new On;a.file("documents.csv",t),a.file("embeddings.json",JSON.stringify(l,null,2)),a.file("reranker_scores.json",JSON.stringify(e,null,2)),a.file("README.txt",`SearchTech Solutions - Two-Stage Retrieval System

Implement a production-grade vector search API with metadata filtering and re-ranking.
Follow the API spec in the exam portal.
`);let h=await a.generateAsync({type:"blob"}),u=URL.createObjectURL(h),g=Rn`
    <div class="mb-4">
      <p class="lead">
        <strong>Scenario:</strong> You are a Machine Learning Engineer at <strong>SearchTech Solutions</strong>. 
        Your team is building an enterprise search platform. To balance latency and accuracy, you must implement a 
        <strong>two-stage retrieval pipeline</strong>: first, retrieve candidate documents using vector similarity 
        with metadata filtering, then re-rank them using a pre-computed cross-encoder score table.
      </p>

      <!-- SVG 2-Stage Retrieval Diagram -->
      <div class="text-center my-4 p-3 bg-light rounded border border-secondary-subtle">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 240" class="w-100" style="max-width: 650px;">
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#10b981;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#059669;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#f43f5e;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#e11d48;stop-opacity:1" />
            </linearGradient>
          </defs>

          <!-- Input Blocks -->
          <rect x="10" y="30" width="160" height="40" rx="6" fill="#1e293b" />
          <text x="90" y="55" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Query Vector</text>

          <rect x="10" y="90" width="160" height="40" rx="6" fill="#1e293b" />
          <text x="90" y="115" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Metadata Filter</text>

          <rect x="10" y="150" width="160" height="60" rx="6" fill="#475569" />
          <text x="90" y="175" fill="white" font-size="12" font-weight="bold" text-anchor="middle">500 Documents</text>
          <text x="90" y="195" fill="#cbd5e1" font-size="10" text-anchor="middle">(CSV &amp; Embeddings)</text>

          <!-- Stage 1 Block -->
          <rect x="260" y="55" width="180" height="110" rx="8" fill="url(#grad1)" />
          <text x="350" y="95" fill="white" font-size="14" font-weight="bold" text-anchor="middle">Stage 1: Retrieval</text>
          <text x="350" y="120" fill="white" font-size="11" text-anchor="middle">Filter + Cosine Similarity</text>
          <text x="350" y="140" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Returns Top-K</text>

          <!-- Connecting lines -->
          <path d="M170 50 L210 50 L260 80" stroke="#94a3b8" stroke-width="2" fill="none" />
          <path d="M170 110 L260 110" stroke="#94a3b8" stroke-width="2" fill="none" />
          <path d="M170 180 L210 180 L260 140" stroke="#94a3b8" stroke-width="2" fill="none" />

          <!-- Stage 2 Block -->
          <path d="M440 110 L490 110" stroke="#94a3b8" stroke-width="3" fill="none" />

          <rect x="490" y="70" width="160" height="80" rx="8" fill="url(#grad2)" />
          <text x="570" y="105" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Stage 2: Re-ranking</text>
          <text x="570" y="130" fill="white" font-size="11" text-anchor="middle">Reranker Score Lookup</text>

          <!-- Output Block -->
          <path d="M650 110 L690 110" stroke="#94a3b8" stroke-width="3" fill="none" />

          <rect x="690" y="80" width="100" height="60" rx="8" fill="#3b82f6" />
          <text x="740" y="115" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Top-N Results</text>
        </svg>
      </div>

      <p><strong>Your Task:</strong></p>
      <ol>
        <li>Download the dataset containing <code>documents.csv</code>, <code>embeddings.json</code>, and <code>reranker_scores.json</code>.</li>
        <li>Implement a <code>POST /vector-search</code> endpoint that performs the following operations:
          <ul>
            <li><strong>Filter:</strong> Filter the documents in <code>documents.csv</code> based on the incoming metadata <code>filter</code>. Your API must support:
              <ul>
                <li>Exact match: <code>{"department": "finance"}</code></li>
                <li>Greater than or equal: <code>{"year": {"gte": 2023}}</code></li>
                <li>Less than or equal: <code>{"year": {"lte": 2025}}</code></li>
                <li>In list: <code>{"region": {"in": ["north_america", "europe"]}}</code></li>
              </ul>
            </li>
            <li><strong>Vector Similarity:</strong> Compute the Cosine Similarity between the incoming <code>query_vector</code> and the embeddings of the filtered documents. Retrieve the top <code>top_k</code> documents. Sort descending by similarity, tie-break by lexicographically smaller <code>doc_id</code>.</li>
            <li><strong>Re-ranking:</strong> Re-rank the retrieved top <code>top_k</code> documents using the lookup table <code>reranker_scores[query_id]</code>.</li>
            <li><strong>Output:</strong> Return the top <code>rerank_top_n</code> document IDs in re-ranked order. Sort descending by score, tie-break by lexicographically smaller <code>doc_id</code>.</li>
          </ul>
        </li>
      </ol>

      <p><strong>API Endpoint Specification:</strong></p>
      <h6>Request Format (JSON):</h6>
      <pre><code>{
  "query_id": "Q001",
  "query_vector": [0.12, -0.45, 0.87, ...],  // 100-dimensional vector
  "top_k": 10,
  "rerank_top_n": 3,
  "filter": {
    "department": "finance",
    "year": {"gte": 2023},
    "region": {"in": ["north_america", "europe"]}
  }
}</code></pre>

      <h6>Response Format (JSON):</h6>
      <pre><code>{
  "matches": ["D103", "D088", "D901"]
}</code></pre>

      <div class="my-3">
        <a href="${u}" download="vector_search_rerank_data.zip" class="btn btn-primary">
          📥 Download Vector Search Data (ZIP)
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Enter your public API URL</strong></label>
        <input
          type="url"
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          placeholder="https://your-app.ngrok-free.app/vector-search"
          required
        />
        <div class="form-text">
          The server will send 10 diverse test cases with complex filters and edge cases to verify your implementation.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:g,answer:async y=>{let k=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:{url:y,phase:"submit"},weight:o,questionId:i})}),b=await k.json();if(!k.ok)throw new Error(b.error||"Validation failed.");return b}}}var te,we,ct,lt,ht=A(()=>{"use strict";te=R(O(),1),we="tds-ga4-q4-data-74b0cb0ad988a5d60aa486353b85d4ff816446657b041c85",ct=["finance","engineering","marketing","sales","hr","legal"],lt=["north_america","europe","asia_pacific","latin_america"]});var ut={};I(ut,{default:()=>Tn});import{html as En}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";async function Tn({user:n,weight:o=2}){let i="q-graphrag-pipeline-api-server",s="GraphRAG Pipeline: Extract \u2192 Index \u2192 Query",m=En`
    <div class="mb-4">
      <p class="lead">
        <strong>Scenario:</strong> You are a Principal AI Architect at <strong>GraphMind Systems</strong>. 
        Your team is building a next-generation knowledge retrieval system. To answer complex, multi-hop queries 
        across unstructured documents, you must build a complete <strong>GraphRAG Pipeline</strong>. 
        This pipeline consists of three endpoints: entity/relationship extraction, multi-hop graph querying, and 
        community summarization.
      </p>

      <!-- SVG GraphRAG Diagram -->
      <div class="text-center my-4 p-3 bg-light rounded border border-secondary-subtle">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 240" class="w-100" style="max-width: 650px;">
          <defs>
            <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#06b6d4;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:1" />
            </linearGradient>
            <linearGradient id="grad2" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" style="stop-color:#ec4899;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#f43f5e;stop-opacity:1" />
            </linearGradient>
          </defs>

          <!-- Input Block -->
          <rect x="10" y="90" width="140" height="60" rx="8" fill="url(#grad1)" />
          <text x="80" y="125" fill="white" font-size="14" font-weight="bold" text-anchor="middle">Text Chunk</text>

          <!-- Arrow 1 -->
          <path d="M150 120 L200 120" stroke="#94a3b8" stroke-width="3" fill="none" />

          <!-- Extraction Block -->
          <rect x="200" y="70" width="160" height="100" rx="8" fill="#1e293b" />
          <text x="280" y="115" fill="white" font-size="13" font-weight="bold" text-anchor="middle">1. Extract Graph</text>
          <text x="280" y="140" fill="#94a3b8" font-size="10" text-anchor="middle">POST /extract-graph</text>

          <!-- Arrow 2 -->
          <path d="M360 120 L410 120" stroke="#94a3b8" stroke-width="3" fill="none" />

          <!-- Graph Query & Community Blocks -->
          <rect x="410" y="20" width="180" height="90" rx="8" fill="#1e293b" />
          <text x="500" y="60" fill="white" font-size="13" font-weight="bold" text-anchor="middle">2. Graph Query</text>
          <text x="500" y="85" fill="#94a3b8" font-size="10" text-anchor="middle">POST /graph-query</text>

          <rect x="410" y="130" width="180" height="90" rx="8" fill="#1e293b" />
          <text x="500" y="170" fill="white" font-size="13" font-weight="bold" text-anchor="middle">3. Community Summary</text>
          <text x="500" y="195" fill="#94a3b8" font-size="10" text-anchor="middle">POST /community-summary</text>

          <!-- Converging Arrows -->
          <path d="M590 65 L640 65 L660 110" stroke="#94a3b8" stroke-width="3" fill="none" />
          <path d="M590 175 L640 175 L660 130" stroke="#94a3b8" stroke-width="3" fill="none" />

          <!-- Output Block -->
          <rect x="660" y="80" width="130" height="80" rx="8" fill="url(#grad2)" />
          <text x="725" y="120" fill="white" font-size="14" font-weight="bold" text-anchor="middle">Multi-hop Answers</text>
          <text x="725" y="140" fill="white" font-size="11" text-anchor="middle">&amp; Summaries</text>
        </svg>
      </div>

      <p><strong>Your Task:</strong></p>
      <p>Deploy a web server exposing three endpoints. The grader will call them sequentially:</p>

      <div class="card mb-3">
        <div class="card-header bg-dark text-white font-monospace">1. POST /extract-graph</div>
        <div class="card-body">
          <p>Extract entities (Person, Organization, Product, Framework) and relationships (FOUNDED, DEVELOPED, INTEGRATED_INTO, HIRED, AUTHORED) from raw text.</p>
          <h6>Request:</h6>
          <pre><code>{"chunk_id": "C001", "text": "LangChain was created by Harrison Chase..."}</code></pre>
          <h6>Response:</h6>
          <pre><code>{
  "entities": [{"name": "LangChain", "type": "Framework"}, ...],
  "relationships": [{"source": "Harrison Chase", "target": "LangChain", "relation": "CREATED"}]
}</code></pre>
        </div>
      </div>

      <div class="card mb-3">
        <div class="card-header bg-dark text-white font-monospace">2. POST /graph-query</div>
        <div class="card-body">
          <p>Perform multi-hop reasoning over the provided knowledge graph to answer a natural language question.</p>
          <h6>Request:</h6>
          <pre><code>{
  "question": "Who created the framework that integrates with OpenAI?",
  "graph": { "entities": [...], "relationships": [...] }
}</code></pre>
          <h6>Response:</h6>
          <pre><code>{
  "answer": "Harrison Chase",
  "reasoning_path": ["OpenAI", "LangChain", "Harrison Chase"],
  "hops": 2
}</code></pre>
        </div>
      </div>

      <div class="card mb-3">
        <div class="card-header bg-dark text-white font-monospace">3. POST /community-summary</div>
        <div class="card-body">
          <p>Summarize the relationships and entities of a specific sub-community (connected component) in the graph.</p>
          <h6>Request:</h6>
          <pre><code>{
  "community_id": "COM_001",
  "entities": ["LangChain", "Harrison Chase", "OpenAI"],
  "relationships": [...]
}</code></pre>
          <h6>Response:</h6>
          <pre><code>{
  "community_id": "COM_001",
  "summary": "This community centers around LangChain, an AI framework created by Harrison Chase that integrates with OpenAI."
}</code></pre>
        </div>
      </div>

      <div class="alert alert-info">
        <strong>💡 Deploying your GraphRAG server:</strong> Provide the base URL of your deployed application below. 
        The grader will append the sub-paths (e.g., <code>/extract-graph</code>, <code>/graph-query</code>, <code>/community-summary</code>) 
        during evaluation.
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Enter your public GraphRAG Base URL</strong></label>
        <input
          type="url"
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          placeholder="https://your-app.ngrok-free.app"
          required
        />
        <div class="form-text">
          The grader will verify all 3 endpoints using 14 distinct, seeded multi-hop test cases.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:m,answer:async l=>{let e=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:{url:l,phase:"submit"},weight:o,questionId:i})}),r=await e.json();if(!e.ok)throw new Error(r.error||"Validation failed.");return r}}}var mt=A(()=>{"use strict"});var xt={};I(xt,{default:()=>Pn});import zn from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as jn}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function wt(n){return String(n||"").trim().toLowerCase()}function oe(n,o){return String(n).padStart(o,"0")}function Ln(n,o){return n[Math.floor(o()*n.length)]}function Jn(n){return wt(n).split("").reduce((o,i)=>Math.imul(o,33)+i.charCodeAt(0)>>>0,5381)}function Fn({service:n,region:o,release:i,heading:s,owner:m,priority:d,docIndex:l,sectionIndex:e,emailNumber:r}){let c=12+(r+l+e)%9,t=2+(r+l*3+e)%7,a=40+(r+l+e*5)%45,h=ne[(r+l+e)%ne.length],u=ne[(r+l+e+5)%ne.length],g=bt[(r+l+e)%bt.length];return[`The ${h} marker appears in many handbooks, but this ${s.toLowerCase()} rule is scoped only to ${n} in ${o}.`,`For release ${i}, ${m} must ${g} when the status age is above ${c} hours.`,`The answer should cite the local section before quoting the global handbook because the handbook omits the ${o} override.`,`A late chunk that carries the title and section metadata can distinguish ${n} from the similarly worded ${Ln(B,(0,xe.default)(`${n}-${o}`))} memo.`,`If the request mentions signal ${u}, keep it in the candidate set but do not promote it unless the service and region also match.`,`The escalation timer is ${t} business days and the stale evidence threshold is ${a} minutes.`,`Operators should mark priority ${d} on the retrieval trace so rerankers can explain why the section was selected.`,`When two chunks have identical body text, the chunk with release ${i} wins only if its contextual header names ${n} and ${o}.`]}function Bn(n){let o=wt(n),i=Jn(o),s=(0,xe.default)(`${Mn}#${o}#late-context-data`),m=[],d=[];for(let t=0;t<32;t++){let a=B[(t+i)%B.length],h=pt[(t+Math.floor(i/7))%pt.length],u=ft[(t+Math.floor(i/11))%ft.length],g={doc_id:`LC_DOC_${oe(t+1,3)}`,title:`${a.replace("_"," ")} retrieval handbook ${oe(t+1,3)}`,region:h,release:u,sections:[]};for(let w=0;w<5;w++){let y=yt[(t+w+i)%yt.length],k=gt[(t*2+w+i)%gt.length],b=1+(t+w+i)%5,f=B[(t+w+i)%B.length],p=Fn({service:f,region:h,release:u,heading:y,owner:k,priority:b,docIndex:t,sectionIndex:w,emailNumber:i}),x={section_id:`S${oe(w+1,2)}`,heading:y,service:f,owner:k,priority:b,sentences:p};g.sections.push(x),d.push({doc:g,section:x,sentence:p[1],targetIndex:1})}m.push(g)}let l=[],e=new Set;for(;l.length<28;){let t=Math.floor(s()*d.length);e.has(t)||(e.add(t),l.push(d[t]))}let r=l.map((t,a)=>({query_id:`LC_Q_${oe(a+1,3)}`,text:`Find the late chunk that explains what ${t.section.owner} must do for ${t.section.service} ${t.section.heading.toLowerCase()} in ${t.doc.region}.`,service:t.section.service,region:t.doc.region,release:t.doc.release,priority:t.section.priority}));return{documents:m,queries:r,rules:{chunk_sentence_count:4,chunk_sentence_overlap:1,top_k:4,bm25_k1:1.2,bm25_b:.75,contextual_template:"{title} {region} {release} {heading} {service} {owner} priority-{priority} {chunk_text}",query_template:"{text} {service} {region} {release} priority-{priority}",expected_output:"JSON object mapping each query_id to an array of the top_k chunk_id strings, sorted by BM25 score descending."}}}async function Pn({user:n,weight:o=2}){let i="q-late-chunking-context-retrieval-server",s="Late Chunking with Contextual Retrieval",m=Bn(n.email),d=new zn;d.file("documents.jsonl",m.documents.map(t=>JSON.stringify(t)).join(`
`)),d.file("queries.json",JSON.stringify(m.queries,null,2)),d.file("retrieval_rules.json",JSON.stringify(m.rules,null,2)),d.file("documents.md",m.documents.map(t=>[`# ${t.title}`,`region: ${t.region}`,`release: ${t.release}`,...t.sections.flatMap(a=>["",`## ${a.section_id} ${a.heading}`,`service: ${a.service}`,`owner: ${a.owner}`,`priority: ${a.priority}`,...a.sentences])].join(`
`)).join(`

---

`)),d.file("README.txt",`Late Chunking Challenge

Build chunks only after preserving document and section context. Return the top chunk IDs for each query.
`);let l=await d.generateAsync({type:"blob"}),e=URL.createObjectURL(l),r=jn`
    <div class="mb-4">
      <p class="lead">
        The BS Degree chatbot team found that ordinary sentence chunks confuse similarly worded policy
        sections across services and regions. Your job is to reproduce a late-chunking retrieval trace that
        keeps document context attached to each chunk.
      </p>

      <p><strong>Task:</strong></p>
      <ol>
        <li>Download the ZIP and read <code>retrieval_rules.json</code>.</li>
        <li>
          For every section in <code>documents.jsonl</code>, make sliding-window chunks of
          <code>chunk_sentence_count</code> sentences with <code>chunk_sentence_overlap</code> overlap.
          Use chunk IDs in this format: <code>LC_DOC_001:S01:w00</code>.
        </li>
        <li>
          Score chunks with BM25 over the contextual text template in the rules file. Build query text using
          the query template. Use <code>bm25_k1</code>, <code>bm25_b</code>, and tokenize with
          <code>/\\b[a-z0-9_]+\\b/g</code> after lowercasing.
        </li>
        <li>
          Return the top <code>top_k</code> chunk IDs for every query. Sort by BM25 score descending, then by
          chunk ID ascending to break ties.
        </li>
      </ol>

      <div class="my-3">
        <a href="${e}" download="late_chunking_contextual_retrieval.zip" class="btn btn-primary">
          Download Late Chunking Data
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit ranked chunk IDs as JSON</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "LC_Q_001": ["LC_DOC_001:S01:w00", "LC_DOC_014:S03:w01", "..."],\n  "LC_Q_002": ["..."]\n}'
          required
        ></textarea>
        <div class="form-text">
          Submit only the JSON object. Do not include scores, prose, or markdown fences.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the mapping exactly as a JSON object.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var xe,Mn,B,pt,ft,gt,yt,bt,ne,vt=A(()=>{"use strict";xe=R(O(),1),Mn="tds-ga4-late-chunking-data-2b5414d4e08627bc19dffa210e83013d3b48245376cd160b797d6f4ba22d4bd43e2eb9a2d6c3c0b57c04fdfaa8cc016d",B=["admissions","course_catalog","fees","identity","proctoring","scholarships","support","transcripts"],pt=["apac","emea","latam","na"],ft=["2026.05","2026.06","2026.07","2026.08"],gt=["argo","banyan","cedar","drona","ember","falcon","gingko","helios"],yt=["Policy Exceptions","Escalation Timers","Evidence Windows","Retry Controls","Audit Labels","Status Mapping"],bt=["refresh the derived status before sending the answer","attach the last verified event as supporting evidence","route the request through the regional reviewer queue","suppress stale draft notes from the final context","prefer the section-level rule over global boilerplate","raise a manual review flag when evidence is older than the limit"],ne=["amber","bronze","cobalt","delta","ember","fennel","granite","harbor","indigo","juniper","kepler","lumen"]});var At={};I(At,{default:()=>Wn});import Gn from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as Hn}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function Vn(n){return String(n||"").trim().toLowerCase()}function ve(n,o){return String(n).padStart(o,"0")}function $t(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}function ke(n,o,i){return $t(n.map(s=>s+(o()*2-1)*i))}function St(n){let o=(0,M.default)(`${qt}#vector#${n}`);return $t(Array.from({length:36},()=>o()*2-1))}function Qn(n){let o=Vn(n),i=(0,M.default)(`${qt}#${o}#semantic-cache-data`),s=G.map((e,r)=>St(`${r}-${e.join("-")}`)),m=[];for(let e=0;e<960;e++){let r=e%G.length,c=P[(e+Math.floor(i()*10))%P.length],t=kt[(e+Math.floor(i()*10))%kt.length],a=_t[(e+Math.floor(i()*10))%_t.length],h=G[r],u=`${h[e%h.length]} ${h[(e+1)%h.length]} help ${c} term ${2024+e%4}`;m.push({cache_id:`SC_C_${ve(e+1,4)}`,tenant:c,channel:t,language:a,created_minute:1e3+e*3,query:u,embedding:ke(s[r],(0,M.default)(`${o}#cache#${e}`),.045),answer_id:`ANS_${ve((r+1)*100+e%97,4)}`})}let d=[];for(let e=0;e<72;e++){let r=e%4!==3,c=m[(e*37+Math.floor(i()*23))%m.length],t=G.findIndex(b=>b.some(f=>c.query.includes(f))),a=G[Math.max(0,t)],h=r?c.tenant:P[(P.indexOf(c.tenant)+1)%P.length],u=c.channel,g=c.language,w=r?c.created_minute+120+e%90:c.created_minute+900+e,y=`${a[(e+2)%a.length]} ${a[(e+3)%a.length]} status ${h}`,k=r?ke(c.embedding,(0,M.default)(`${o}#request-hit#${e}`),.025):ke(St(`miss-${e}-${o}`),(0,M.default)(`${o}#request-miss#${e}`),.12);d.push({request_id:`SC_R_${ve(e+1,3)}`,tenant:h,channel:u,language:g,at_minute:w,query:y,embedding:k})}return{cache_entries:m,requests:d,expansion_map:Un,rules:{ttl_minutes:480,similarity_threshold:.91,candidate_filters:["tenant","channel","language","not expired"],output:"JSON object mapping request_id to {decision, cache_id, nearest_similarity, added_terms}. nearest_similarity is rounded to 4 decimals."}}}async function Wn({user:n,weight:o=2}){let i="q-semantic-cache-query-augmentation-server",s="Semantic Caching and Query Augmentation",m=Qn(n.email),d=new Gn;d.file("cache_entries.jsonl",m.cache_entries.map(t=>JSON.stringify(t)).join(`
`)),d.file("requests.json",JSON.stringify(m.requests,null,2)),d.file("expansion_map.json",JSON.stringify(m.expansion_map,null,2)),d.file("cache_rules.json",JSON.stringify(m.rules,null,2)),d.file("README.txt",`Semantic Cache Challenge

Apply query augmentation, filter valid cache entries, compute cosine similarity, and decide HIT or MISS.
`);let l=await d.generateAsync({type:"blob"}),e=URL.createObjectURL(l),r=Hn`
    <div class="mb-4">
      <p class="lead">
        A RAG support assistant is expensive because repeated questions still call the model. You need to
        simulate a semantic cache that uses tenant-safe filters, query expansion, TTL, and cosine similarity.
      </p>

      <p><strong>Task:</strong></p>
      <ol>
        <li>Download the ZIP and inspect <code>cache_rules.json</code>.</li>
        <li>
          For each request, tokenize its query with <code>/\\b[a-z0-9]+\\b/g</code>. Use
          <code>expansion_map.json</code> to list added expansion terms. Sort these terms alphabetically.
        </li>
        <li>
          Candidate cache entries must match <code>tenant</code>, <code>channel</code>, and
          <code>language</code>, and must not be older than <code>ttl_minutes</code>.
        </li>
        <li>
          Compute cosine similarity between the request embedding and each candidate cache embedding. Return
          <code>HIT</code> if the nearest valid candidate reaches the threshold; otherwise return
          <code>MISS</code>.
        </li>
      </ol>

      <div class="my-3">
        <a href="${e}" download="semantic_cache_query_augmentation.zip" class="btn btn-primary">
          Download Semantic Cache Data
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit cache decisions as JSON</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "SC_R_001": {"decision": "HIT", "cache_id": "SC_C_0001", "nearest_similarity": 0.9876, "added_terms": ["receipt"]},\n  "SC_R_002": {"decision": "MISS", "cache_id": null, "nearest_similarity": 0.4123, "added_terms": []}\n}'
          required
        ></textarea>
        <div class="form-text">
          Round <code>nearest_similarity</code> to exactly 4 decimals. Use <code>null</code> for a miss
          cache ID.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the cache decision mapping only.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var M,qt,P,kt,_t,G,Un,It=A(()=>{"use strict";M=R(O(),1),qt="tds-ga4-semantic-cache-data-0c52326402a2404371ad5f1ae83cb12fd628e05cd6e0c0477ab2836185b6db3c13cef8923de5922d3f14f5dab500763b",P=["degree","diploma","foundation"],kt=["web","mobile","ivr"],_t=["en","hi"],G=[["fee","refund","receipt","payment"],["exam","hallticket","slot","reschedule"],["course","credit","drop","withdraw"],["project","review","rubric","deadline"],["login","otp","profile","identity"],["certificate","transcript","grade","dispatch"],["scholarship","waiver","income","document"],["proctoring","camera","browser","violation"]],Un={fee:["payment","receipt"],refund:["reversal","bank"],exam:["assessment","slot"],hallticket:["admitcard","exam"],course:["subject","term"],project:["submission","rubric"],login:["signin","otp"],certificate:["transcript","dispatch"],scholarship:["waiver","income"],proctoring:["camera","browser"]}});var Ot={};I(Ot,{default:()=>eo});import Yn from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as Xn}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function Zn(n){return String(n||"").trim().toLowerCase()}function _e(n,o){return String(n).padStart(o,"0")}function se(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}function re(n,o,i){return se(n.map(s=>s+(o()*2-1)*i))}function Se(n){let o=(0,j.default)(`${Ct}#${n}`);return se(Array.from({length:48},()=>o()*2-1))}function ae(n){let o=Array.from({length:n[0].length},()=>0);for(let i of n)for(let s=0;s<o.length;s++)o[s]+=i[s];return se(o)}function Kn(n){let o=Zn(n),i=(0,j.default)(`${Ct}#${o}#multimodal-data`),s=Object.fromEntries(H.map(t=>[t,Se(`category-${t}`)])),m=Object.fromEntries(U.map(t=>[t,Se(`color-${t}`)])),d=Object.fromEntries(V.map(t=>[t,Se(`layout-${t}`)])),l=se(Array.from({length:48},(t,a)=>(a%5-2)/50)),e=[];for(let t=0;t<780;t++){let a=H[(t+Math.floor(i()*9))%H.length],h=ie[(t+Math.floor(i()*9))%ie.length],u=U[(t*2+Math.floor(i()*9))%U.length],g=V[(t*3+Math.floor(i()*9))%V.length],w=ae([s[a],m[u],d[g]]),y=ae([s[a],m[u],d[g],l]);e.push({item_id:`MM_I_${_e(t+1,4)}`,category:a,locale:h,color:u,layout:g,caption:`${h} ${u} ${g} ${a} artifact ${_e(t+1,4)}`,text_embedding:re(w,(0,j.default)(`${o}#text#${t}`),.05),image_embedding:re(y,(0,j.default)(`${o}#image#${t}`),.06)})}let r=[];for(let t=0;t<42;t++){let a=H[(t+Math.floor(i()*11))%H.length],h=ie[(t+Math.floor(i()*7))%ie.length],u=U[(t+Math.floor(i()*13))%U.length],g=V[(t+Math.floor(i()*17))%V.length],w=ae([s[a],m[u],d[g]]),y=ae([s[a],m[u],d[g],l]);r.push({query_id:`MM_Q_${_e(t+1,3)}`,text:`Find ${h} ${u} ${g} ${a} artifacts.`,target_category:a,target_locale:h,category_filter:t%5===0?null:a,locale_filter:t%6===0?null:h,text_weight:t%3===0?.65:.55,image_weight:t%3===0?.35:.45,text_embedding:re(w,(0,j.default)(`${o}#query-text#${t}`),.04),image_embedding:re(y,(0,j.default)(`${o}#query-image#${t}`),.045)})}return{items:e,queries:r,calibration:{image_delta:l,category_match_boost:.025,locale_match_boost:.015,top_k:5,output:"JSON object mapping query_id to an array of top_k item_id strings sorted by calibrated score."}}}async function eo({user:n,weight:o=2}){let i="q-multimodal-embedding-calibration-server",s="Multimodal Embedding Calibration",m=Kn(n.email),d=new Yn;d.file("items.jsonl",m.items.map(t=>JSON.stringify(t)).join(`
`)),d.file("queries.json",JSON.stringify(m.queries,null,2)),d.file("calibration.json",JSON.stringify(m.calibration,null,2)),d.file("README.txt",`Multimodal Calibration Challenge

Calibrate image embeddings, combine text and image similarity, apply filters and boosts, and rank artifacts.
`);let l=await d.generateAsync({type:"blob"}),e=URL.createObjectURL(l),r=Xn`
    <div class="mb-4">
      <p class="lead">
        A document search system stores separate text and image embeddings for scanned learning artifacts.
        The image encoder has a small modality bias, so raw cosine search is not enough. Calibrate the image
        vectors, combine modalities, and return the final ranking.
      </p>

      <p><strong>Task:</strong></p>
      <ol>
        <li>Download the ZIP and read <code>calibration.json</code>.</li>
        <li>
          For every item, subtract <code>image_delta</code> from <code>image_embedding</code>, then L2-normalize
          the result.
        </li>
        <li>
          Apply each query's category and locale filters when they are not <code>null</code>.
        </li>
        <li>
          Score each valid item:
          <pre><code>text_weight * cosine(query_text, item_text)
+ image_weight * cosine(query_image, calibrated_item_image)
+ category_match_boost if item.category equals target_category
+ locale_match_boost if item.locale equals target_locale</code></pre>
        </li>
        <li>Return the top <code>top_k</code> item IDs for every query, breaking ties by item ID.</li>
      </ol>

      <div class="my-3">
        <a href="${e}" download="multimodal_embedding_calibration.zip" class="btn btn-primary">
          Download Multimodal Embedding Data
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit ranked item IDs as JSON</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "MM_Q_001": ["MM_I_0001", "MM_I_0231", "MM_I_0442", "MM_I_0108", "MM_I_0710"],\n  "MM_Q_002": ["..."]\n}'
          required
        ></textarea>
        <div class="form-text">
          Submit only the JSON object mapping each query ID to its top 5 ranked item IDs.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the ranked item mapping only.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var j,Ct,H,ie,U,V,Rt=A(()=>{"use strict";j=R(O(),1),Ct="tds-ga4-multimodal-data-50b663aeac4714b9eb240a19f7a7566a5842a9c2ccd6b33c4c75cfa5643d3f6890ca7d0e9d5250b97eb7ed110731c069",H=["poster","invoice","certificate","diagram","screenshot","id_card"],ie=["en","hi","ta","te"],U=["blue","green","red","yellow","gray","violet"],V=["dense","spacious","two_column","bordered","minimal","annotated"]});var zt={};I(zt,{default:()=>ro});import to from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as no}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function oo(n){return String(n||"").trim().toLowerCase()}function Dt(n,o){return String(n).padStart(o,"0")}function $e(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}function qe(n,o,i){return $e(n.map(s=>s+(o()*2-1)*i))}function Nt(n){let o=(0,L.default)(`${Tt}#${n}`);return $e(Array.from({length:32},()=>o()*2-1))}function Et(n){let o=Array.from({length:n[0].length},()=>0);for(let i of n)for(let s=0;s<o.length;s++)o[s]+=i[s];return $e(o)}function io(n){let o=oo(n),i=(0,L.default)(`${Tt}#${o}#hyde-data`),s=Object.fromEntries(Q.map(r=>[r,Nt(`category-${r}`)])),m=Object.fromEntries(W.map(r=>[r,Nt(`year-${r}`)])),d=[];for(let r=0;r<500;r++){let c=Q[(r+Math.floor(i()*7))%Q.length],t=W[(r*2+Math.floor(i()*7))%W.length],a=Et([s[c],m[t]]);d.push({item_id:`KB_I_${Dt(r+1,4)}`,category:c,publish_year:t,text_embedding:qe(a,(0,L.default)(`${o}#item#${r}`),.05)})}let l=[];for(let r=0;r<40;r++){let c=Q[(r+Math.floor(i()*9))%Q.length],t=W[(r*3+Math.floor(i()*9))%W.length],a=Et([s[c],m[t]]),h=r%3===0?.3:.4;l.push({query_id:`HQ_${Dt(r+1,3)}`,query_text:`Something is wrong with my ${c} \u2014 what should I do?`,target_category:c,min_year:t,raw_weight:h,hyde_weight:Number((1-h).toFixed(2)),query_embedding:qe(a,(0,L.default)(`${o}#query#${r}`),.14),hypothetical_answers:[0,1,2].map(u=>({text:`Hypothetical answer ${u+1} for query ${r+1} about ${c} policies from ${t}.`,embedding:qe(a,(0,L.default)(`${o}#hyde#${r}#${u}`),.05)}))})}return{items:d,queries:l,rules:{top_k:5,category_match_boost:.03,recency_boost:.02,recency_rule:"item.publish_year >= query.min_year",hyde_vector_rule:"normalize(sum of the 3 hypothetical_answers[].embedding, component-wise)",final_vector_rule:"normalize(raw_weight * query_embedding + hyde_weight * hyde_vector, component-wise)",output:"JSON object mapping query_id to an array of top_k item_id strings sorted by final blended score."}}}async function ro({user:n,weight:o=2}){let i="q-hyde-hypothetical-retrieval-server",s="HyDE: Hypothetical Document Embeddings for Query Augmentation",m=io(n.email),d=new to;d.file("items.jsonl",m.items.map(t=>JSON.stringify(t)).join(`
`)),d.file("queries.json",JSON.stringify(m.queries,null,2)),d.file("retrieval_rules.json",JSON.stringify(m.rules,null,2)),d.file("README.txt",`HyDE Query Augmentation Challenge

Short student queries embed poorly and land far from the knowledge-base articles that answer them.
Build a Hypothetical Document Embeddings (HyDE) pipeline: embed a few hypothetical answers, blend
that with the raw query embedding, and rank knowledge-base items against the blended vector.
`);let l=await d.generateAsync({type:"blob"}),e=URL.createObjectURL(l),r=no`
    <div class="mb-4">
      <p class="lead">
        The BS Degree helpdesk assistant struggles with short, vague student questions — their raw query
        embeddings land far from the knowledge-base articles that actually answer them. Your job is to
        reproduce a HyDE (Hypothetical Document Embeddings) retrieval pipeline that fixes this.
      </p>

      <p><strong>Task:</strong></p>
      <ol>
        <li>Download the ZIP and read <code>retrieval_rules.json</code>.</li>
        <li>
          For every query, compute the <strong>HyDE vector</strong>: sum the embeddings of its 3
          <code>hypothetical_answers</code> component-wise, then L2-normalize the result.
        </li>
        <li>
          Compute the <strong>final vector</strong>: <code>raw_weight * query_embedding + hyde_weight *
          hyde_vector</code> (component-wise), then L2-normalize the result. Use the exact
          <code>raw_weight</code> and <code>hyde_weight</code> given for that query.
        </li>
        <li>
          Score every item as <code>cosine(final_vector, item.text_embedding)</code>, plus
          <code>category_match_boost</code> if <code>item.category === query.target_category</code>, plus
          <code>recency_boost</code> if <code>item.publish_year >= query.min_year</code>.
        </li>
        <li>
          Return the top <code>top_k</code> item IDs for every query, sorted by score descending, then by
          item ID ascending to break ties.
        </li>
      </ol>

      <div class="my-3">
        <a href="${e}" download="hyde_hypothetical_retrieval.zip" class="btn btn-primary">
          Download HyDE Retrieval Data
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit ranked item IDs as JSON</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "HQ_001": ["KB_I_0001", "KB_I_0042", "..."],\n  "HQ_002": ["..."]\n}'
          required
        ></textarea>
        <div class="form-text">
          Submit only the JSON object. Do not include scores, prose, or markdown fences.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the mapping exactly as a JSON object.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var L,Tt,Q,W,jt=A(()=>{"use strict";L=R(O(),1),Tt="tds-ga4-hyde-data-5203f61502e12bdcacc52e5a3078c423fb3268646470906a2b5fcff1076a66071613d66507f5fe8365838d3f2c6f8441",Q=["billing","enrollment","assessment","curriculum","aid","integrity","records","helpdesk"],W=[2023,2024,2025,2026]});var Ft={};I(Ft,{default:()=>yo});import ao from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as so}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function po(n){return String(n||"").trim().toLowerCase()}function Ie(n,o){return String(n).padStart(o,"0")}function Jt(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}function Mt(n,o,i){return Jt(n.map(s=>s+(o()*2-1)*i))}function fo(n){let o=(0,Y.default)(`${Lt}#${n}`);return Jt(Array.from({length:ho},()=>o()*2-1))}function go(n){let o=po(n),i=(0,Y.default)(`${Lt}#${o}#ann-data`),s=Array.from({length:Ae},(e,r)=>({centroid_id:`CEN_${Ie(r,2)}`,embedding:fo(`centroid-${o}-${r}`)})),m=[];for(let e=0;e<co;e++){let r=Math.floor(i()*Ae);m.push({item_id:`VDB_I_${Ie(e+1,4)}`,embedding:Mt(s[r].embedding,(0,Y.default)(`${o}#item#${e}`),uo)})}let d=[];for(let e=0;e<lo;e++){let r=Math.floor(i()*Ae);d.push({query_id:`ANN_Q_${Ie(e+1,3)}`,nprobe:e%4+1,embedding:Mt(s[r].embedding,(0,Y.default)(`${o}#query#${e}`),mo)})}return{centroids:s,items:m,queries:d,rules:{top_k:5,assignment_rule:"Assign each item to the centroid with highest cosine similarity (ties broken by lowest centroid_id).",probe_rule:"Rank all centroids by cosine similarity to the query embedding descending (ties by lowest centroid_id). Take the top `nprobe` centroids for that query.",candidate_rule:"The candidate set is the union of all items assigned to the probed centroids only.",search_rule:"Within the candidate set only, rank by cosine similarity to the query descending (ties by item_id ascending). Return top_k.",output:"JSON object mapping query_id to an array of top_k item_id strings."}}}async function yo({user:n,weight:o=2}){let i="q-ann-index-recall-latency-server",s="ANN Index: IVF Recall vs. Latency Tradeoff",m=go(n.email),d=new ao;d.file("centroids.json",JSON.stringify(m.centroids,null,2)),d.file("items.jsonl",m.items.map(t=>JSON.stringify(t)).join(`
`)),d.file("queries.json",JSON.stringify(m.queries,null,2)),d.file("index_rules.json",JSON.stringify(m.rules,null,2)),d.file("README.txt",`IVF Approximate Nearest Neighbor Challenge

Build a two-level IVF-style index: assign every item to its nearest centroid (the "inverted lists"),
then for each query probe only its nprobe nearest centroids' lists instead of scanning the whole
corpus. This trades recall for latency -- a small nprobe is fast but can miss the true nearest
neighbors sitting in an unprobed cluster.
`);let l=await d.generateAsync({type:"blob"}),e=URL.createObjectURL(l),r=so`
    <div class="mb-4">
      <p class="lead">
        InfoCore's vector database has grown too large for brute-force search on every query. Your job is
        to build an IVF-style (Inverted File) approximate index: cluster items under centroids, then
        restrict each query's search to only its <code>nprobe</code> nearest clusters.
      </p>

      <p><strong>Task:</strong></p>
      <ol>
        <li>Download the ZIP and read <code>index_rules.json</code>.</li>
        <li>
          Assign every item in <code>items.jsonl</code> to its nearest centroid in
          <code>centroids.json</code> by cosine similarity (ties go to the lowest <code>centroid_id</code>).
          This builds one inverted list per centroid.
        </li>
        <li>
          For every query, rank all centroids by cosine similarity to the query embedding, and keep only
          the top <code>nprobe</code> centroids (given per query). The candidate set is the union of the
          inverted lists of just those centroids &mdash; <strong>do not</strong> search the full corpus.
        </li>
        <li>
          Within that restricted candidate set only, rank items by cosine similarity to the query
          descending (ties by item ID ascending) and return the top <code>top_k</code> item IDs.
        </li>
      </ol>

      <div class="my-3">
        <a href="${e}" download="ann_index_recall_latency.zip" class="btn btn-primary">
          Download ANN Index Data
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit ranked item IDs as JSON</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "ANN_Q_001": ["VDB_I_0001", "VDB_I_0042", "..."],\n  "ANN_Q_002": ["..."]\n}'
          required
        ></textarea>
        <div class="form-text">
          Submit only the JSON object. Results must come from the <code>nprobe</code>-restricted
          candidate set, not a full brute-force scan.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the mapping exactly as a JSON object.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var Y,Lt,Ae,co,lo,ho,uo,mo,Bt=A(()=>{"use strict";Y=R(O(),1),Lt="tds-ga4-ann-data-9b212e1877f9a0b061ad49307ed02d1e65cdb193b9d38ed4dcb9d7cb2ec9935349a039acec4e81f5c6f4f64382122d6e",Ae=20,co=900,lo=45,ho=8,uo=.7,mo=.55});var Vt={};I(Vt,{default:()=>$o});import bo from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as wo}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function Ht(n){return String(n||"").trim().toLowerCase()}function Oe(n,o){return String(n).padStart(o,"0")}function So(n){return Ht(n).split("").reduce((o,i)=>Math.imul(o,33)+i.charCodeAt(0)>>>0,5381)}function Ut(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}function Re(n,o,i){return Ut(n.map(s=>s+(o()*2-1)*i))}function Gt(n){let o=(0,X.default)(`${xo}#${n}`);return Ut(Array.from({length:_o},()=>o()*2-1))}function qo(n){let o=Ht(n),i=So(o),s=[],m=0,d=[];for(let e=0;e<Pt;e++){let r=Gt(`family-${o}-${e}`),c=3e3+(e*37+i)%90*500,t=3+(e*7+i)%5;d.push({baseVector:r,numericFact:c});for(let a=0;a<t;a++)m+=1,s.push({doc_id:`SD_${Oe(m,4)}`,embedding:Re(r,(0,X.default)(`${o}#fam#${e}#${a}`),Ce),numeric_fact:c})}for(let e=0;e<vo;e++){let r=d[(e*13+i)%Pt],c=e%2===0?1:-1,t=200+e%5*37;m+=1,s.push({doc_id:`SD_${Oe(m,4)}`,embedding:Re(r.baseVector,(0,X.default)(`${o}#trap#${e}`),Ce),numeric_fact:r.numericFact+c*t})}for(let e=0;e<ko;e++){let r=Gt(`singleton-${o}-${e}`);m+=1,s.push({doc_id:`SD_${Oe(m,4)}`,embedding:Re(r,(0,X.default)(`${o}#single#${e}`),Ce),numeric_fact:3e3+(e*53+i)%90*500})}return{docs:s,rules:{similarity_threshold:.92,numeric_tolerance:50,numeric_field:"numeric_fact",merge_rule:"For every pair of documents, merge them into the same dedup group only if cosine(embedding_a, embedding_b) >= similarity_threshold AND abs(numeric_fact_a - numeric_fact_b) <= numeric_tolerance. Take the transitive closure of all merges (union-find).",canonical_rule:"Within each dedup group, the canonical_id is the lexicographically smallest doc_id in the group.",output:"JSON object mapping every doc_id to its canonical_id (a doc with no duplicates maps to itself)."}}}async function $o({user:n,weight:o=2}){let i="q-semantic-dedup-numeric-guardrail-server",s="Semantic Deduplication with Numeric-Fact Guardrails",m=qo(n.email),d=new bo;d.file("documents.jsonl",m.docs.map(t=>JSON.stringify(t)).join(`
`)),d.file("dedup_rules.json",JSON.stringify(m.rules,null,2)),d.file("README.txt",`Semantic Deduplication Challenge

Embedding similarity alone is not safe for deduplication: two policy notices can be near-identical in
wording (and embedding space) while quoting two different fee amounts. Merge documents only when both
their embeddings AND their numeric facts agree within tolerance.
`);let l=await d.generateAsync({type:"blob"}),e=URL.createObjectURL(l),r=wo`
    <div class="mb-4">
      <p class="lead">
        The BS Degree policy archive has accumulated hundreds of near-duplicate notices. A naive
        embedding-similarity dedup would incorrectly merge notices that are worded almost identically but
        quote a <em>different</em> fee amount. Build a deduplication pipeline that only merges documents
        when both the embeddings <strong>and</strong> the numeric fact agree.
      </p>

      <p><strong>Task:</strong></p>
      <ol>
        <li>Download the ZIP and read <code>dedup_rules.json</code>.</li>
        <li>
          For every pair of documents, compute cosine similarity between their embeddings. Merge the pair
          into the same dedup group only if the similarity is at least <code>similarity_threshold</code>
          <strong>and</strong> <code>|numeric_fact_a - numeric_fact_b| &le; numeric_tolerance</code>.
        </li>
        <li>
          Take the transitive closure of all merges (i.e. build connected components / union-find over the
          qualifying pairs).
        </li>
        <li>
          For every connected component, its <code>canonical_id</code> is the lexicographically smallest
          <code>doc_id</code> in that group. A document with no duplicates maps to itself.
        </li>
      </ol>

      <div class="my-3">
        <a href="${e}" download="semantic_dedup_numeric_guardrail.zip" class="btn btn-primary">
          Download Semantic Dedup Data
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit canonical ID mapping as JSON</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "SD_0001": "SD_0001",\n  "SD_0002": "SD_0001",\n  "SD_0003": "SD_0003"\n}'
          required
        ></textarea>
        <div class="form-text">
          Submit a JSON object with one entry for every document ID in the dataset.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the canonical ID mapping exactly as a JSON object.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var X,xo,Pt,vo,ko,_o,Ce,Qt=A(()=>{"use strict";X=R(O(),1),xo="tds-ga4-dedup-data-18aae18831e243c9bea945c8822447aeb7cbcf66ee5c48e59044f142adc1f1e7d26da7f2760f94825cbc6b5d7f0a60b4",Pt=50,vo=55,ko=70,_o=32,Ce=.03});var Yt={};I(Yt,{default:()=>No});import Ao from"https://cdn.jsdelivr.net/npm/jszip@3/+esm";import{html as Io}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function Ro(n){return String(n||"").trim().toLowerCase()}function De(n,o){return String(n).padStart(o,"0")}function Do(n){let o=Ro(n),i=(0,Wt.default)(`${Co}#${o}#context-assembly-data`),s=[];for(let d=0;d<Oo;d++){let l=15+Math.floor(i()*16),e=[],r=0;for(let a=0;a<l;a++){let h=80+Math.floor(i()*321),u=Number(i().toFixed(4));r+=h,e.push({chunk_id:`CTX_${De(d+1,3)}_${De(a+1,3)}`,token_count:h,relevance_score:u})}let c=.35+d%7*.05,t=Math.round(r*c);s.push({query_id:`CA_Q_${De(d+1,3)}`,token_budget:t,candidate_chunks:e})}return{queries:s,rules:{selection_rule:"Sort candidate_chunks by relevance_score descending (ties broken by chunk_id ascending). Walk this order once, keeping a running token total: if a chunk's token_count fits within the remaining token_budget, select it and add its tokens to the running total; otherwise skip it and continue to the next chunk (do not stop at the first chunk that does not fit).",assembly_rule:"Take the selected chunks in relevance_score-descending order c1 (highest) .. cn (lowest). Build the final sequence by alternating from the outside in: c1 goes to position 0, c2 goes to the last position, c3 to position 1, c4 to the second-to-last position, and so on -- the most relevant selected chunks anchor both ends of the context and the least relevant selected chunk ends up in the middle.",output:"JSON object mapping query_id to an array of the selected chunk_id strings in final assembled order."}}}async function No({user:n,weight:o=2}){let i="q-context-assembly-lost-middle-server",s="Context Assembly: Beating Lost-in-the-Middle",m=Do(n.email),d=new Ao;d.file("queries.json",JSON.stringify(m.queries,null,2)),d.file("assembly_rules.json",JSON.stringify(m.rules,null,2)),d.file("README.txt",`Lost-in-the-Middle Context Assembly Challenge

LLMs pay the most attention to the start and end of a long context and the least to the middle. Given
a token budget, select which retrieved chunks fit, then arrange the selected chunks so the most
relevant ones anchor both ends of the context and the weakest one lands in the middle.
`);let l=await d.generateAsync({type:"blob"}),e=URL.createObjectURL(l),r=Io`
    <div class="mb-4">
      <p class="lead">
        The BS Degree RAG assistant retrieves far more candidate chunks than fit in its context window, and
        naively concatenating the most relevant chunks first buries the weakest (but still selected) chunks
        in the middle where LLMs pay the least attention. Build a context assembler that respects a token
        budget and arranges chunks to counter this "lost in the middle" effect.
      </p>

      <p><strong>Task:</strong></p>
      <ol>
        <li>Download the ZIP and read <code>assembly_rules.json</code>.</li>
        <li>
          For every query, sort its <code>candidate_chunks</code> by <code>relevance_score</code>
          descending (ties by <code>chunk_id</code> ascending). Walk this order once: if a chunk fits in
          the remaining <code>token_budget</code>, select it and deduct its tokens; otherwise skip it and
          keep going &mdash; do not stop at the first chunk that doesn't fit.
        </li>
        <li>
          Arrange the selected chunks (still in relevance order c1..cn) into the final sequence by
          alternating from the outside in: c1 &rarr; position 0, c2 &rarr; last position, c3 &rarr;
          position 1, c4 &rarr; second-to-last position, and so on.
        </li>
      </ol>

      <div class="my-3">
        <a href="${e}" download="context_assembly_lost_middle.zip" class="btn btn-primary">
          Download Context Assembly Data
        </a>
      </div>

      <div class="mb-3">
        <label for="${i}" class="form-label"><strong>Submit assembled chunk order as JSON</strong></label>
        <textarea
          class="form-control font-monospace"
          id="${i}"
          name="${i}"
          rows="10"
          placeholder='{\n  "CA_Q_001": ["CTX_001_003", "CTX_001_009", "..."],\n  "CA_Q_002": ["..."]\n}'
          required
        ></textarea>
        <div class="form-text">
          Submit only the JSON object. Array lengths vary per query depending on how many chunks fit the
          budget.
        </div>
      </div>
    </div>
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the mapping exactly as a JSON object.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var Wt,Co,Oo,Xt=A(()=>{"use strict";Wt=R(O(),1),Co="tds-ga4-context-assembly-data-271d73ad9bab61b3517cb379323b28edc716443bd31059bdafc8e7b17bd944fc5bec2f3ba9986e34e47d23f992d68767",Oo=45});var Kt={};I(Kt,{default:()=>Bo});import{html as Ne}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function jo(n){return String(n||"").trim().toLowerCase()}function le(n,o,i){return o+Math.floor(n()*(i-o+1))}function Ee(n,o){return o[Math.floor(n()*o.length)]}function Mo(n,o){let i=le(n,4,6),s=new Set;for(;s.size<i;)s.add(Ee(n,o));return[...s].join(" ")}function Lo({email:n,id:o=To,version:i=""}){let s=(0,Zt.default)(`${jo(n)}#${o}#${i??""}`),m=[];for(let e=1;e<=Eo;e++){let r=le(s,0,ce.length-1),c=le(s,20,45),t=[];for(let a=0;a<c;a++)t.push(s()<.65?Ee(s,ce[r]):Ee(s,zo));m.push({id:e,text:t.join(" ")})}let d=le(s,0,ce.length-1),l=Mo(s,ce[d]);return{docs:m,query:l}}function Jo(n){return Ne`
    <div class="table-responsive border rounded" style="max-height: 360px; overflow: auto;">
      <table class="table table-sm table-bordered align-middle mb-0">
        <thead class="table-light" style="position: sticky; top: 0; z-index: 1;">
          <tr>
            <th scope="col" style="width: 5rem;">Doc ID</th>
            <th scope="col">Text</th>
          </tr>
        </thead>
        <tbody>
          ${n.map(o=>Ne`
                <tr>
                  <td><code>${o.id}</code></td>
                  <td class="font-monospace small">${o.text}</td>
                </tr>
              `)}
        </tbody>
      </table>
    </div>
  `}function Fo(n){if(String(n||"").length>2e3)throw new Error("Submission is too large.");let o;try{o=JSON.parse(n)}catch{throw new Error("Submit valid JSON.")}if(!o||typeof o!="object"||Array.isArray(o)||Object.keys(o).sort().join(",")!=="third_score,top5"||!Array.isArray(o.top5)||o.top5.length!==5||!o.top5.every(Number.isInteger)||!Number.isFinite(o.third_score))throw new Error('Use exactly {"top5":[...],"third_score":...}.')}async function Bo({user:n,weight:o=2,version:i=""}){let s="q-rrf-fusion-server",m="Reciprocal Rank Fusion by Hand",{docs:d,query:l}=Lo({email:n.email,id:s,version:i}),e=new Blob([JSON.stringify({query:l,docs:d},null,2)],{type:"application/json"}),r=URL.createObjectURL(e),c=Ne`
  <div class="mb-3">
    <p class="lead">
      Real search systems rarely rely on one retrieval method. <strong>Keyword search</strong> (like BM25) finds
      documents that share exact words with your query. <strong>Semantic search</strong> (embeddings + cosine
      similarity) can find documents that mean the same thing even when the wording differs. Each method misses
      things the other one catches — so production systems often run both and merge the results.
    </p>
    <p>
      Your job: build both ranked lists yourself from the corpus below, then merge them with
      <strong>Reciprocal Rank Fusion (RRF)</strong>.
    </p>

    <div class="p-3 my-3 border rounded">
      <h6 class="mb-2">Query</h6>
      <code class="fs-6">${l}</code>
    </div>

    <div class="d-flex align-items-center justify-content-between gap-3 mt-4 mb-2">
      <h6 class="mb-0">Corpus (150 documents)</h6>
      <a class="btn btn-sm btn-outline-primary" href="${r}" download="rrf-corpus.json">
        Download corpus as JSON
      </a>
    </div>
    ${Jo(d)}

    <h6 class="mt-4">Tokenizer</h6>
    <p>
      Use this <em>everywhere</em> below — corpus docs, query, BM25, and hashing all need to agree on what counts as
      a "word", or your two lists won't match anyone else's (including ours): lowercase the string, split on
      <code>/[^a-z0-9]+/</code>, drop empty tokens.
    </p>

    <h6 class="mt-4">Step 1 — List A: BM25 (keyword retrieval)</h6>
    <p>
      BM25 scores a document higher when it contains the query's words more often — but with two corrections that
      keep it honest. <strong>IDF</strong> downweights words that appear in almost every document (they carry little
      information). <strong>Length normalization</strong> stops long documents from winning purely by containing more
      words overall; <code>k1</code> controls how much extra term repetitions are worth (with diminishing returns),
      and <code>b</code> controls how strongly length is penalized.
    </p>
    <pre><code>k1 = 1.5, b = 0.75, N = 150 (corpus size)

df(t)   = number of docs containing term t at least once
f(t,d)  = number of times t appears in doc d
avgdl   = mean token count across all 150 docs

idf(t) = ln((N - df(t) + 0.5) / (df(t) + 0.5) + 1)

score(doc, query) =
  sum over unique query terms t of
  idf(t) * f(t, doc) * (k1 + 1)
  / (f(t, doc) + k1 * (1 - b + b * |doc| / avgdl))</code></pre>
    <p class="mb-1"><strong>Worked example (fake numbers, not your corpus):</strong></p>
    <pre><code>N = 10, df("cache") = 2, f("cache", doc7) = 3, |doc7| = 30, avgdl = 25
idf("cache") = ln((10 - 2 + 0.5) / (2 + 0.5) + 1) = 1.481605
term contribution = 1.481605 * 3 * 2.5 / (3 + 1.5*(1 - 0.75 + 0.75*30/25)) = 2.351754</code></pre>
    <p>
      Rank all 150 docs by score descending (lower doc ID breaks ties). The top 20 IDs are <strong>List A</strong>.
    </p>

    <h6 class="mt-4">Step 2 — List B: hashed embeddings (semantic retrieval)</h6>
    <p>
      Real embedding models map words to vectors learned from huge amounts of text. We can't ship a trained model
      into an exam, so instead you'll build a tiny deterministic stand-in using the
      <a href="https://en.wikipedia.org/wiki/Feature_hashing" target="_blank" rel="noopener">hashing trick</a>:
      hash each word to a fixed "slot" so the whole vocabulary — no matter how large — fits in a small vector of
      length 64. Random <code>+1</code>/<code>-1</code> signs keep hash collisions from all pushing the same
      direction. Normalizing each vector to length 1 means we're comparing <em>direction</em> (what the document is
      about), not <em>magnitude</em> (how long it is) — exactly what cosine similarity between real embeddings does.
    </p>
    <pre><code>D = 64  (vector length)

FNV-1a hash of a token:
  hash = 0x811c9dc5
  for each character c: hash = hash XOR charCode(c); hash = Math.imul(hash, 0x01000193)
  hash = hash >>> 0

bucket = hash % 64
sign   = ((hash >>> 16) & 1) === 0 ? 1 : -1</code></pre>
    <p>
      For each token <em>occurrence</em> (not just unique words) in a document, add <code>sign</code> at
      <code>bucket</code> in that document's 64-length vector. Do the same for the query. L2-normalize both vectors,
      then take their dot product (= cosine similarity; a zero-norm vector has similarity 0 to anything). Rank all
      150 docs by similarity descending (lower doc ID breaks ties). The top 20 IDs are <strong>List B</strong>.
    </p>

    <h6 class="mt-4">Step 3 — Fuse with RRF</h6>
    <p>
      BM25 scores and cosine similarities live on completely different scales — one is roughly unbounded, the other
      sits between −1 and 1 — so averaging them directly would let whichever method has bigger numbers dominate for
      no good reason. RRF sidesteps that: it only looks at each document's <em>rank position</em> in each list, not
      its raw score, so the two methods combine on equal footing.
    </p>
    <pre><code>score(doc) = sum over lists containing doc of 1 / (60 + rank_in_that_list)</code></pre>
    <p>
      Ranks are 1-indexed; a document missing from a list contributes 0 for it. Round scores to 6 decimals, then
      sort descending (lower doc ID breaks ties).
    </p>
    <pre><code>List A: [101, 205], List B: [205, 309]
score(101) = 1/61          = 0.016393
score(205) = 1/62 + 1/61   = 0.032522
score(309) = 1/62          = 0.016129
Fused order: [205, 101, 309]</code></pre>

    <h6 class="mt-4">What to submit</h6>
    <ul class="mb-3">
      <li><code>top5</code>: the fused top 5 document IDs, in order.</li>
      <li><code>third_score</code>: the rounded RRF score of the 3rd-ranked document.</li>
    </ul>

    <label for="${s}" class="form-label"><strong>JSON answer</strong></label>
    <textarea
      class="form-control font-monospace"
      id="${s}"
      name="${s}"
      rows="4"
      placeholder='{"top5":[14,3,27,8,19],"third_score":0.016129}'
    ></textarea>
    <div class="form-text">
      Partial credit is position-sensitive: 70% for the ordered top 5, 30% for the 3rd score.
    </div>
  </div>
`;return{id:s,title:m,weight:o,question:c,answer:async a=>{Fo(a);let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:s,version:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Verification failed.");return u}}}var Zt,Eo,To,ce,zo,en=A(()=>{"use strict";Zt=R(O(),1),Eo=150,To="q-rrf-fusion-server",ce=["invoice ledger revenue expense margin budget forecast audit payroll vendor asset liability equity tax cashflow profit loss credit debit capital accrual balance statement variance treasury","shipment warehouse inventory carrier route freight delivery pallet dispatch tracking dock container manifest customs fulfillment barcode scanner transit fleet lastmile packaging returns supply demand reorder","sensor device signal voltage current circuit gateway firmware telemetry battery antenna network protocol packet latency bandwidth module controller actuator calibration diagnostic frequency resistance connector hardware","patient clinic diagnosis therapy dosage symptom vaccine screening nurse doctor hospital pharmacy medication allergy recovery treatment infection chronic acute laboratory sample trial wellness triage prescription","student course lesson grade assignment quiz lecture campus faculty syllabus tutorial semester credit rubric library classroom enrollment degree alumni workshop mentor project exam feedback certificate","server database cache api endpoint request response thread cluster container runtime deploy scaling memory cpu queue worker session token schema migration backup replica shard timeout","campaign audience brand content channel conversion impression click creative segment retention loyalty promotion pricing survey persona funnel newsletter sponsor launch market social engagement lead growth","weather climate rainfall temperature humidity pressure forecast storm monsoon drought wind cloud satellite radar season cyclone flood heatwave snowfall evaporation airmass front precipitation visibility barometer","recipe ingredient kitchen flavor spice sauce baking grill roast simmer texture portion nutrition protein carbohydrate vitamin menu chef restaurant cuisine pantry grain vegetable dessert beverage","contract clause policy compliance regulation license permit liability privacy security breach audit standard governance risk control evidence approval review obligation dispute retention consent jurisdiction filing","image pixel camera render filter contrast brightness histogram texture object detection segmentation label frame video resolution channel mask feature vision caption scene depth color annotation","graph node edge path degree centrality community network cluster bridge weight flow route matrix adjacency component link neighbor distance ranking pagerank subgraph cycle tree bipartite"].map(n=>n.split(" ")),zo="the and for with from into using across between during after before under over within without near through about each many some every this that these those when where while".split(" ")});import{html as F,render as cn}from"https://cdn.jsdelivr.net/npm/lit-html@3/lit-html.js";function Te(n,o){let i=F`<ol class="mt-3">
    ${n.map(({id:d,title:l,weight:e})=>F`<li><a href="#h${d}">${l}</a> (${e} ${e==1?"mark":"marks"})</li>`)}
  </ol>`,s=[F`<h1 class="display-6">Questions</h1>`,i,...n.map(({id:d,title:l,weight:e,question:r,help:c},t)=>(c&&!Array.isArray(c)&&(c=[c]),F`
        <div class="card my-5" data-question="${d}" id="h${d}">
          <div class="card-header">
            <span class="badge text-bg-primary me-2">${t+1}</span>
            ${l} (${e} ${e==1?"mark":"marks"})
          </div>
          ${c?c.map(a=>F`<div class="card-body border-bottom">${a}</div>`):""}
          <div class="card-body">${r}</div>
          <div class="card-footer d-flex">
            <button type="button" class="btn btn-primary check-answer" data-question="${d}">Check</button>
          </div>
        </div>
      `))],m={index:i,questions:s};for(let[d,l]of o)cn(m[l],d)}import{unsafeHTML as ln}from"https://cdn.jsdelivr.net/npm/lit-html@3/directives/unsafe-html.js";import{Marked as dn}from"https://cdn.jsdelivr.net/npm/marked@13/+esm";var ze="https://tds.s-anand.net",je=n=>n&&!n.match(/^(https?|mailto):/),hn=new dn({renderer:{image(n,o,i){return je(n)&&(n=`${ze}/${n}`),`<img src="${n}" alt="${i}" ${o?`title="${o}"`:""} class="img-fluid" loading="lazy">`},link(n,o,i){return je(n)&&(n=`${ze}/${n.endsWith(".md")?`#/${n.replace(/\.md$/,"")}`:n}`),`<a href="${n}" ${o?`title="${o}"`:""} target="_blank">${i}</a>`}}}),q=n=>ln(hn.parse(n));async function _i(n,o){let i=[{...await Promise.resolve().then(()=>(tt(),et)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [How does Reciprocal Rank Fusion (RRF) combine sparse and dense search results?](#askai)
- [How do k1 and b parameters affect BM25 scoring?](#askai)
- [What is the difference between sentence, paragraph, and fixed-character chunking?](#askai)
        `)]},{...await Promise.resolve().then(()=>(rt(),it)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [How are faithfulness and answer relevance defined in RAGAS?](#askai)
- [What is the difference between context recall and context precision?](#askai)
- [How do I compute the Average Precision at k (AP@k) for retrieved contexts?](#askai)
        `)]},{...await Promise.resolve().then(()=>(st(),at)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [How can I implement an anti-hallucination guardrail for an LLM?](#askai)
- [How do I structure a grounded QA prompt that enforces citation of chunk IDs?](#askai)
- [How do I return a calibrated confidence score for unanswerable questions?](#askai)
        `)]},{...await Promise.resolve().then(()=>(ht(),dt)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [What is two-stage retrieval and why is it used in production RAG?](#askai)
- [How do I implement metadata filtering on a vector database?](#askai)
- [How do I combine cosine similarity and cross-encoder re-ranking?](#askai)
        `)]},{...await Promise.resolve().then(()=>(mt(),ut)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [What is GraphRAG and how does it improve over standard vector RAG?](#askai)
- [How do I perform entity and relationship extraction using LLMs?](#askai)
- [How do I implement multi-hop reasoning over a knowledge graph?](#askai)
        `)]},{...await Promise.resolve().then(()=>(vt(),xt)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [What is late chunking and why can it improve retrieval quality?](#askai)
- [How does contextual retrieval add document metadata to chunks?](#askai)
- [How do I implement BM25 with k1 and b from scratch?](#askai)
        `)]},{...await Promise.resolve().then(()=>(It(),At)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [How does a semantic cache reduce latency and token cost in RAG?](#askai)
- [What filters are needed to avoid unsafe cache hits across tenants?](#askai)
- [How can query expansion improve recall without changing the user's intent?](#askai)
        `)]},{...await Promise.resolve().then(()=>(Rt(),Ot)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [Why do multimodal embedding spaces need calibration?](#askai)
- [How do I combine text and image cosine similarities in one ranking score?](#askai)
- [What is modality bias and how can a centroid delta correction help?](#askai)
        `)]},{...await Promise.resolve().then(()=>(jt(),zt)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [What is HyDE (Hypothetical Document Embeddings) and why does it help vague queries?](#askai)
- [How do I blend a raw query embedding with a hypothetical-answer embedding?](#askai)
- [Why does averaging multiple hypothetical answer embeddings reduce noise?](#askai)
        `)]},{...await Promise.resolve().then(()=>(Bt(),Ft)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [How does an IVF (Inverted File) approximate nearest neighbor index work?](#askai)
- [Why does a smaller nprobe reduce latency but hurt recall?](#askai)
- [How do I assign vectors to their nearest centroid efficiently?](#askai)
        `)]},{...await Promise.resolve().then(()=>(Qt(),Vt)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [Why is embedding similarity alone unsafe for deduplicating documents?](#askai)
- [How do I implement union-find to merge near-duplicate records?](#askai)
- [How can a numeric-fact guardrail prevent merging records with conflicting facts?](#askai)
        `)]},{...await Promise.resolve().then(()=>(Xt(),Yt)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [What is the "lost in the middle" problem in long-context LLMs?](#askai)
- [How do I select retrieved chunks under a token budget without an expensive knapsack solver?](#askai)
- [How does a serpentine (outside-in) ordering combat lost-in-the-middle?](#askai)
        `)]},{...await Promise.resolve().then(()=>(en(),Kt)).then(s=>s.default({user:n,weight:2})),help:[q(`
### Ask AI
- [How does Reciprocal Rank Fusion combine sparse and dense search rankings?](#askai)
- [How do I hand-calculate RRF scores with k = 60?](#askai)
- [Why does a deterministic tie-break rule matter in ranked retrieval evaluation?](#askai)
        `)]}];return Te(i,o),Object.fromEntries(i.map(({id:s,...m})=>[s,m]))}export{_i as questions};
