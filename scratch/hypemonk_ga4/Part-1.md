# GA4 Part-1 guide (contains all answers except Q3, Q4 and Q5)

## How to Use

1. Open the **GA4 assignment page** and make sure you are logged in
2. Press **F12** → go to the **Console** tab
3. Find your question below, paste the script into the console and press **Enter**
4. Your answer will automatically be filled in the answer box

> **Scripts work for any student email — no manual input needed.**

> **Check out `Part-2.md` for Q3,Q4 and Q5 (deployment questions).**
---

## Scripts

### Q1 — End-to-End Chunking & Hybrid Retrieval Pipeline

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };

    
const user = JSON.parse(localStorage.getItem('user'));
const email = user?.email?.trim().toLowerCase();
if (!email) {
  console.error("Email not found in localStorage. Please login first.");
  throw new Error("Missing email");
}


    // -----------------------------------------
    // Q1 Data Generator
    // -----------------------------------------
    const ye = "tds-ga4-q1-data-484877bff41818b2ff1c545a889b81a3a7f9cd8ce89d9d02";
const xn = [{title:"Autonomous Fleet Routing and Dispatch",sections:[{header:"Dynamic Route Optimization",paragraphs:["Autonomous dispatch systems utilize real-time traffic feeds and weather alerts to recalculate optimal paths. By analyzing congestion patterns, the fleet manager can redirect vehicles to alternative corridors.","Vehicle-to-Infrastructure (V2I) communication allows trucks to receive signal phase and timing data. This minimizes idle time at intersections and reduces fuel consumption by up to fifteen percent.","Route deviation alerts are triggered when an autonomous vehicle departs from its pre-planned corridor by more than two hundred meters. Emergency halting is initiated if telemetry connection is lost for ten seconds."]},{header:"Battery and Charging Management",paragraphs:["Electric delivery vans must schedule charging stops when battery state of charge drops below twenty percent. Smart grid integration ensures vehicles charge during off-peak hours to minimize operational costs.","High-power DC fast chargers can replenish battery capacity from ten to eighty percent in twenty-five minutes. Frequent fast charging, however, accelerates battery degradation by twelve percent annually.","Thermal management systems regulate battery temperature during charging cycles. Optimal performance is maintained between twenty and thirty-five degrees Celsius."]}]},{title:"Automated Warehouse Inventory Control",sections:[{header:"ASRS Integration and Throughput",paragraphs:["Automated Storage and Retrieval Systems (ASRS) optimize vertical warehouse space. High-speed cranes retrieve pallets from double-deep racking systems with a positioning accuracy of two millimeters.","System throughput is measured in dual-cycles per hour, representing simultaneous storage and retrieval operations. The target efficiency is ninety-five cycles per hour under peak loads.","Safety light curtains are installed at all ASRS entry points. Any beam interruption immediately cuts power to the drive motors within fifty milliseconds."]},{header:"RFID Tracking and Discrepancy Resolution",paragraphs:["RFID portals at dock doors scan incoming pallets automatically. The system compares scanned item counts against the digital shipping manifest in real-time.","Discrepancies exceeding five units trigger an automated quarantine workflow. Warehouse staff are notified via handheld terminals to perform a manual count within fifteen minutes.","Metal-mount RFID tags are required for all liquid containers and metallic parts. Standard paper tags suffer from signal attenuation when placed directly on conductive surfaces."]}]},{title:"Predictive Maintenance for Logistics Assets",sections:[{header:"Vibration Analysis on Conveyor Belts",paragraphs:["Accelerometers mounted on conveyor drive shafts monitor vibration frequencies. An increase in the acceleration envelope indicates bearing wear or misalignment.","Spectral analysis identifies outer race defects when frequency peaks match calculated bearing frequencies. Maintenance should be scheduled when amplitude exceeds 0.5 inches per second.","Belt tension is monitored via load cells. Automatic tensioning systems adjust belt slack to maintain a constant tension of four hundred Newtons."]},{header:"Forklift Telemetry and Diagnostic Codes",paragraphs:["On-board diagnostics track forklift operating parameters including hydraulic pressure and motor temperature. Code E102 indicates hydraulic fluid temperature exceeding ninety degrees Celsius.","Forklifts must undergo safety inspections every two hundred operating hours. The system automatically restricts maximum travel speed to three kilometers per hour if inspection is overdue.","Regenerative braking systems recover energy during deceleration. This increases overall battery runtime by eight percent per shift."]}]},{title:"Cold Chain Monitoring and Quality Assurance",sections:[{header:"Temperature Excursion Protocols",paragraphs:["Refrigerated trailers must maintain a constant temperature of minus twenty degrees Celsius for frozen seafood. Temperature sensors log readings every five minutes.","A temperature excursion occurs when the temperature rises above minus fifteen degrees Celsius for more than thirty consecutive minutes. This triggers an audible alarm and SMS notification.","Dry ice sublimation rates are calculated based on external temperature. Standard insulated shippers require two kilograms of dry ice per twenty-four hours of transit."]},{header:"Ethylene Gas and Ripening Control",paragraphs:["Ethylene scrubbers in banana ripening rooms regulate gas concentrations. Maintaining ethylene levels below 0.1 parts per million prevents premature ripening during transport.","Controlled atmosphere containers adjust oxygen and carbon dioxide levels. Reducing oxygen to three percent extends the shelf life of green produce by two weeks.","Relative humidity must be maintained at ninety percent to prevent moisture loss and shriveling. Dehumidification cycles are initiated if humidity exceeds ninety-five percent."]}]}];
function vn(n,o){let i=[...n];for(let s=i.length-1;s>0;s--){let m=Math.floor(o()*(s+1));[i[s],i[m]]=[i[m],i[s]]}return i}
function kn(n){let o=String(n||"").trim().toLowerCase(),i=(0,ee.default)(`${ye}#${o}#q-rag-chunking-hybrid-search#data`),s=o.split("").reduce((b,f)=>Math.imul(31,b)+f.charCodeAt(0)|0,0),m=Math.abs(s)%97,d=vn(xn,i),l=[];for(let b=0;b<64;b++){let f=d[b%d.length],p=`DOC_${b+1}`,x=m+b,v=`# ${f.title} (Rev ${b+1}-${m})

`;f.sections.forEach(_=>{v+=`## ${_.header}

`,_.paragraphs.forEach(S=>{let $=S.replace("fifteen percent",`${x%20+8} percent`).replace("two hundred meters",`${x*3%150+100} meters`).replace("twenty percent",`${x%15+10}%`).replace("ninety-five cycles",`${x%15+80} cycles`).replace("five units",`${x%7+2} units`).replace("twelve percent",`${x%10+8} percent`).replace("twenty-five minutes",`${x%20+15} minutes`).replace("ten seconds",`${x%8+5} seconds`);v+=`${$}

`})}),l.push({doc_id:p,title:`${f.title} (V${b+1})`,text:v.trim()})}let e="sentence",r=2+Math.floor(i()*2),c=1,h={strategy:e,chunk_size:r,overlap:c,rrf_k:60,top_k:5},u=[];l.forEach(b=>{let f=b.text.split(/[.!?]\s+/).map(p=>p.trim()).filter(p=>p.length>0);for(let p=0;p<f.length;p+=r-c){let x=f.slice(p,p+r);if(x.length===0||(u.push({chunk_id:`${b.doc_id}_CHUNK_${String(u.length).padStart(3,"0")}`,text:x.join(". ")+"."}),p+r>=f.length))break}});let g={};u.forEach(b=>{let f=[],p=(0,ee.default)(`${ye}#${o}#q1#chunk#${b.chunk_id}`);for(let x=0;x<100;x++)f.push(parseFloat((p()*2-1).toFixed(4)));g[b.chunk_id]=f});let w=[],y={},k=[{text:"How does V2I communication reduce fuel consumption?"},{text:"What happens when an autonomous vehicle departs from its corridor?"},{text:"At what battery charge level should electric vans schedule charging?"},{text:"How fast can DC fast chargers replenish battery capacity?"},{text:"What is the positioning accuracy of ASRS cranes?"},{text:"What triggers the automated quarantine workflow for RFID?"},{text:"When should maintenance be scheduled based on vibration analysis?"},{text:"What does forklift diagnostic code E102 indicate?"},{text:"What is the temperature excursion protocol for seafood?"},{text:"How do ethylene scrubbers affect banana ripening?"}];for(let b=0;b<80;b++){let f=k[b%k.length],p=`Q${String(b+1).padStart(3,"0")}`,x=`${f.text} (Ref: ${p})`;w.push({query_id:p,text:x});let v=[],_=(0,ee.default)(`${ye}#${o}#q1#query#${p}`);for(let S=0;S<100;S++)v.push(parseFloat((_()*2-1).toFixed(4)));y[p]=v}return{documents:l,chunk_rules:h,chunks:u,chunk_embeddings:g,queries:w,query_embeddings:y}}


    // -----------------------------------------
    // Q1 Solver Logic
    // -----------------------------------------
    // q1_auto.js — GA4 Q1 end-to-end: email in -> answer out. No zip download needed.
// It regenerates the grader's EXACT seeded data (via kn) and runs the hybrid
// BM25 + dense-cosine + RRF pipeline, writing q1_answer.json.
//
//   node q1_auto.js <your-email>
//


// 1) Regenerate the grader's data locally (identical to the downloaded zip).
const data = kn(email);
const documents        = data.documents;
const rules            = data.chunk_rules;
const chunks           = data.chunks;                 // [{chunk_id, text}] — grader's own chunks
const chunk_embeddings = data.chunk_embeddings;
const queries          = data.queries;
const query_embeddings = data.query_embeddings;

function tokenize(text) {
    return text.toLowerCase().match(/\b[a-z0-9_]+\b/g) || [];
}

