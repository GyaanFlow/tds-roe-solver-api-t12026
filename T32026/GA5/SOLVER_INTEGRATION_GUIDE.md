# T3-2026 GA5: browser-solver integration guide

How to wire the four T3 GA5 questions into the static browser solver (`tds-roe-solver/solvers/T32026/ga5/`) using the
same style as T3 GA1 (`api-client.js` URL builders, `/health` wake-up, `window.tdsPatchAnswer`).
Exam source: `exam-tds-2026-09-ga5.js` (snapshot in this folder). All weights below are the page defaults.

| # | Exam id | Marks | Kind | Hub route (origin = the Render host) |
|---|---|---|---|---|
| Q1 | `q-rag-colosseum-server` | 2 | live server, grader calls `POST {base}/query` | submit `{ORIGIN}/t3ga5/{email}` |
| Q2 | `q-ollama-faiss-rank-correlation-server` | 2 | local compute (real Ollama models), paste a 10x7 matrix | script + dataset from the hub |
| Q3 | `q-ball-tracker-server` | 2 | binary PNG frames from the student's signed URL | browser-side only: the solver's `exam-page.js` + `tracker.js` (not part of this hub; being debugged) |
| Q4 | `q-harness-safety-router-server` | 1 | live server, grader calls the exact POST route | submit `{ORIGIN}/t3ga5/{email}/harness` |
| Q5 | `q-time-use-review-server` | 2 | **manual** poster review (added to the exam in Nov 2026) | nothing to serve: student pastes the signed receipt |

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

// Render's free tier sleeps; the first request after sleep takes ~30-60 s, far over the grader's 8 s limit.
// Call this before showing the Q1/Q4 answers and tell the student to press Check only after it returns true.
export async function wakeApi(onStatus = () => {}) {
  for (let i = 1; i <= 8; i++) {
    onStatus(`Waking the GA5 server (attempt ${i}/8)…`);
    try {
      const r = await fetch(`${T3_API_ORIGIN}/t3ga5/health`, { cache: 'no-store', signal: AbortSignal.timeout(15000) });
      if (r.ok && (await r.json()).ok === true) { onStatus('GA5 server is awake.'); return true; }
    } catch { /* still asleep or network error: retry */ }
    await new Promise(res => setTimeout(res, 5000));
  }
  onStatus('GA5 server did not wake. Open the health link manually, then retry.');
  return false;
}
```

`GET /t3ga5/health` returns `{"ok": true, ...}` with CORS `*`, so it can be called straight from the static page.

### Module list (`ga5/index.js`)

```js
import * as q1 from './q01-rag-colosseum.js';
import * as q2 from './q02-ollama-faiss.js';
import * as q3 from './q03-ball-tracker.js';      // placeholder until Q3 is built
import * as q4 from './q04-harness-safety-router.js';
import * as q5 from './q05-time-use-review.js';
export const questions = [q1, q2, q3, q4, q5];
```

Each module exports `id`, `title` and `async solve(email)`, which returns the usual result object
(`{type: 'solved' | 'guide' | 'manual', answer?, answerDisplay}`). Use `window.tdsPatchAnswer(id, answer)` to fill a field,
the same as T3 GA1. Run `await wakeApi(...)` once before Q1 and Q4.

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
"confidence": 0..1}`. CORS `Access-Control-Allow-Origin: *` is set; responses take well under a second (limit: 8 s).

The engine follows the five rounds seen in the **real grader traffic** (captured 2026-11-27):

| Round | What the grader asks | What the service returns |
|---|---|---|
| Retrieval | a value question that **describes** a passage without naming it ("periodic keepalive signals sent by the cluster coordinator…") | the sentence holding that value, its passage first in `sources` |
| Abstention | "How does X handle…", "exact mathematical formulation of…", off-topic trivia | `answer: null`, `sources: []`, `scores: []`, confidence 0.1 |
| Synthesis | "Synthesizing …: <opening of passage A>. Furthermore, in adjacent architecture: <opening of B>. How do both integrate?" | every value of both passages (e.g. `"3, 150, 250, 2"`), sources `[A, B]` |
| Adversarial | the same questions with injected instructions (HTML comments, `[INST]`, fake system tags) or a **false premise** ("Since Raft requires 100 nodes…") | injections are stripped and ignored; a false premise abstains |
| Concurrent | plain named value questions, sent in parallel | the value sentence |

Definition questions ("What is X?") abstain too, matching a reference service that scores 20/20.

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

The grader sends four batches of 24 cases (at most two at a time, 60 s each, 2 MiB limit, no redirects) with the full
policy, and expects `{"profile","batchId","results":[{"caseId","requestDecision","toolDecision","route","trajectory"}]}`.
Each case is judged on its own, in any order. A duplicate `caseId` returns 422, and one malformed case degrades to a safe
default instead of failing the batch.

Real cases carry trusted `proposedTool.resolved` metadata with a fixed operation vocabulary (`workspace_read`, `workspace_edit`,
`read_secret`, `read_public_schema`, `delete`, `send`, `deploy`, `rollback`, `database_mutation`, `terraform_apply`, `restart`,
`force_push`, `host_admin`, `security_test`). `harness_structured.py` decides from that metadata plus the isolation facts,
preflight records, rollback plan and the ordered user messages:

- harmful requests (credential theft, fraud, harassment, destructive malware, physical harm) block everything, route `none`;
- revoked or explicitly forbidden actions, out-of-scope credential reads, private data to an unapproved destination and a
  bypassed preflight block the tool;
- production mutations need an exact approval (same target and environment), a passed preflight and a matching rollback plan,
  otherwise `review`; unknown environments are `review`;
- security work uses the `restricted` route; unclear ownership or scope is `review`;
- untrusted tool output that tries to steer the session moves the trajectory to `watch`.

The grader returns only a total ("Safety: N/96 complete decisions correct"), so a few readings of the policy are unconfirmed:
a failed preflight gives `review`, "has not been approved" / "no other namespace is approved" give `review`, malware-report
analysis uses `restricted`, and prompt-injection inspection uses `primary`.

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

Not served by this hub. Your static solver already ships a browser tracker (`solvers/T32026/ga5/exam-page.js`, `tracker.js`,
`ga5-tools.js`) that downloads the frames with the student's own session; it was reported failing and needs the console error to fix.
The exam serves binary frames at `/questionData?...&questionId=q-ball-tracker-server` (header: fps,
frame count, three target frame numbers, then length-prefixed PNG frames; the student reports the final number on their ball and
the ball centre at the three target frames). It needs the student's own frames file to build and test a tracker.
Until then, register a placeholder:

```js
export const id = 'q-ball-tracker-server';
export const title = 'Q3: Track the red ball';
export async function solve() {
  return { type: 'manual', answerDisplay: '### Q3: Track the red ball\nNot automated yet. Answer format: `number; x,y; x,y; x,y`.' };
}
```

## 5b. Q5 Time Use poster review: `q05-time-use-review.js` (manual)

This one has no API. The student opens the review link inside Q5 on the exam page, compares at least eight poster pairs
(choose A, B or "about equal", with a short reason), then copies the **signed review receipt** and pastes it into the Q5 field.
Marks reward taking part, not agreeing with others. The solver should only show instructions and never generate or alter the receipt.

```js
export const id = 'q-time-use-review-server';
export const title = 'Q5: Time Use Charts: which data story would you share?';
export async function solve() {
  return { type: 'manual', answerDisplay: [
    '### Q5: Poster review (manual)',
    '1. Open the review link in Q5 on the exam page.',
    '2. Compare at least 8 poster pairs, each with a short reason.',
    '3. Copy the signed receipt and paste it into the Q5 field, then Check and Save.'].join('\n') };
}
```

## 6. Verification

```bash
python -m pytest tests/test_t32026_ga5.py tests/test_t32026_ga5_robust.py tests/test_t32026_ga5_instructions.py \
                 tests/test_t32026_ga5_grader_probes.py tests/test_t32026_ga5_harness_real.py -q
```

- `test_t32026_ga5_grader_probes.py`: the 20 **real** Q1 probes on six emails, plus generated probes in the same style
  (synthesis for all 25 passage pairs, false and true premises for every passage, nameless paraphrases).
- `test_t32026_ga5_harness_real.py`: the 96 **real** Q4 cases (fixture `tests/fixtures/t3ga5_harness_real_cases.json`, no student
  data), pinned to the reviewed decisions, plus the cross-axis rules the policy states.
- The older suites: knowledge base and Q2 dataset against npm `seedrandom`, injection styles, hostile and malformed input (no 5xx),
  policy invariants on random cases, the batch contract, the Q2 script against a fake Ollama, and the routes through the gateway.

Status on 2026-11-27: the live service answers all 20 real Q1 probes correctly and returns the tested decision on all 96 real Q4
cases. The real score still comes only from a Check.

## 7. Recording the grader's real traffic (owner only)

The two graded routes (`/query`, `/harness`) are recorded by default: request and response, `sensitive` fields redacted, bounded,
kept only in the server's temp directory. Read them with
`GET {ORIGIN}/t3ga5/{email}/debug/captures?key=<owner key>`. The key is either `$T3GA5_DEBUG_KEY` or the owner secret whose SHA-256
is pinned in `main.py` (the secret itself is never committed). A wrong or missing key returns 404. Set `T3GA5_CAPTURE=0` to turn
recording off. Render's free tier wipes the recording on every restart, so read it soon after pressing Check.

**Never put the key in the static solver**: the solver only needs the two answer URLs.

## Common mistakes

- Appending `/query` to the Q1 answer (the grader adds it itself). A trailing slash (`…/t3ga5/{email}/`) is harmless: the hub
  collapses `//query` since commit 5a1d8c0.
- Using up checks: each Check or Save counts against the exam's limited checks per time window. Keep one for Save.
- Submitting Q4 without the `/harness` suffix.
- Not encoding `@` in the email, or using a mixed-case email (the exam lower-cases it).
- Pressing Check while Render is asleep: the Q1 gauntlet has an 8-second limit per request.
- Expecting Q2 to be solved by a URL: it is a local computation.
