# T3-2026 GA5: browser-solver integration guide

How to wire the four T3 GA5 questions into the static browser solver (`tds-roe-solver/solvers/T32026/ga5/`) using the
same style as T3 GA1 (`api-client.js` URL builders, `/health` wake-up, `window.tdsPatchAnswer`).
Exam source: `exam-tds-2026-09-ga5.js` (snapshot in this folder). All weights below are the page defaults.

| # | Exam id | Marks | Kind | Hub route (origin = the Render host) |
|---|---|---|---|---|
| Q1 | `q-rag-colosseum-server` | 2 | live server, grader calls `POST {base}/query` | submit `{ORIGIN}/t3ga5/{email}` |
| Q2 | `q-ollama-faiss-rank-correlation-server` | 2 | local compute (real Ollama models), paste a 10x7 matrix | script + dataset from the hub |
| Q3 | `q-ball-tracker-server` | 2 | binary PNG frames from the student's signed URL | **not built yet** (needs a real frames file) |
| Q4 | `q-harness-safety-router-server` | 1 | live server, grader calls the exact POST route | submit `{ORIGIN}/t3ga5/{email}/harness` |

`{email}` is the trimmed, lower-cased exam email, URL-encoded (`@` becomes `%40`): the exam seeds Q1 and Q2 with exactly that
form. Use **Render** as the origin (`https://tds-roe-solver-api-t12026.onrender.com`). The free tier sleeps, so call
`GET {ORIGIN}/t3ga5/health` just before pressing Check.

## 1. Shared helper (`ga5/api-client.js`, new; or extend `ga1/api-client.js`)

```js
import { normalizeEmail } from './utils.js';

export const T3_API_ORIGIN = 'https://tds-roe-solver-api-t12026.onrender.com';

export function t3ga5Url(email, suffix = '') {
  const norm = normalizeEmail(email);
  if (!norm || !norm.includes('@')) throw new Error('A valid exam email is required.');
  return `${T3_API_ORIGIN}/t3ga5/${encodeURIComponent(norm)}${suffix}`;
}

export async function wakeApi() {
  for (let i = 0; i < 6; i++) {            // Render can take ~30-50 s to wake
    try { const r = await fetch(`${T3_API_ORIGIN}/t3ga5/health`, { cache: 'no-store' }); if (r.ok) return true; } catch {}
    await new Promise(res => setTimeout(res, 8000));
  }
  return false;
}
```

## 2. Q1 RAG Colosseum: `q01-rag-colosseum.js`

The answer is the **base URL** (no `/query`). The hub regenerates the student's 50-passage knowledge base from the email, so
there is nothing to upload.

```js
import { t3ga5Url } from './api-client.js';
export const id = 'q-rag-colosseum-server';
export const title = 'Q1: RAG Colosseum';
export async function solve(email) {
  const url = t3ga5Url(email);
  return { type: 'solved', answer: url, variant: 'Live T3 GA5 RAG endpoint',
    answerDisplay: ['### Q1: RAG Colosseum', '**Submit this base URL:**', '```text', url, '```', '',
      'The grader POSTs `{base}/query`. Open `/t3ga5/health` first so the free server is awake.'].join('\n') };
}
```

Contract served at `POST {base}/query` with `{"question": "...", "top_k": 3}`:
`{"answer": string|null, "sources": [0-based passage ids, descending], "scores": [0..1, descending, same length],
"confidence": 0..1}`. It abstains (`answer: null`, empty `sources`/`scores`, confidence 0.1) when the question asks for an
attribute the matching passage does not state, or names something outside the knowledge base. Answers compare two passages
when two entities are named. Instructions hidden in a question are discarded; the answer comes only from the passages.
CORS `Access-Control-Allow-Origin: *` is set; a typical response takes tens of milliseconds (limit: 8 s).

Debug views: `GET {base}/kb` (the 50 passages) and the dashboard at `{ORIGIN}/t3ga5/`.

## 3. Q4 Harness safety router: `q04-harness-safety-router.js`

Same shape as Q1 with a different suffix, and the answer is the **exact POST route**:

```js
import { t3ga5Url } from './api-client.js';
export const id = 'q-harness-safety-router-server';
export const title = 'Q4: Harness Engineering: Contextual Safety and Model Routing';
export async function solve(email) {
  const url = t3ga5Url(email, '/harness');
  return { type: 'solved', answer: url, variant: 'Live T3 GA5 harness endpoint',
    answerDisplay: ['### Q4: Harness safety router', '**Submit this exact POST route:**', '```text', url, '```'].join('\n') };
}
```