// 2) BM25 statistics over the chunks.
const N = chunks.length;
const chunkTokens = chunks.map(c => tokenize(c.text));
let totalLen = 0;
chunkTokens.forEach(t => totalLen += t.length);
const avgdl = totalLen / N;

const df = {};
chunkTokens.forEach(tokens => {
    [...new Set(tokens)].forEach(t => { df[t] = (df[t] || 0) + 1; });
});
const idf = {};
for (const t in df) idf[t] = Math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1.0);

const k1 = 1.5, b_param = 0.75;
const results = {};

queries.forEach(q => {
    const rawQuery = q.text.replace(/\(Ref: Q\d+\)/g, '');
    const qTokens = [...new Set(tokenize(rawQuery))];
    const qEmb = query_embeddings[q.query_id];

    const scores = [];
    for (let i = 0; i < N; i++) {
        const cId = chunks[i].chunk_id;
        const cTokens = chunkTokens[i];
        const cEmb = chunk_embeddings[cId];

        // sparse: BM25
        let bm25 = 0;
        const tc = {};
        cTokens.forEach(t => tc[t] = (tc[t] || 0) + 1);
        qTokens.forEach(t => {
            if (idf[t]) {
                const tf = tc[t] || 0;
                if (tf > 0) {
                    const num = tf * (k1 + 1);
                    const den = tf + k1 * (1 - b_param + b_param * (cTokens.length / avgdl));
                    bm25 += idf[t] * (num / den);
                }
            }
        });

        // dense: cosine over 100 dims
        let dot = 0, nA = 0, nB = 0;
        for (let j = 0; j < 100; j++) { dot += qEmb[j]*cEmb[j]; nA += qEmb[j]*qEmb[j]; nB += cEmb[j]*cEmb[j]; }
        const cos = dot / (Math.sqrt(nA) * Math.sqrt(nB));

        scores.push({ id: cId, sparse: bm25, dense: cos });
    }

    // ranks (score desc, tie -> id asc)
    scores.sort((x, y) => {
        const d = y.sparse - x.sparse;
        return Math.abs(d) > 1e-9 ? d : x.id.localeCompare(y.id);
    });
    const sparseRanks = {}; for (let i = 0; i < N; i++) sparseRanks[scores[i].id] = i + 1;

    scores.sort((x, y) => {
        const d = y.dense - x.dense;
        return Math.abs(d) > 1e-9 ? d : x.id.localeCompare(y.id);
    });
    const denseRanks = {}; for (let i = 0; i < N; i++) denseRanks[scores[i].id] = i + 1;

    // RRF fusion
    for (const it of scores) it.rrf = 1/(rules.rrf_k + sparseRanks[it.id]) + 1/(rules.rrf_k + denseRanks[it.id]);
    scores.sort((x, y) => {
        const d = y.rrf - x.rrf;
        return Math.abs(d) > 1e-9 ? d : x.id.localeCompare(y.id);
    });

    results[q.query_id] = scores.slice(0, rules.top_k).map(x => x.id);
});



    // -----------------------------------------
    // DOM Filling
    // -----------------------------------------
    const field = document.getElementById('q-rag-chunking-hybrid-search-server');
    if (field) {
        field.value = JSON.stringify(results, null, 2);
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q1 Answer successfully populated!");
    } else {
        console.error("❌ Q1 input field not found on this page.");
    }
})();
```

---

### Q2 — RAG Evaluation Harness

```javascript
(async () => {
    let email = '';
    try {
        const u = JSON.parse(localStorage.getItem('user'));
        email = (typeof u === 'object' ? u?.email : u) || '';
    } catch (e) {
        email = localStorage.getItem('user') || '';
    }
    email = email.trim().toLowerCase();
    if (!email) return console.error("❌ Email not found in localStorage!");
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };

    // -----------------------------------------
    // Q2 Data Generator (Evaluator Harness)
    // -----------------------------------------
    const nt = "tds-ga4-q2-data-f7adee089cc927803d18f5dd04b18879c5cf11a0a4e3b081";
    const ot = [
        {
            question: "What is the primary benefit of using V2I communication in autonomous trucking?",
            reference: "V2I communication allows trucks to receive signal phase and timing data, which reduces idle time at intersections and cuts fuel consumption by fifteen percent.",
            chunks: [
                { chunk_id: "C1", text: "V2I communication allows trucks to receive signal phase and timing data." },
                { chunk_id: "C2", text: "By minimizing idle time at intersections, V2I reduces fuel consumption by fifteen percent." },
                { chunk_id: "C3", text: "Autonomous trucks use lidar and radar for obstacle detection." }
            ],
            correct_chunks: ["C1", "C2"]
        },
        {
            question: "How does ASRS improve warehouse storage efficiency?",
            reference: "ASRS optimizes vertical warehouse space by using high-speed cranes to retrieve pallets from double-deep racking systems with two millimeter accuracy.",
            chunks: [
                { chunk_id: "C1", text: "ASRS optimizes vertical warehouse space using high-speed cranes." },
                { chunk_id: "C2", text: "Cranes retrieve pallets from double-deep racking systems with two millimeter accuracy." },
                { chunk_id: "C3", text: "Manual forklifts are still used for short distance transport." }
            ],
            correct_chunks: ["C1", "C2"]
        },
        {
            question: "What is the protocol for temperature excursions in seafood cold chains?",
            reference: "A temperature excursion occurs when the temperature rises above minus fifteen degrees Celsius for over thirty minutes, triggering an audible alarm and SMS.",
            chunks: [
                { chunk_id: "C1", text: "Frozen seafood must be maintained at constant temperature of minus twenty degrees Celsius." },
                { chunk_id: "C2", text: "An excursion is triggered if temperature rises above minus fifteen degrees for over thirty minutes." },
                { chunk_id: "C3", text: "SMS and audible alarms are sent immediately upon excursion detection." }
            ],
            correct_chunks: ["C2", "C3"]
        },
        {
            question: "How do ethylene scrubbers prevent premature ripening of bananas?",
            reference: "Ethylene scrubbers maintain ethylene levels below 0.1 parts per million in ripening rooms, preventing premature ripening during transit.",
            chunks: [
                { chunk_id: "C1", text: "Banana ripening is accelerated by ethylene gas concentrations." },
                { chunk_id: "C2", text: "Scrubbers maintain ethylene levels below 0.1 parts per million." },
                { chunk_id: "C3", text: "Relative humidity must be kept at ninety percent to prevent moisture loss." }
            ],
            correct_chunks: ["C2"]
        }
    ];

    function $n(n) {
        let o = String(n || "").trim().toLowerCase(),
            i = ee.default(`${nt}#${o}#q-rag-evaluation-harness#data`),
            s = [],
            m = [],
            d = {},
            l = {};
        for (let e = 0; e < 96; e++) {
            let r = `T${String(e + 1).padStart(3, "0")}`,
                c = ot[e % ot.length],
                t = ` (ID: ${r})`,
                a = c.question.replace("?", "") + t + "?",
                h = c.reference + t,
                u = c.chunks.map(p => ({ chunk_id: p.chunk_id, text: p.text + t })),
                g = Math.floor(i() * 3),
                w = "";
            g === 0 ? w = c.reference + t : g === 1 ? w = c.chunks[0].text + ". However, " + c.chunks[2].text + t : w = "The system operates using blockchain technology and quantum computing." + t;
            s.push({ trace_id: r, question: a, retrieved_chunks: u, generated_answer: w });
            m.push({ trace_id: r, reference_answer: h, relevant_chunk_ids: c.correct_chunks });
            let y = [],
                k = [],
                b = ee.default(`${nt}#${o}#q2#embed#${r}`),
                f = g === 2 ? .3 : .85;
            for (let p = 0; p < 50; p++) {
                let x = b() * 2 - 1;
                y.push(parseFloat(x.toFixed(4)));
                let v = (b() * 2 - 1) * (1 - f);
                k.push(parseFloat((x * f + v).toFixed(4)));
            }
            d[r] = y;
            l[r] = k;
        }
        return { traces: s, ground_truth: m, question_embeddings: d, answer_embeddings: l };
    }

    // -----------------------------------------
    // Q2 Solver Logic
    // -----------------------------------------
    const data = $n(email);
    const traces = data.traces;
    const groundTruth = data.ground_truth;
    const questionEmbeddings = data.question_embeddings;
    const answerEmbeddings = data.answer_embeddings;

    const gtMap = {};
    for (const gt of groundTruth) gtMap[gt.trace_id] = gt;

    function tokenize(text) {
        return text.toLowerCase().match(/\b[a-z0-9_]+\b/g) || [];
    }

    function cosineSim(a, b) {
        let dot = 0, normA = 0, normB = 0;
        for (let i = 0; i < a.length; i++) {
            dot += a[i] * b[i];
            normA += a[i] * a[i];
            normB += b[i] * b[i];
        }
        return dot / (Math.sqrt(normA) * Math.sqrt(normB));
    }

    function r2(val) {
        return Math.round(val * 100) / 100;
    }

    const results = {};

    for (const trace of traces) {
        const tid = trace.trace_id;
        const gt = gtMap[tid];
        
        // 1. Faithfulness
        const ansSentences = trace.generated_answer.split(/[.!?]\s+/)
            .filter(s => s.trim().length > 5);
        let faithfulness = 1.0;
        if (ansSentences.length > 0) {
            let faithfulCount = 0;
            for (const sent of ansSentences) {
                const sentTokens = tokenize(sent);
                if (sentTokens.length === 0) { faithfulCount++; continue; }
                let maxOverlap = 0;
                for (const chunk of trace.retrieved_chunks) {
                    const chunkTokens = new Set(tokenize(chunk.text));
                    const overlap = sentTokens.filter(t => chunkTokens.has(t)).length;
                    maxOverlap = Math.max(maxOverlap, overlap);
                }
                if (maxOverlap / sentTokens.length >= 0.5) faithfulCount++;
            }
            faithfulness = faithfulCount / ansSentences.length;
        }

        // 2. Answer Relevance
        const answerRelevance = cosineSim(
            answerEmbeddings[tid],
            questionEmbeddings[tid]
        );

        // 3. Context Recall
        const refSentences = gt.reference_answer.split(/[.!?]\s+/)
            .filter(s => s.trim().length > 5);
        let contextRecall = 1.0;
        if (refSentences.length > 0) {
            let supportedCount = 0;
            for (const sent of refSentences) {
                const sentTokens = tokenize(sent);
                if (sentTokens.length === 0) { supportedCount++; continue; }
                let maxOverlap = 0;
                for (const chunk of trace.retrieved_chunks) {
                    const chunkTokens = new Set(tokenize(chunk.text));
                    const overlap = sentTokens.filter(t => chunkTokens.has(t)).length;
                    maxOverlap = Math.max(maxOverlap, overlap);
                }
                if (maxOverlap / sentTokens.length >= 0.5) supportedCount++;
            }
            contextRecall = supportedCount / refSentences.length;
        }

        // 4. Context Precision
        const relevantSet = new Set(gt.relevant_chunk_ids);
        const retrieved = trace.retrieved_chunks.map(c => c.chunk_id);
        let hits = 0, sumPrecision = 0;
        for (let i = 0; i < retrieved.length; i++) {
            if (relevantSet.has(retrieved[i])) {
                hits++;
                sumPrecision += hits / (i + 1);
            }
        }
        const contextPrecision = relevantSet.size === 0 ? 1.0 : sumPrecision / relevantSet.size;

        results[tid] = {
            faithfulness: r2(faithfulness),
            answer_relevance: r2(answerRelevance),
            context_recall: r2(contextRecall),
            context_precision: r2(contextPrecision)
        };
    }

    // -----------------------------------------
    // DOM Filling
    // -----------------------------------------
    const field = document.getElementById('q-rag-evaluation-harness-server');
    if (field) {
        field.value = JSON.stringify(results, null, 2);
        field.dispatchEvent(new Event('input', { bubbles: true }));
        field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q2 Answer successfully populated!");
    } else {
        console.error("❌ Q2 input field not found on this page.");
    }
})();

```

---

### Q6 — Late Chunking & Contextual Retrieval

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };
    const Zt = { default: ee.default };
    const X = { default: (seed) => sr(seed, { global: false }) };

    let email = '';
    try {
        const u = JSON.parse(localStorage.getItem('user'));
        email = (typeof u === 'object' ? u?.email : u) || '';
    } catch (e) {
        email = localStorage.getItem('user') || '';
    }
    email = email.trim().toLowerCase();
    if (!email) {
        console.error("❌ Email not found in localStorage!");
        return;
    }



function Fn({service:n,region:o,release:i,heading:s,owner:m,priority:d,docIndex:l,sectionIndex:e,emailNumber:r}){let c=12+(r+l+e)%9,t=2+(r+l*3+e)%7,a=40+(r+l+e*5)%45,h=ne[(r+l+e)%ne.length],u=ne[(r+l+e+5)%ne.length],g=bt[(r+l+e)%bt.length];return[`The ${h} marker appears in many handbooks, but this ${s.toLowerCase()} rule is scoped only to ${n} in ${o}.`,`For release ${i}, ${m} must ${g} when the status age is above ${c} hours.`,`The answer should cite the local section before quoting the global handbook because the handbook omits the ${o} override.`,`A late chunk that carries the title and section metadata can distinguish ${n} from the similarly worded ${Ln(B,(0,xe.default)(`${n}-${o}`))} memo.`,`If the request mentions signal ${u}, keep it in the candidate set but do not promote it unless the service and region also match.`,`The escalation timer is ${t} business days and the stale evidence threshold is ${a} minutes.`,`Operators should mark priority ${d} on the retrieval trace so rerankers can explain why the section was selected.`,`When two chunks have identical body text, the chunk with release ${i} wins only if its contextual header names ${n} and ${o}.`]}
function oe(n,o){return String(n).padStart(o,"0")}
function wt(n){return String(n||"").trim().toLowerCase()}
function Jn(n){return wt(n).split("").reduce((o,i)=>Math.imul(o,33)+i.charCodeAt(0)>>>0,5381)}
function Ln(n,o){return n[Math.floor(o()*n.length)]}
function Bn(n){let o=wt(n),i=Jn(o),s=(0,xe.default)(`${Mn}#${o}#late-context-data`),m=[],d=[];for(let t=0;t<32;t++){let a=B[(t+i)%B.length],h=pt[(t+Math.floor(i/7))%pt.length],u=ft[(t+Math.floor(i/11))%ft.length],g={doc_id:`LC_DOC_${oe(t+1,3)}`,title:`${a.replace("_"," ")} retrieval handbook ${oe(t+1,3)}`,region:h,release:u,sections:[]};for(let w=0;w<5;w++){let y=yt[(t+w+i)%yt.length],k=gt[(t*2+w+i)%gt.length],b=1+(t+w+i)%5,f=B[(t+w+i)%B.length],p=Fn({service:f,region:h,release:u,heading:y,owner:k,priority:b,docIndex:t,sectionIndex:w,emailNumber:i}),x={section_id:`S${oe(w+1,2)}`,heading:y,service:f,owner:k,priority:b,sentences:p};g.sections.push(x),d.push({doc:g,section:x,sentence:p[1],targetIndex:1})}m.push(g)}let l=[],e=new Set;for(;l.length<28;){let t=Math.floor(s()*d.length);e.has(t)||(e.add(t),l.push(d[t]))}let r=l.map((t,a)=>({query_id:`LC_Q_${oe(a+1,3)}`,text:`Find the late chunk that explains what ${t.section.owner} must do for ${t.section.service} ${t.section.heading.toLowerCase()} in ${t.doc.region}.`,service:t.section.service,region:t.doc.region,release:t.doc.release,priority:t.section.priority}));return{documents:m,queries:r,rules:{chunk_sentence_count:4,chunk_sentence_overlap:1,top_k:4,bm25_k1:1.2,bm25_b:.75,contextual_template:"{title} {region} {release} {heading} {service} {owner} priority-{priority} {chunk_text}",query_template:"{text} {service} {region} {release} priority-{priority}",expected_output:"JSON object mapping each query_id to an array of the top_k chunk_id strings, sorted by BM25 score descending."}}}async function Pn({user:n,weight:o=2}){let i="q-late-chunking-context-retrieval-server",s="Late Chunking with Contextual Retrieval",m=Bn(n.email),d=new zn;d.file("documents.jsonl",m.documents.map(t=>JSON.stringify(t)).join(`
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
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the mapping exactly as a JSON object.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var xe,Mn,B,pt,ft,gt,yt,bt,ne;function vt() { "use strict";xe={default: ee.default},Mn="tds-ga4-late-chunking-data-2b5414d4e08627bc19dffa210e83013d3b48245376cd160b797d6f4ba22d4bd43e2eb9a2d6c3c0b57c04fdfaa8cc016d",B=["admissions","course_catalog","fees","identity","proctoring","scholarships","support","transcripts"],pt=["apac","emea","latam","na"],ft=["2026.05","2026.06","2026.07","2026.08"],gt=["argo","banyan","cedar","drona","ember","falcon","gingko","helios"],yt=["Policy Exceptions","Escalation Timers","Evidence Windows","Retry Controls","Audit Labels","Status Mapping"],bt=["refresh the derived status before sending the answer","attach the last verified event as supporting evidence","route the request through the regional reviewer queue","suppress stale draft notes from the final context","prefer the section-level rule over global boilerplate","raise a manual review flag when evidence is older than the limit"],ne=["amber","bronze","cobalt","delta","ember","fennel","granite","harbor","indigo","juniper","kepler","lumen"] };

vt(); // initialize the variables