The grader sends four batches of 24 cases (two at a time) to this route and expects
`{"profile","batchId","results":[{"caseId","requestDecision","toolDecision","route","trajectory"}]}`. Each case is judged on its
own, in any order. A duplicate `caseId` returns 422, and one malformed case degrades to a safe default instead of failing the
batch. The rules implement the policy text shown in the exam (content policy, security-research scope, exact and unrevoked
user approval, isolation facts, production preflight and rollback, routing, trajectory).

## 4. Q2 Ollama / FAISS rank correlation: `q02-ollama-faiss.js` (guide result)

The graded value is the Spearman rho between **two real Ollama embedding models**, which must land within +/-0.05 of the
exam's reference, so no hosted service can produce it. The solver returns a `guide` result with commands to run locally:

```text
ollama pull nomic-embed-text
ollama pull mxbai-embed-large
pip install requests numpy
curl -s {ORIGIN}/t3ga5/{email}/answers/ollama-script -o ollama_matrix.py
python ollama_matrix.py --email {email} --host {ORIGIN}
```

The last command prints the 10x7 matrix `[[a1,a2,a3,b1,b2,b3,rho], ...]` to paste into the exam. The hub also serves the
student's exact `dataset.json` at `GET {ORIGIN}/t3ga5/{email}/answers/ollama-dataset` (verified identical to the exam page's
generator). `ollama_matrix.py` follows the exam's starter script (normalised embeddings, inner-product search over all 50
documents, Spearman rho) without needing FAISS or SciPy; its rank and rho math is tested against SciPy.

## 5. Q3 Track the red ball

No hosted service can answer this one: the exam serves a binary frames file at `/questionData?...&questionId=q-ball-tracker-server`
that only the signed-in student can fetch (layout: big-endian uint32 fps, frame count, three target frame numbers, then
length-prefixed PNG frames), and the student reports the final number on their ball plus the ball centre at the three target frames
(`number; x,y; x,y; x,y`).

The portal ships `solvers/T32026/ga5/q03-ball-tracker.js`: the student saves the frames file once, opens it in an in-browser viewer
(frame stepping, zoom, "find my red ball" in frame 0, click-to-mark with exact pixel mapping) and gets the answer line built for them.
It also offers a small `ball_frames.py` that unpacks the file into PNGs for anyone who wants to write an automatic tracker. There is no
server-side tracker because no real frames file was available to build and validate one.

## 6. Verification

```bash
python -m pytest tests/test_t32026_ga5.py tests/test_t32026_ga5_robust.py -q
```

Covers: the knowledge base and Q2 dataset against the real npm `seedrandom`; Q1 retrieval / extraction / abstention / comparison /
injection rounds; **phrasings the engine was not tuned on** (about 99-100% on three emails and on 300 random emails), nine styles of
unanswerable question (about 100% abstain), definition and conceptual questions; hostile and malformed input (1,300+ requests, no
5xx); 55 harness policy cases; the batch contract; the Q2 script end to end against a fake Ollama (both embedding APIs, missing model,
Ollama offline); and the routes through the real gateway. These are **local, self-written probes**: the real grader's 20 questions
and 96 cases are unseen, so treat a Check result as the authority.

Q1 behaviour in short: a value question answers with the passage sentence that states the value; it abstains when the matching passage
has no such value (`"Raft election timeout"`, `"replication factor"`, `"who invented X"`); a bare definition (`"What is X?"`) returns the
opening sentence; two named entities with a comparison cue return one fact each plus the verdict.

## 7. Recording the grader's real traffic (optional, owner only)

Set `T3GA5_DEBUG_KEY` on the host. The two graded routes are then recorded (request and response, `sensitive` fields redacted,
bounded, kept in the temp directory) and readable at
`GET {ORIGIN}/t3ga5/{email}/debug/captures?key=<T3GA5_DEBUG_KEY>`. Without that variable nothing is stored and the route
returns 404. Render's free tier wipes the recording on every restart, so read it soon after pressing Check.

## Common mistakes

- Appending `/query` to the Q1 answer (the grader adds it itself).
- Submitting Q4 without the `/harness` suffix.
- Not encoding `@` in the email, or using a mixed-case email (the exam lower-cases it).
- Pressing Check while Render is asleep: the Q1 gauntlet has an 8-second limit per request.
- Expecting Q2 to be solved by a URL: it is a local computation.