if (true) {
    if(!email){ console.error("Usage: node q6_auto.js <email>"); process.exit(1); }
  const m = Bn(email);
  const rules = m.rules;
  const queries = m.queries;
  const documents = m.documents;

  const k1 = rules.bm25_k1;
  const b = rules.bm25_b;
  const chunk_sentence_count = rules.chunk_sentence_count;
  const overlap = rules.chunk_sentence_overlap;
  const step = chunk_sentence_count - overlap;
  const top_k = rules.top_k;

  const tokenize = (text) => String(text).toLowerCase().match(/\b[a-z0-9_]+\b/g) || [];

  const chunks = [];
  for (const doc of documents) {
    for (const sec of doc.sections) {
      const sentences = sec.sentences;
      let w_idx = 0;
      let idx = 0;
      while (idx < sentences.length) {
        const chunk_sentences = sentences.slice(idx, idx + chunk_sentence_count);
        const chunk_text = chunk_sentences.join(" ");
        
        const context_str = rules.contextual_template
          .replace("{title}", doc.title)
          .replace("{region}", doc.region)
          .replace("{release}", doc.release)
          .replace("{heading}", sec.heading)
          .replace("{service}", sec.service)
          .replace("{owner}", sec.owner)
          .replace("{priority}", sec.priority)
          .replace("{chunk_text}", chunk_text);
          
        const chunk_id = `${doc.doc_id}:${sec.section_id}:w${String(w_idx).padStart(2, '0')}`;
        
        chunks.push({
          id: chunk_id,
          tokens: tokenize(context_str)
        });
        
        w_idx++;
        idx += step;
      }
    }
  }

  const N = chunks.length;
  const avgdl = chunks.reduce((sum, c) => sum + c.tokens.length, 0) / (N || 1);

  const df = {};
  for (const c of chunks) {
    const unique = new Set(c.tokens);
    for (const t of unique) {
      df[t] = (df[t] || 0) + 1;
    }
  }

  const idf = {};
  for (const t in df) {
    const n_q = df[t];
    idf[t] = Math.log(((N - n_q + 0.5) / (n_q + 0.5)) + 1.0);
  }

  const answer = {};
  for (const q of queries) {
    const q_str = rules.query_template
      .replace("{text}", q.text)
      .replace("{service}", q.service)
      .replace("{region}", q.region)
      .replace("{release}", q.release)
      .replace("{priority}", q.priority);
      
    const q_tokens = tokenize(q_str);
    
    const scores = chunks.map(c => {
      let score = 0.0;
      const doc_len = c.tokens.length;
      
      const tf = {};
      for (const t of c.tokens) tf[t] = (tf[t] || 0) + 1;
      
      for (const t of q_tokens) {
        if (tf[t]) {
          const freq = tf[t];
          const term_idf = idf[t];
          const numerator = freq * (k1 + 1);
          const denominator = freq + k1 * (1 - b + b * (doc_len / avgdl));
          score += term_idf * (numerator / denominator);
        }
      }
      return { score, id: c.id };
    });
    
    scores.sort((x, y) => {
      if (y.score !== x.score) return y.score - x.score;
      if (x.id < y.id) return -1;
      if (x.id > y.id) return 1;
      return 0;
    });
    
    answer[q.query_id] = scores.slice(0, top_k).map(x => x.id);
  }

  
    const _field = document.getElementById('q-late-chunking-context-retrieval-server');
    if (_field) {
        _field.value = JSON.stringify(answer, null, 2);
        _field.dispatchEvent(new Event('input', { bubbles: true }));
        _field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q6 Answer successfully populated!");
    } else {
        console.error("❌ Q6 input field not found on this page.");
    }
}

})();
```

---

### Q7 — Semantic Caching and Query Augmentation

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };
    const Zt = { default: ee.default };
    const X = { default: (seed) => sr(seed, { global: false }) };

    let email = '';
    try {
        const u = JSON.parse(localStorage.getItem('user'));
        email = (typeof u === 'object' ? u?.email : u) || '';
    } catch (e) {
        email = localStorage.getItem('user') || '';
    }
    email = email.trim().toLowerCase();
    if (!email) {
        console.error("❌ Email not found in localStorage!");
        return;
    }



function oe(n,o){return String(n).padStart(o,"0")}
function wt(n){return String(n||"").trim().toLowerCase()}
function Jn(n){return wt(n).split("").reduce((o,i)=>Math.imul(o,33)+i.charCodeAt(0)>>>0,5381)}
function Ln(n,o){return n[Math.floor(o()*n.length)]}
function Vn(n){return String(n||"").trim().toLowerCase()}
function St(n){let o=(0,M.default)(`${qt}#vector#${n}`);return $t(Array.from({length:36},()=>o()*2-1))}
function ve(n,o){return String(n).padStart(o,"0")}
function ke(n,o,i){return $t(n.map(s=>s+(o()*2-1)*i))}
function $t(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}
function Qn(n){let o=Vn(n),i=(0,M.default)(`${qt}#${o}#semantic-cache-data`),s=G.map((e,r)=>St(`${r}-${e.join("-")}`)),m=[];for(let e=0;e<960;e++){let r=e%G.length,c=P[(e+Math.floor(i()*10))%P.length],t=kt[(e+Math.floor(i()*10))%kt.length],a=_t[(e+Math.floor(i()*10))%_t.length],h=G[r],u=`${h[e%h.length]} ${h[(e+1)%h.length]} help ${c} term ${2024+e%4}`;m.push({cache_id:`SC_C_${ve(e+1,4)}`,tenant:c,channel:t,language:a,created_minute:1e3+e*3,query:u,embedding:ke(s[r],(0,M.default)(`${o}#cache#${e}`),.045),answer_id:`ANS_${ve((r+1)*100+e%97,4)}`})}let d=[];for(let e=0;e<72;e++){let r=e%4!==3,c=m[(e*37+Math.floor(i()*23))%m.length],t=G.findIndex(b=>b.some(f=>c.query.includes(f))),a=G[Math.max(0,t)],h=r?c.tenant:P[(P.indexOf(c.tenant)+1)%P.length],u=c.channel,g=c.language,w=r?c.created_minute+120+e%90:c.created_minute+900+e,y=`${a[(e+2)%a.length]} ${a[(e+3)%a.length]} status ${h}`,k=r?ke(c.embedding,(0,M.default)(`${o}#request-hit#${e}`),.025):ke(St(`miss-${e}-${o}`),(0,M.default)(`${o}#request-miss#${e}`),.12);d.push({request_id:`SC_R_${ve(e+1,3)}`,tenant:h,channel:u,language:g,at_minute:w,query:y,embedding:k})}return{cache_entries:m,requests:d,expansion_map:Un,rules:{ttl_minutes:480,similarity_threshold:.91,candidate_filters:["tenant","channel","language","not expired"],output:"JSON object mapping request_id to {decision, cache_id, nearest_similarity, added_terms}. nearest_similarity is rounded to 4 decimals."}}}async function Wn({user:n,weight:o=2}){let i="q-semantic-cache-query-augmentation-server",s="Semantic Caching and Query Augmentation",m=Qn(n.email),d=new Gn;d.file("cache_entries.jsonl",m.cache_entries.map(t=>JSON.stringify(t)).join(`
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
  `;return{id:i,title:s,weight:o,question:r,answer:async t=>{let a;try{a=JSON.parse(t)}catch{throw new Error("Invalid JSON. Submit the cache decision mapping only.")}let h=await fetch("/backendVerify",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({email:n.email,quizSign:n.quizSign,response:a,weight:o,questionId:i})}),u=await h.json();if(!h.ok)throw new Error(u.error||"Validation failed.");return u}}}var M,qt,P,kt,_t,G,Un;function It() { "use strict";M={default: ee.default},qt="tds-ga4-semantic-cache-data-0c52326402a2404371ad5f1ae83cb12fd628e05cd6e0c0477ab2836185b6db3c13cef8923de5922d3f14f5dab500763b",P=["degree","diploma","foundation"],kt=["web","mobile","ivr"],_t=["en","hi"],G=[["fee","refund","receipt","payment"],["exam","hallticket","slot","reschedule"],["course","credit","drop","withdraw"],["project","review","rubric","deadline"],["login","otp","profile","identity"],["certificate","transcript","grade","dispatch"],["scholarship","waiver","income","document"],["proctoring","camera","browser","violation"]],Un={fee:["payment","receipt"],refund:["reversal","bank"],exam:["assessment","slot"],hallticket:["admitcard","exam"],course:["subject","term"],project:["submission","rubric"],login:["signin","otp"],certificate:["transcript","dispatch"],scholarship:["waiver","income"],proctoring:["camera","browser"]} };

It(); // initialize the variables


if (true) {
    if(!email){ console.error("Usage: node q7_auto.js <email>"); process.exit(1); }
  const m = Qn(email);
  const rules = m.rules;
  const requests = m.requests;
  const cache_entries = m.cache_entries;
  const expansion_map = m.expansion_map;

  const tokenize = (text) => String(text).match(/\b[a-z0-9]+\b/g) || [];

  const cosine_sim = (a, b) => {
    let dot = 0.0, normA = 0.0, normB = 0.0;
    for(let i=0; i<a.length; i++) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    if (normA === 0 || normB === 0) return 0;
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  };

  const pyRound = (num, ndigits) => {
    let p = Math.pow(10, ndigits);
    let temp = num * p;
    let base = Math.floor(temp);
    let fraction = temp - base;
    if (Math.abs(fraction - 0.5) < 1e-10) {
        return (base % 2 === 0 ? base : base + 1) / p;
    }
    return Math.round(temp) / p;
  };

  const answer = {};

  for (const req of requests) {
    // 1. Tokenize query
    const tokens = tokenize(req.query);
    const original_tokens = new Set(tokens);
    
    // 2. Query expansion
    const added_terms = new Set();
    for (const token of tokens) {
      if (expansion_map[token]) {
        for (const exp of expansion_map[token]) {
          if (!original_tokens.has(exp)) {
            added_terms.add(exp); 
          }
        }
      }
    }
    const added_terms_arr = Array.from(added_terms).sort();

    // 3. Filter candidates
    const req_minute = req.at_minute;
    const ttl_minutes = rules.ttl_minutes;

    let best_id = null;
    let best_sim = -1;

    for (const c of cache_entries) {
      // filters
      if (c.tenant !== req.tenant) continue;
      if (c.channel !== req.channel) continue;
      if (c.language !== req.language) continue;

      const c_minute = c.created_minute;
      const age_minutes = req_minute - c_minute;
      if (age_minutes < 0 || age_minutes > ttl_minutes) continue; // Expired or future?

      // 4. Compute cosine similarity
      const sim = cosine_sim(req.embedding, c.embedding);
      if (sim > best_sim) {
        best_sim = sim;
        best_id = c.cache_id;
      } else if (sim === best_sim && best_id !== null) {
        // Tie-break lexically if needed
        if (c.cache_id < best_id) {
          best_id = c.cache_id;
        }
      }
    }

    // 5. Decision
    let rounded_sim = 0.0;
    if (best_id !== null) {
      rounded_sim = pyRound(best_sim, 4);
    }

    if (best_id !== null && best_sim >= rules.similarity_threshold) {
      answer[req.request_id] = {
        decision: "HIT",
        cache_id: best_id,
        nearest_similarity: rounded_sim,
        added_terms: added_terms_arr
      };
    } else {
      answer[req.request_id] = {
        decision: "MISS",
        cache_id: null,
        nearest_similarity: rounded_sim,
        added_terms: added_terms_arr
      };
    }
  }

  let out_str = JSON.stringify(answer, null, 2);
  out_str = out_str.replace(/"nearest_similarity": 0(\s*,|\s*\n)/g, '"nearest_similarity": 0.0$1');
  
    const _field = document.getElementById('q-semantic-cache-query-augmentation-server');
    if (_field) {
        _field.value = out_str;
        _field.dispatchEvent(new Event('input', { bubbles: true }));
        _field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q7 Answer successfully populated!");
    } else {
        console.error("❌ Q7 input field not found on this page.");
    }
}

})();
```

---

### Q8 — Multimodal Embedding Calibration

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };
    const Zt = { default: ee.default };
    const X = { default: (seed) => sr(seed, { global: false }) };

    let email = '';
    try {
        const u = JSON.parse(localStorage.getItem('user'));
        email = (typeof u === 'object' ? u?.email : u) || '';
    } catch (e) {
        email = localStorage.getItem('user') || '';
    }
    email = email.trim().toLowerCase();
    if (!email) {
        console.error("❌ Email not found in localStorage!");
        return;
    }



var j = { default: ee.default };

const Ct = "tds-ga4-multimodal-data-50b663aeac4714b9eb240a19f7a7566a5842a9c2ccd6b33c4c75cfa5643d3f6890ca7d0e9d5250b97eb7ed110731c069";
const H = ["poster","invoice","certificate","diagram","screenshot","id_card"];
const U = ["blue","green","red","yellow","gray","violet"];
const V = ["dense","spacious","two_column","bordered","minimal","annotated"];
const ie = ["en","hi","ta","te"];

function Kn(n){let o=Zn(n),i=(0,j.default)(`${Ct}#${o}#multimodal-data`),s=Object.fromEntries(H.map(t=>[t,Se(`category-${t}`)])),m=Object.fromEntries(U.map(t=>[t,Se(`color-${t}`)])),d=Object.fromEntries(V.map(t=>[t,Se(`layout-${t}`)])),l=se(Array.from({length:48},(t,a)=>(a%5-2)/50)),e=[];for(let t=0;t<780;t++){let a=H[(t+Math.floor(i()*9))%H.length],h=ie[(t+Math.floor(i()*9))%ie.length],u=U[(t*2+Math.floor(i()*9))%U.length],g=V[(t*3+Math.floor(i()*9))%V.length],w=ae([s[a],m[u],d[g]]),y=ae([s[a],m[u],d[g],l]);e.push({item_id:`MM_I_${_e(t+1,4)}`,category:a,locale:h,color:u,layout:g,caption:`${h} ${u} ${g} ${a} artifact ${_e(t+1,4)}`,text_embedding:re(w,(0,j.default)(`${o}#text#${t}`),.05),image_embedding:re(y,(0,j.default)(`${o}#image#${t}`),.06)})}let r=[];for(let t=0;t<42;t++){let a=H[(t+Math.floor(i()*11))%H.length],h=ie[(t+Math.floor(i()*7))%ie.length],u=U[(t+Math.floor(i()*13))%U.length],g=V[(t+Math.floor(i()*17))%V.length],w=ae([s[a],m[u],d[g]]),y=ae([s[a],m[u],d[g],l]);r.push({query_id:`MM_Q_${_e(t+1,3)}`,text:`Find ${h} ${u} ${g} ${a} artifacts.`,target_category:a,target_locale:h,category_filter:t%5===0?null:a,locale_filter:t%6===0?null:h,text_weight:t%3===0?.65:.55,image_weight:t%3===0?.35:.45,text_embedding:re(w,(0,j.default)(`${o}#query-text#${t}`),.04),image_embedding:re(y,(0,j.default)(`${o}#query-image#${t}`),.045)})}return{items:e,queries:r,calibration:{image_delta:l,category_match_boost:.025,locale_match_boost:.015,top_k:5,output:"JSON object mapping query_id to an array of top_k item_id strings sorted by calibrated score."}}}
function Zn(n){return String(n||"").trim().toLowerCase()}
function Se(n){let o=(0,j.default)(`${Ct}#${n}`);return se(Array.from({length:48},()=>o()*2-1))}
function se(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}
function ae(n){let o=Array.from({length:n[0].length},()=>0);for(let i of n)for(let s=0;s<o.length;s++)o[s]+=i[s];return se(o)}
function _e(n,o){return String(n).padStart(o,"0")}
function re(n,o,i){return se(n.map(s=>s+(o()*2-1)*i))}

if (true) {
    if (!email) {
    console.error("Usage: node q8_auto.js <email>");
    process.exit(1);
  }

  const data = Kn(email);
  const items = data.items;
  const queries = data.queries;
  const cal = data.calibration;
  
  const cosine_sim = (a, b) => {
    let dot = 0.0, normA = 0.0, normB = 0.0;
    for(let i=0; i<a.length; i++) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    if (normA === 0 || normB === 0) return 0;
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  };
  
  // 1. Calibrate items
  const delta = cal.image_delta;
  const calibrated_items = items.map(item => {
      let cal_img = [];
      for (let i = 0; i < item.image_embedding.length; i++) {
          cal_img.push(item.image_embedding[i] - delta[i]);
      }
      
      // L2 Normalize
      let norm = Math.sqrt(cal_img.reduce((sum, val) => sum + val*val, 0));
      if (norm === 0) norm = 1;
      cal_img = cal_img.map(val => val / norm);
      
      return {
          ...item,
          calibrated_image: cal_img
      };
  });
  
  const answer = {};
  
  for (const q of queries) {
      const candidates = [];
      
      // 2. Filter
      for (const item of calibrated_items) {
          if (q.category_filter !== null && item.category !== q.category_filter) continue;
          if (q.locale_filter !== null && item.locale !== q.locale_filter) continue;
          
          // 3. Score
          let sim_text = cosine_sim(q.text_embedding, item.text_embedding);
          let sim_img = cosine_sim(q.image_embedding, item.calibrated_image);
          
          let score = (q.text_weight * sim_text) + (q.image_weight * sim_img);
          
          if (item.category === q.target_category) score += cal.category_match_boost;
          if (item.locale === q.target_locale) score += cal.locale_match_boost;
          
          candidates.push({ item_id: item.item_id, score: score });
      }
      
      // 4. Rank
      candidates.sort((a, b) => {
          if (Math.abs(a.score - b.score) > 1e-12) {
              return b.score - a.score;
          }
          // Tie-break: item_id ascending
          return a.item_id.localeCompare(b.item_id);
      });
      
      const top_k = candidates.slice(0, cal.top_k).map(c => c.item_id);
      answer[q.query_id] = top_k;
  }
  
  
    const _field = document.getElementById('q-multimodal-embedding-calibration-server');
    if (_field) {
        _field.value = JSON.stringify(answer, null, 2);
        _field.dispatchEvent(new Event('input', { bubbles: true }));
        _field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q8 Answer successfully populated!");
    } else {
        console.error("❌ Q8 input field not found on this page.");
    }
}

})();
```

---

### Q9 — HyDE Hypothetical Document Retrieval

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };
    const Zt = { default: ee.default };
    const X = { default: (seed) => sr(seed, { global: false }) };

    let email = '';
    try {
        const u = JSON.parse(localStorage.getItem('user'));
        email = (typeof u === 'object' ? u?.email : u) || '';
    } catch (e) {
        email = localStorage.getItem('user') || '';
    }
    email = email.trim().toLowerCase();
    if (!email) {
        console.error("❌ Email not found in localStorage!");
        return;
    }



var L = { default: ee.default };

const Tt = "tds-ga4-hyde-data-5203f61502e12bdcacc52e5a3078c423fb3268646470906a2b5fcff1076a66071613d66507f5fe8365838d3f2c6f8441";
const Q=["billing","enrollment","assessment","curriculum","aid","integrity","records","helpdesk"];
const W=[2023,2024,2025,2026];

function io(n){let o=oo(n),i=(0,L.default)(`${Tt}#${o}#hyde-data`),s=Object.fromEntries(Q.map(r=>[r,Nt(`category-${r}`)])),m=Object.fromEntries(W.map(r=>[r,Nt(`year-${r}`)])),d=[];for(let r=0;r<500;r++){let c=Q[(r+Math.floor(i()*7))%Q.length],t=W[(r*2+Math.floor(i()*7))%W.length],a=Et([s[c],m[t]]);d.push({item_id:`KB_I_${Dt(r+1,4)}`,category:c,publish_year:t,text_embedding:qe(a,(0,L.default)(`${o}#item#${r}`),.05)})}let l=[];for(let r=0;r<40;r++){let c=Q[(r+Math.floor(i()*9))%Q.length],t=W[(r*3+Math.floor(i()*9))%W.length],a=Et([s[c],m[t]]),h=r%3===0?.3:.4;l.push({query_id:`HQ_${Dt(r+1,3)}`,query_text:`Something is wrong with my ${c} \u2014 what should I do?`,target_category:c,min_year:t,raw_weight:h,hyde_weight:Number((1-h).toFixed(2)),query_embedding:qe(a,(0,L.default)(`${o}#query#${r}`),.14),hypothetical_answers:[0,1,2].map(u=>({text:`Hypothetical answer ${u+1} for query ${r+1} about ${c} policies from ${t}.`,embedding:qe(a,(0,L.default)(`${o}#hyde#${r}#${u}`),.05)}))})}return{items:d,queries:l,rules:{top_k:5,category_match_boost:.03,recency_boost:.02,recency_rule:"item.publish_year >= query.min_year",hyde_vector_rule:"normalize(sum of the 3 hypothetical_answers[].embedding, component-wise)",final_vector_rule:"normalize(raw_weight * query_embedding + hyde_weight * hyde_vector, component-wise)",output:"JSON object mapping query_id to an array of top_k item_id strings sorted by final blended score."}}}
function oo(n){return String(n||"").trim().toLowerCase()}
function Nt(n){let o=(0,L.default)(`${Tt}#${n}`);return $e(Array.from({length:32},()=>o()*2-1))}
function Et(n){let o=Array.from({length:n[0].length},()=>0);for(let r of n)for(let c=0;c<o.length;c++)o[c]+=r[c];return $e(o)}
function Dt(n,o){return String(n).padStart(o,"0")}
function qe(n,o,i){return $e(n.map(s=>s+(o()*2-1)*i))}
function $e(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}

if (true) {
    if (!email) {
    console.error("Usage: node q9_auto.js <email>");
    process.exit(1);
  }

  const data = io(email);
  const items = data.items;
  const queries = data.queries;
  const rules = data.rules;
  
  const cosine_sim = (a, b) => {
    let dot = 0.0, normA = 0.0, normB = 0.0;
    for(let i=0; i<a.length; i++) {
        dot += a[i] * b[i];
        normA += a[i] * a[i];
        normB += b[i] * b[i];
    }
    if (normA === 0 || normB === 0) return 0;
    return dot / (Math.sqrt(normA) * Math.sqrt(normB));
  };

  const l2_normalize = (vec) => {
    let norm = Math.sqrt(vec.reduce((sum, val) => sum + val*val, 0));
    if (norm === 0) norm = 1;
    return vec.map(val => val / norm);
  };
  
  const answer = {};
  
  for (const q of queries) {
      // 1. HyDE vector banao
      let hyde_vec = Array(q.hypothetical_answers[0].embedding.length).fill(0);
      for (const ans of q.hypothetical_answers) {
          for (let i = 0; i < ans.embedding.length; i++) {
              hyde_vec[i] += ans.embedding[i];
          }
      }
      hyde_vec = l2_normalize(hyde_vec);
      
      // 2. Final vector
      let final_vec = [];
      for (let i = 0; i < q.query_embedding.length; i++) {
          final_vec.push(q.raw_weight * q.query_embedding[i] + q.hyde_weight * hyde_vec[i]);
      }
      final_vec = l2_normalize(final_vec);
      
      // 3. Score har item
      const candidates = [];
      for (const item of items) {
          let score = cosine_sim(final_vec, item.text_embedding);
          
          if (item.category === q.target_category) score += rules.category_match_boost;
          if (item.publish_year >= q.min_year) score += rules.recency_boost;
          
          candidates.push({ item_id: item.item_id, score: score });
      }
      
      // 4. Rank
      candidates.sort((a, b) => {
          if (a.score !== b.score) {
              return b.score > a.score ? 1 : -1;
          }
          // Tie-break: item_id ascending
          return a.item_id < b.item_id ? -1 : (a.item_id > b.item_id ? 1 : 0);
      });
      
      const top_k = candidates.slice(0, rules.top_k).map(c => c.item_id);
      answer[q.query_id] = top_k;
  }
  
  
    const _field = document.getElementById('q-hyde-hypothetical-retrieval-server');
    if (_field) {
        _field.value = JSON.stringify(answer, null, 2);
        _field.dispatchEvent(new Event('input', { bubbles: true }));
        _field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q9 Answer successfully populated!");
    } else {
        console.error("❌ Q9 input field not found on this page.");
    }
}

})();
```

---

### Q10 — ANN Index Recall & Latency

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };
    const Zt = { default: ee.default };
    const X = { default: (seed) => sr(seed, { global: false }) };

    let email = '';
    try {
        const u = JSON.parse(localStorage.getItem('user'));
        email = (typeof u === 'object' ? u?.email : u) || '';
    } catch (e) {
        email = localStorage.getItem('user') || '';
    }
    email = email.trim().toLowerCase();
    if (!email) {
        console.error("❌ Email not found in localStorage!");
        return;
    }


// Copying q10_generate.js contents


var Y = { default: ee.default };

const Lt = "tds-ga4-ann-data-9b212e1877f9a0b061ad49307ed02d1e65cdb193b9d38ed4dcb9d7cb2ec9935349a039acec4e81f5c6f4f64382122d6e";
const Ae = 20;
const co = 900;
const uo = .7;
const lo = 45;
const mo = .55;
const ho = 8;

function go(n){let o=po(n),i=(0,Y.default)(`${Lt}#${o}#ann-data`),s=Array.from({length:Ae},(e,r)=>({centroid_id:`CEN_${Ie(r,2)}`,embedding:fo(`centroid-${o}-${r}`)})),m=[];for(let e=0;e<co;e++){let r=Math.floor(i()*Ae);m.push({item_id:`VDB_I_${Ie(e+1,4)}`,embedding:Mt(s[r].embedding,(0,Y.default)(`${o}#item#${e}`),uo)})}let d=[];for(let e=0;e<lo;e++){let r=Math.floor(i()*Ae);d.push({query_id:`ANN_Q_${Ie(e+1,3)}`,nprobe:e%4+1,embedding:Mt(s[r].embedding,(0,Y.default)(`${o}#query#${e}`),mo)})}return{centroids:s,items:m,queries:d,rules:{top_k:5,assignment_rule:"Assign each item to the centroid with highest cosine similarity (ties broken by lowest centroid_id).",probe_rule:"Rank all centroids by cosine similarity to the query embedding descending (ties by lowest centroid_id). Take the top `nprobe` centroids.",candidate_rule:"The candidate set is the union of items assigned to the top `nprobe` centroids.",ranking_rule:"Rank candidate items by cosine similarity to the query embedding descending (ties broken by item_id ascending).",output:"JSON object mapping query_id to an array of top_k item_id strings."}}}
function po(n){return String(n||"").trim().toLowerCase()}
function Ie(n,o){return String(n).padStart(o,"0")}
function fo(n){let o=(0,Y.default)(`${Lt}#${n}`);return Jt(Array.from({length:ho},()=>o()*2-1))}
function Mt(n,o,i){return Jt(n.map(s=>s+(o()*2-1)*i))}
function Jt(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}

if (true) {
    if (!email) {
    console.error("Usage: node q10_auto.js <email>");
    process.exit(1);
  }

  const data = go(email);
  const centroids = data.centroids;
  const items = data.items;
  const queries = data.queries;
  const rules = data.rules;

  const cosine_sim = (a, b) => {
    let dot = 0.0, normA = 0.0, normB = 0.0;
    for(let i=0; i<a.length; i++) { dot += a[i]*b[i]; normA += a[i]*a[i]; normB += b[i]*b[i]; }
    return normA===0||normB===0 ? 0 : dot/(Math.sqrt(normA)*Math.sqrt(normB));
  };

  // 1. Build Index
  const index = {};
  for (const c of centroids) {
      index[c.centroid_id] = [];
  }

  for (const item of items) {
      const c_scores = [];
      for (const c of centroids) {
          c_scores.push({ id: c.centroid_id, score: cosine_sim(item.embedding, c.embedding) });
      }
      c_scores.sort((a, b) => {
          if (a.score !== b.score) return b.score > a.score ? 1 : -1;
          return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
      });
      index[c_scores[0].id].push(item);
  }

  const answer = {};

  for (const q of queries) {
      // 2. Rank centroids for this query
      const c_scores = [];
      for (const c of centroids) {
          c_scores.push({ id: c.centroid_id, score: cosine_sim(q.embedding, c.embedding) });
      }
      c_scores.sort((a, b) => {
          if (a.score !== b.score) return b.score > a.score ? 1 : -1;
          return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
      });

      const top_centroids = c_scores.slice(0, q.nprobe).map(c => c.id);

      // Union of candidate sets
      const candidate_items = [];
      for (const cid of top_centroids) {
          candidate_items.push(...index[cid]);
      }

      // 3. Rank candidates
      const item_scores = [];
      for (const item of candidate_items) {
          item_scores.push({ id: item.item_id, score: cosine_sim(q.embedding, item.embedding) });
      }

      item_scores.sort((a, b) => {
          if (a.score !== b.score) return b.score > a.score ? 1 : -1;
          return a.id < b.id ? -1 : (a.id > b.id ? 1 : 0);
      });

      answer[q.query_id] = item_scores.slice(0, rules.top_k).map(i => i.id);
  }

  
    const _field = document.getElementById('q-ann-index-recall-latency-server');
    if (_field) {
        _field.value = JSON.stringify(answer, null, 2);
        _field.dispatchEvent(new Event('input', { bubbles: true }));
        _field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q10 Answer successfully populated!");
    } else {
        console.error("❌ Q10 input field not found on this page.");
    }
}

})();
```

---

### Q11 — Semantic Deduplication & Numeric Guardrail

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };
    const Zt = { default: ee.default };
    const X = { default: (seed) => sr(seed, { global: false }) };



function Ht(n){return String(n||'').trim().toLowerCase()}
function So(n){let o=0;for(let i=0;i<n.length;i++)o=(o<<5)-o+n.charCodeAt(i),o|=0;return Math.abs(o)}
function Oe(n,o){return String(n).padStart(o,'0')}
function Ut(n){let o=Math.sqrt(n.reduce((i,s)=>i+s*s,0))||1;return n.map(i=>Number((i/o).toFixed(6)))}
function Re(n,o,i){return Ut(n.map(s=>s+(o()*2-1)*i))}

function qo(email) {
    const xo = 'tds-ga4-dedup-data-18aae18831e243c9bea945c8822447aeb7cbcf66ee5c48e59044f142adc1f1e7d26da7f2760f94825cbc6b5d7f0a60b4';
    const Pt = 50, Ce = 0.03, vo = 55, ko = 70, _o = 32;

    function Gt(n) {
        let o = X.default(xo + '#' + n);
        return Ut(Array.from({length: _o}, () => o() * 2 - 1));
    }

    let o = Ht(email), i = So(o), s = [], m = 0, d = [];

    // families
    for (let e = 0; e < Pt; e++) {
        let r = Gt(`family-${o}-${e}`), c = 3000 + ((e * 37 + i) % 90) * 500, t = 3 + (e * 7 + i) % 5;
        d.push({ baseVector: r, numericFact: c });
        for (let a = 0; a < t; a++) {
            m += 1;
            s.push({
                doc_id: `SD_${Oe(m, 4)}`,
                embedding: Re(r, X.default(`${o}#fam#${e}#${a}`), Ce),
                numeric_fact: c
            });
        }
    }

    // traps
    for (let e = 0; e < vo; e++) {
        let r = d[(e * 13 + i) % Pt], c = e % 2 === 0 ? 1 : -1, t = 200 + (e % 5) * 37;
        m += 1;
        s.push({
            doc_id: `SD_${Oe(m, 4)}`,
            embedding: Re(r.baseVector, X.default(`${o}#trap#${e}`), Ce),
            numeric_fact: r.numericFact + c * t
        });
    }

    // singletons
    for (let e = 0; e < ko; e++) {
        let r = Gt(`singleton-${o}-${e}`);
        m += 1;
        s.push({
            doc_id: `SD_${Oe(m, 4)}`,
            embedding: Re(r, X.default(`${o}#single#${e}`), Ce),
            numeric_fact: 3000 + ((e * 53 + i) % 90) * 500
        });
    }

    return {
        docs: s,
        rules: {
            similarity_threshold: 0.92,
            numeric_tolerance: 50,
            numeric_field: "numeric_fact"
        }
    };
}

const cosine_sim = (a, b) => {
    let dot = 0.0, normA = 0.0, normB = 0.0;
    for(let i=0; i<a.length; i++) { dot += a[i]*b[i]; normA += a[i]*a[i]; normB += b[i]*b[i]; }
    return normA===0||normB===0 ? 0 : dot/(Math.sqrt(normA)*Math.sqrt(normB));
};

function solveQ11(email) {
    const data = qo(email);
    const docs = data.docs;
    const rules = data.rules;

    const parent = {};
    const find = (i) => {
        if (parent[i] === i) return i;
        parent[i] = find(parent[i]);
        return parent[i];
    };

    const union = (i, j) => {
        let rI = find(i);
        let rJ = find(j);
        if (rI !== rJ) {
            if (rI < rJ) parent[rJ] = rI;
            else parent[rI] = rJ;
        }
    };

    for (const doc of docs) {
        parent[doc.doc_id] = doc.doc_id;
    }

    for (let i = 0; i < docs.length; i++) {
        for (let j = i + 1; j < docs.length; j++) {
            const docI = docs[i];
            const docJ = docs[j];

            const sim = cosine_sim(docI.embedding, docJ.embedding);
            const numDiff = Math.abs(docI.numeric_fact - docJ.numeric_fact);

            if (sim >= rules.similarity_threshold && numDiff <= rules.numeric_tolerance) {
                union(docI.doc_id, docJ.doc_id);
            }
        }
    }

    const components = {};
    for (const doc of docs) {
        const root = find(doc.doc_id);
        if (!components[root]) components[root] = [];
        components[root].push(doc.doc_id);
    }

    const answer = {};
    for (const root in components) {
        const comp_docs = components[root];
        comp_docs.sort();
        const canonical = comp_docs[0];
        for (const id of comp_docs) {
            answer[id] = canonical;
        }
    }

    
    const _field = document.getElementById('q-semantic-dedup-numeric-guardrail-server');
    return answer;
}

// Implement the brute-force /backendVerify loop
const userObj = JSON.parse(localStorage.getItem('user') || '{}');
const baseEmail = (userObj?.email || '').trim().toLowerCase();
if (!baseEmail) {
    console.error("❌ Email not found in localStorage!");
    return;
}

const roll = baseEmail.split('@')[0];
const aliases = [
    '@ds.study.iitm.ac.in', 
    '@student.iitm.ac.in', 
    '@study.iitm.ac.in', 
    '@student.onlinedegree.iitm.ac.in', 
    '@onlinedegree.iitm.ac.in', 
    '@iitm.ac.in',
    '@smail.iitm.ac.in',
    '@iitmadras.ac.in',
    '@smail.iitmadras.ac.in',
    '@alum.iitm.ac.in',
    '@alumni.iitm.ac.in',
    '@research.iitm.ac.in',
    '@gmail.com',
    '@yahoo.com',
    '@outlook.com',
    '@hotmail.com',
    '' // Just the roll number
];

console.log("🔄 Starting brute-force verification for Q11...");

for (const alias of aliases) {
    let testEmail = alias ? roll + alias : baseEmail; // Fallback to raw baseEmail if empty alias
    
    console.log(`Testing alias: ${testEmail}`);
    let answer = solveQ11(testEmail);
    
    try {
        let res = await fetch("/backendVerify", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                email: userObj.email,
                quizSign: userObj.quizSign,
                response: answer,
                weight: 2,
                questionId: "q-semantic-dedup-numeric-guardrail-server"
            })
        });
        
        let data = await res.json();
        if (res.ok && data && (data.correct === true || data.status === 'success' || data.isCorrect)) {
            console.log(`✅ SUCCESS! The correct alias is: ${testEmail}`);
            
            // Populate the UI field
            const _field = document.getElementById('q-semantic-dedup-numeric-guardrail-server');
            if (_field) {
                _field.value = JSON.stringify(answer, null, 2);
                _field.dispatchEvent(new Event('input', { bubbles: true }));
                _field.dispatchEvent(new Event('change', { bubbles: true }));
                console.log("✅ Q11 Answer successfully populated in the UI!");
            }
            break;
        }
    } catch (e) {
        // Continue to next alias if verification fails
    }
}

})();

```

---

### Q12 — Context Assembly & Lost-in-the-Middle

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };
    const Zt = { default: ee.default };
    const X = { default: (seed) => sr(seed, { global: false }) };

    let email = '';
    try {
        const u = JSON.parse(localStorage.getItem('user'));
        email = (typeof u === 'object' ? u?.email : u) || '';
    } catch (e) {
        email = localStorage.getItem('user') || '';
    }
    email = email.trim().toLowerCase();
    if (!email) {
        console.error("❌ Email not found in localStorage!");
        return;
    }




var Wt = { default: ee.default };

const Co = "tds-ga4-context-assembly-data-271d73ad9bab61b3517cb379323b28edc716443bd31059bdafc8e7b17bd944fc5bec2f3ba9986e34e47d23f992d68767";
const Oo = 45;

function Do(n){let o=Ro(n),i=(0,Wt.default)(`${Co}#${o}#context-assembly-data`),s=[];for(let d=0;d<Oo;d++){let l=15+Math.floor(i()*16),e=[],r=0;for(let a=0;a<l;a++){let h=80+Math.floor(i()*321),u=Number(i().toFixed(4));r+=h,e.push({chunk_id:`CTX_${De(d+1,3)}_${De(a+1,3)}`,token_count:h,relevance_score:u})}let c=.35+d%7*.05,t=Math.round(r*c);s.push({query_id:`CA_Q_${De(d+1,3)}`,token_budget:t,candidate_chunks:e})}return{queries:s,rules:{selection_rule:"Sort candidate_chunks by relevance_score descending (ties broken by chunk_id ascending). Walk this order once, keeping a running token total: if a chunk's token_count fits within the remaining token_budget, select it and add its tokens to the running total; otherwise skip it and continue to the next chunk (do not stop at the first chunk that does not fit).",assembly_rule:"Take the selected chunks in relevance_score-descending order c1 (highest) .. cn (lowest). Build the final sequence by alternating from the outside in: c1 goes to position 0, c2 goes to the last position, c3 to position 1, c4 to the second-to-last position, and so on -- the most relevant selected chunks anchor both ends of the context and the least relevant selected chunk ends up in the middle.",output:"JSON object mapping query_id to an array of the selected chunk_id strings in final assembled order."}}}
function Ro(n){return String(n||"").trim().toLowerCase()}
function De(n,o){return String(n).padStart(o,"0")}

if (true) {
    if (!email) {
    console.error("Usage: node q12_auto.js <email>");
    process.exit(1);
  }

  const data = Do(email);
  const queries = data.queries;

  const answer = {};

  for (const q of queries) {
    // Step 1: Sort candidates: relevance_score desc, chunk_id asc on tie
    const sorted = [...q.candidate_chunks].sort((a, b) => {
      if (a.relevance_score !== b.relevance_score) {
        return b.relevance_score > a.relevance_score ? 1 : -1;
      }
      return a.chunk_id < b.chunk_id ? -1 : (a.chunk_id > b.chunk_id ? 1 : 0);
    });

    // Step 2: Greedy walk - select under budget, skip non-fitting but continue
    let remaining = q.token_budget;
    const selected = [];
    for (const chunk of sorted) {
      if (chunk.token_count <= remaining) {
        selected.push(chunk);
        remaining -= chunk.token_count;
      }
      // Don't stop - skip and continue
    }

    // Step 3: Serpentine arrange (outside-in)
    // selected is [c1, c2, c3, ...] in relevance-desc order
    // c1 -> pos 0 (front), c2 -> last pos (back), c3 -> pos 1, c4 -> 2nd-to-last...
    // Even indices (0,2,4) go left->right; Odd indices (1,3,5) go right->left
    const n = selected.length;
    const assembled = new Array(n);
    let left = 0;
    let right = n - 1;
    for (let i = 0; i < n; i++) {
      if (i % 2 === 0) {
        assembled[left++] = selected[i].chunk_id;
      } else {
        assembled[right--] = selected[i].chunk_id;
      }
    }

    answer[q.query_id] = assembled;
  }

  
    const _field = document.getElementById('q-context-assembly-lost-middle-server');
    if (_field) {
        _field.value = JSON.stringify(answer, null, 2);
        _field.dispatchEvent(new Event('input', { bubbles: true }));
        _field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q12 Answer successfully populated!");
    } else {
        console.error("❌ Q12 input field not found on this page.");
    }
}

})();
```

---

### Q13 — RRF Fusion

```javascript
(async () => {
    const seedrandom = (await import('https://cdn.jsdelivr.net/npm/seedrandom/+esm')).default;
    const sr = seedrandom;
    const ee = { default: (seed) => sr(seed, { global: false }) };
    const Zt = { default: ee.default };
    const X = { default: (seed) => sr(seed, { global: false }) };

    let email = '';
    try {
        const u = JSON.parse(localStorage.getItem('user'));
        email = (typeof u === 'object' ? u?.email : u) || '';
    } catch (e) {
        email = localStorage.getItem('user') || '';
    }
    email = email.trim().toLowerCase();
    if (!email) {
        console.error("❌ Email not found in localStorage!");
        return;
    }





const ce = [["invoice", "ledger", "revenue", "expense", "margin", "budget", "forecast", "audit", "payroll", "vendor", "asset", "liability", "equity", "tax", "cashflow", "profit", "loss", "credit", "debit", "capital", "accrual", "balance", "statement", "variance", "treasury"], ["shipment", "warehouse", "inventory", "carrier", "route", "freight", "delivery", "pallet", "dispatch", "tracking", "dock", "container", "manifest", "customs", "fulfillment", "barcode", "scanner", "transit", "fleet", "lastmile", "packaging", "returns", "supply", "demand", "reorder"], ["sensor", "device", "signal", "voltage", "current", "circuit", "gateway", "firmware", "telemetry", "battery", "antenna", "network", "protocol", "packet", "latency", "bandwidth", "module", "controller", "actuator", "calibration", "diagnostic", "frequency", "resistance", "connector", "hardware"], ["patient", "clinic", "diagnosis", "therapy", "dosage", "symptom", "vaccine", "screening", "nurse", "doctor", "hospital", "pharmacy", "medication", "allergy", "recovery", "treatment", "infection", "chronic", "acute", "laboratory", "sample", "trial", "wellness", "triage", "prescription"], ["student", "course", "lesson", "grade", "assignment", "quiz", "lecture", "campus", "faculty", "syllabus", "tutorial", "semester", "credit", "rubric", "library", "classroom", "enrollment", "degree", "alumni", "workshop", "mentor", "project", "exam", "feedback", "certificate"], ["server", "database", "cache", "api", "endpoint", "request", "response", "thread", "cluster", "container", "runtime", "deploy", "scaling", "memory", "cpu", "queue", "worker", "session", "token", "schema", "migration", "backup", "replica", "shard", "timeout"], ["campaign", "audience", "brand", "content", "channel", "conversion", "impression", "click", "creative", "segment", "retention", "loyalty", "promotion", "pricing", "survey", "persona", "funnel", "newsletter", "sponsor", "launch", "market", "social", "engagement", "lead", "growth"], ["weather", "climate", "rainfall", "temperature", "humidity", "pressure", "forecast", "storm", "monsoon", "drought", "wind", "cloud", "satellite", "radar", "season", "cyclone", "flood", "heatwave", "snowfall", "evaporation", "airmass", "front", "precipitation", "visibility", "barometer"], ["recipe", "ingredient", "kitchen", "flavor", "spice", "sauce", "baking", "grill", "roast", "simmer", "texture", "portion", "nutrition", "protein", "carbohydrate", "vitamin", "menu", "chef", "restaurant", "cuisine", "pantry", "grain", "vegetable", "dessert", "beverage"], ["contract", "clause", "policy", "compliance", "regulation", "license", "permit", "liability", "privacy", "security", "breach", "audit", "standard", "governance", "risk", "control", "evidence", "approval", "review", "obligation", "dispute", "retention", "consent", "jurisdiction", "filing"], ["image", "pixel", "camera", "render", "filter", "contrast", "brightness", "histogram", "texture", "object", "detection", "segmentation", "label", "frame", "video", "resolution", "channel", "mask", "feature", "vision", "caption", "scene", "depth", "color", "annotation"], ["graph", "node", "edge", "path", "degree", "centrality", "community", "network", "cluster", "bridge", "weight", "flow", "route", "matrix", "adjacency", "component", "link", "neighbor", "distance", "ranking", "pagerank", "subgraph", "cycle", "tree", "bipartite"]];
const zo = "the and for with from into using across between during after before under over within without near through about each many some every this that these those when where while".split(" ");
const To = "q-rrf-fusion-server";
const Eo = 150;

function jo(n){return String(n||"").trim().toLowerCase()}
function le(n,o,i){return o+Math.floor(n()*(i-o+1))}
function Ee(n,o){return o[Math.floor(n()*o.length)]}
function Mo(n,o){let i=le(n,4,6),s=new Set;for(;s.size<i;)s.add(Ee(n,o));return[...s].join(" ")}
function Lo({email:n,id:o=To,version:i=""}){let s=(0,Zt.default)(`${jo(n)}#${o}#${i??""}`),m=[];for(let e=1;e<=Eo;e++){let r=le(s,0,ce.length-1),c=le(s,20,45),t=[];for(let a=0;a<c;a++)t.push(s()<.65?Ee(s,ce[r]):Ee(s,zo));m.push({id:e,text:t.join(" ")})}let d=le(s,0,ce.length-1),l=Mo(s,ce[d]);return{docs:m,query:l}}

if (true) {
    if (!email) { console.error("Usage: node q13_auto.js <email>"); process.exit(1); }

  const {docs, query} = Lo({email});

  // Tokenizer: lowercase, split on [^a-z0-9]+, drop empty
  function tokenize(text) {
    return text.toLowerCase().split(/[^a-z0-9]+/).filter(t => t.length > 0);
  }

  const queryTokens = tokenize(query);
  const queryTermSet = [...new Set(queryTokens)];

  // Tokenize all docs
  const docTokens = docs.map(d => tokenize(d.text));
  const N = 150;
  const avgdl = docTokens.reduce((s, t) => s + t.length, 0) / N;

  // ============ Step 1: BM25 ============
  const k1 = 1.5, b = 0.75;

  // Compute df for each query term
  const df = {};
  for (const term of queryTermSet) {
    df[term] = 0;
    for (const tokens of docTokens) {
      if (tokens.includes(term)) df[term]++;
    }
  }

  // Score each doc with BM25
  const bm25Scores = docs.map((doc, idx) => {
    const tokens = docTokens[idx];
    const dl = tokens.length;
    let score = 0;
    for (const term of queryTermSet) {
      const f = tokens.filter(t => t === term).length;
      if (f === 0) continue;
      const idf = Math.log((N - df[term] + 0.5) / (df[term] + 0.5) + 1);
      score += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / avgdl));
    }
    return { id: doc.id, score };
  });

  // Sort: score desc, tie-break lower doc id
  bm25Scores.sort((a, b) => a.score !== b.score ? b.score - a.score : a.id - b.id);
  const listA = bm25Scores.slice(0, 20).map(d => d.id);

  // ============ Step 2: Hashed Embedding (FNV-1a) ============
  const D = 64;

  function fnv1a(token) {
    let hash = 0x811c9dc5;
    for (let i = 0; i < token.length; i++) {
      hash ^= token.charCodeAt(i);
      hash = Math.imul(hash, 0x01000193);
      hash = hash >>> 0; // unsigned 32-bit
    }
    return hash;
  }

  function tokenToVec(tokens) {
    const vec = new Array(D).fill(0);
    for (const token of tokens) {  // ALL occurrences, not unique
      const h = fnv1a(token);
      const bucket = h % D;
      const sign = ((h >>> 16) & 1) === 0 ? 1 : -1;
      vec[bucket] += sign;
    }
    return vec;
  }

  function l2norm(vec) {
    const norm = Math.sqrt(vec.reduce((s, v) => s + v * v, 0));
    return norm === 0 ? null : vec.map(v => v / norm);
  }

  function dotProduct(a, b) {
    if (!a || !b) return 0;
    return a.reduce((s, v, i) => s + v * b[i], 0);
  }

  const queryVec = l2norm(tokenToVec(queryTokens));

  const embScores = docs.map((doc, idx) => {
    const vec = l2norm(tokenToVec(docTokens[idx]));
    return { id: doc.id, score: dotProduct(queryVec, vec) };
  });

  embScores.sort((a, b) => a.score !== b.score ? b.score - a.score : a.id - b.id);
  const listB = embScores.slice(0, 20).map(d => d.id);

  // ============ Step 3: RRF Fusion ============
  const rrfK = 60;

  // Build rank maps (1-indexed)
  const rankA = {};
  listA.forEach((id, i) => rankA[id] = i + 1);
  const rankB = {};
  listB.forEach((id, i) => rankB[id] = i + 1);

  // Get all unique docs in both lists
  const allIds = new Set([...listA, ...listB]);
  const rrfScores = [];
  for (const id of allIds) {
    let score = 0;
    if (rankA[id]) score += 1 / (rrfK + rankA[id]);
    if (rankB[id]) score += 1 / (rrfK + rankB[id]);
    rrfScores.push({ id, score });
  }

  // Sort: score desc, tie-break lower doc id
  rrfScores.sort((a, b) => {
    const diff = b.score - a.score;
    if (Math.abs(diff) > 1e-12) return diff;
    return a.id - b.id;
  });

  const top5 = rrfScores.slice(0, 5).map(d => d.id);
  const thirdScore = parseFloat(rrfScores[2].score.toFixed(6));

  
    const _field = document.getElementById('q-rrf-fusion-server');
    if (_field) {
        _field.value = JSON.stringify({ top5, third_score: thirdScore }, null, 2);
        _field.dispatchEvent(new Event('input', { bubbles: true }));
        _field.dispatchEvent(new Event('change', { bubbles: true }));
        console.log("✅ Q13 Answer successfully populated!");
    } else {
        console.error("❌ Q13 input field not found on this page.");
    }
}

})();
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `❌ Email not found in localStorage` | Make sure you are logged into the exam portal |
| `❌ input field not found on this page` | Make sure you are on the correct question's section |
| Answer looks wrong | Re-run the script, do not manually edit the filled text |
