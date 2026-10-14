# T3-2026 GA1 — Browser-Solver Integration Guide (Q6, Q14, Q15)

How to wire the three live API questions into the static browser solver
(`C:/Users/gaura/Downloads/tds-roe-solver/tds-roe-solver/solvers/T32026/ga1/`)
using the same `solve(email)` → `{type:'solved', answer, answerDisplay}` style as
`solvers/T22026/ga2/q-config-precedence.js`.

Q13 (termlog) is **not** an API answer: it needs the student's own signed recording
archive. See [Q13_IMPLEMENTATION_GUIDE.md](Q13_IMPLEMENTATION_GUIDE.md).

## 0. Which host to use

| Host | Q6 config | Q14 MCP | Q15 Ledger |
|---|---|---|---|
| Render `https://tds-roe-solver-api-t12026.onrender.com` | ✅ | ✅ | ✅ (verified live, 6/6 in ~3.7 s cold) |
| HF Space `https://23f1000805-tds-roe-solver-api-t12026.hf.space` | ✅ | ✅ | ❌ HF egress to `exam.sanand.workers.dev` times out |

**Use Render for all three.** Render's free tier sleeps after inactivity; the first
request after sleep can take ~30–50 s, which can exceed the Ledger grader's 15 s
limit. Open `https://tds-roe-solver-api-t12026.onrender.com/health` once just before
pressing *Check*.

## 1. Endpoint contracts

| Q | Exam id | Submit URL | Grader behaviour |
|---|---|---|---|
| Q6 | `q-config-precedence-server` | `{ORIGIN}/ga1/{email}/effective-config` | Browser `GET`s it with appended `?set=key=value&…`; compares all 5 keys with `===` (int `port`/`workers`, bool `debug`, `api_key` = `"****"`). CORS required. |
| Q14 | `q-mcp-server-live-server` | `{ORIGIN}/ga1/{email}/mcp` | Real MCP client: `initialize` → `notifications/initialized` → `tools/list` → 5 × `tools/call solve_challenge` with a fresh `X-Exam-Challenge` header. Text must be `sha256("{challenge}:{email}")[:16]`. |
| Q15 | `q-ledger-agent-server` | `{ORIGIN}/ga1/{email}/ledger/{key}/answer` | `POST {"question":"…"}` several at once; each must return the exact `{"answer":…}` within 15 s. |

`{email}` is the trimmed, lower-cased exam email, URL-encoded (`@` → `%40`).

Q15's `{key}` is the student's `quizSign` in URL-safe form (`+`→`-`, `/`→`_`,
padding `=` removed). It lets the server fetch that student's private ledger with
no stored state. **Get it from `/ga1/onboard`**, which also verifies the
signature with the exam server before returning the URL:

```http
POST {ORIGIN}/ga1/onboard
Content-Type: application/json

{"email":"student@ds.study.iitm.ac.in","question_data_url":"https://exam.sanand.workers.dev/questionData?email=…&quizSign=…&questionId=q-ledger-agent-server&path=/"}
```

Response (abridged): `{"status":"ok","submit_url":"{ORIGIN}/ga1/{email}/ledger/{key}/answer","routes":{…}}`.
Errors: `400 VALID_LEDGER_QUESTION_DATA_URL_REQUIRED` (wrong email / question / host),
`502 LEDGER_UPSTREAM_REJECTED` with `upstream_status` 401/403 (expired or wrong signature),
`504 LEDGER_DISCOVERY_TIMEOUT`.

## 2. Shared helper — `solvers/T32026/ga1/api-client.js` (new)

```js
import { normalizeEmail } from './utils.js';

export const T3_GA1_API_ORIGIN = 'https://tds-roe-solver-api-t12026.onrender.com';

export function ga1Url(email, suffix) {
  const norm = normalizeEmail(email);
  if (!norm || !norm.includes('@')) throw new Error('A valid exam email is required.');
  return `${T3_GA1_API_ORIGIN}/ga1/${encodeURIComponent(norm)}${suffix}`;
}

export function apiAnswer(title, url, notes) {
  return {
    type: 'solved',
    answer: url,
    variant: `Live T3 GA1 endpoint`,
    answerDisplay: [`### ${title}`, `**Submit this URL:**`, '```text', url, '```', '', notes].join('\n'),
  };
}
```

## 3. Q6 — `q06-config-precedence.js`

```js
import { ga1Url, apiAnswer } from './api-client.js';

export const id = 'q-config-precedence-server';
export const title = 'Q6: Resolve 12-Factor Config Precedence';

export async function solve(email) {
  const url = ga1Url(email, '/effective-config');
  return apiAnswer(title, url,
    'The grader appends fresh `?set=key=value` overrides itself — submit the URL exactly as shown.');
}
```

Do not append a sample `?set=` to the answer.

## 4. Q14 — `q14-mcp-server.js`

```js
import { ga1Url, apiAnswer } from './api-client.js';

export const id = 'q-mcp-server-live-server';
export const title = 'Q14: Build a Live MCP Server';

export async function solve(email) {
  const url = ga1Url(email, '/mcp');
  return apiAnswer(title, url,
    'One tool, `solve_challenge`, hashes each call\'s fresh `X-Exam-Challenge` header with your email.');
}
```

Never compute the digest in the browser — the challenge is fresh per call.

## 5. Q15 — `q15-ledger-agent.js`

`solve(email)` only receives the email, but Q15 needs the student's signed URL.
Ask for it with `prompt()` (the exam page uses the same pattern for AI Pipe
tokens), send it once to `/ga1/onboard`, and return the `submit_url`. Do not store
the signed URL in `localStorage`, source, or logs.

```js
import { normalizeEmail } from './utils.js';
import { T3_GA1_API_ORIGIN } from './api-client.js';

export const id = 'q-ledger-agent-server';
export const title = 'Q15: The Ledger Agent';

const DASHBOARD = `${T3_GA1_API_ORIGIN}/ga1/`;

function guide(message) {
  return {
    type: 'guide',
    answer: DASHBOARD,
    variant: 'Signed Ledger URL required',
    answerDisplay: [
      `### ${title}`,
      message,
      '',
      `Or open **${DASHBOARD}**, paste your email and the full Ledger \`questionData\` URL, and submit the Ledger URL it shows.`,
    ].join('\n'),
  };
}

export async function solve(email) {
  const norm = normalizeEmail(email);
  const signed = typeof prompt === 'function'
    ? (prompt('Paste your full Q15 Ledger URL (https://exam.sanand.workers.dev/questionData?...&questionId=q-ledger-agent-server&path=/)') || '').trim()
    : '';
  if (!signed) return guide('No Ledger URL was entered.');

  let r, data;
  try {
    r = await fetch(`${T3_GA1_API_ORIGIN}/ga1/onboard`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: norm, question_data_url: signed }),
    });
    data = await r.json();
  } catch (e) {
    return guide(`The API is waking up or unreachable (${e.message}). Wait 30 s and run again.`);
  }
  if (!r.ok || !data.submit_url) {
    const reason = data?.upstream_status === 403 || data?.upstream_status === 401
      ? 'The exam rejected that signature — copy a fresh Ledger URL from your exam page.'
      : `Onboarding failed: ${data?.error || r.status}.`;
    return guide(reason);
  }
  return {
    type: 'solved',
    answer: data.submit_url,
    variant: `Ledger agent endpoint for ${norm}`,
    answerDisplay: [
      `### ${title}`,
      '**Submit this URL:**',
      '```text', data.submit_url, '```',
      '',
      'It contains your exam signature in URL-safe form — keep it private like the original link.',
      'Open the API `/health` once before pressing Check so Render is awake.',
    ].join('\n'),
  };
}
```

Make sure `runtime.js`/`wrapSolverModule` accepts `type: 'guide'` as well as
`'solved'` (it already does for other guide questions). Update the `registry.js`
comments for q06/q14/q15 from "separate API project handoff" to "live API"; the
`apiHandoffQuestions` metadata can stay.

## 6. What the Ledger engine handles (for the guide text / debugging)

Learned per student from their own data: products, regions, customer ids, currencies, rates.

- Duplicate order ids → the row with the latest `updated_at` wins (compared as instants; the feed mixes `Z` and `+05:30`).
- Business dates in Asia/Kolkata (orders at `2026-03-31T20:00Z` count in April).
- Revenue = `paid` only; refunds = `refunded`; amounts × `usd_per_unit`, summed with Decimal, rounded to cents at the end.
- Measures: revenue, refund amount/count, units, order count, distinct customers/products, average/largest/smallest order, percentage share, top-N/least by product/customer/region/month/currency.
- Filters: region(s) (incl. "Northern", "excluding West"), product names (plural, hyphen/space variants), customer ids, non-USD currency (`EUR orders`, `paid in INR`), dates (month±year, `2026-03`, ISO days, `March 5`, Q1–Q4, halves, year, `between … and …`, `since`, `before`, `until`).
- Ambiguity choices: unqualified "how many orders" counts every status; "how many customers" counts every status unless the question says bought/paid/purchased/spent.

## 7. Verify before submitting

```bash
curl -s "https://tds-roe-solver-api-t12026.onrender.com/ga1/student%40ds.study.iitm.ac.in/effective-config?set=port=9000&set=debug=true"
```

```bash
curl -s -X POST "<Q15 submit_url>" -H "Content-Type: application/json" -d '{"question":"What was the total revenue in USD from the North region in March 2026?"}'
```

The `/ga1/` dashboard runs the same checks (config override, Ledger sample question, full MCP handshake with a fresh challenge). After editing the solver repo, run its usual `node check.mjs --t3-ga1-only`.

## Common mistakes

- Submitting the HF Space URL for Q15 (its egress to the exam server times out).
- Submitting `/ga1/{email}/ledger/answer` (stored-signature route) instead of the keyed `submit_url`; it breaks whenever Render restarts and loses its SQLite file.
- Submitting the `/onboard` or dashboard URL as an answer.
- Not encoding `@` in the email, or adding `?set=` to Q6.
- Pressing Check while Render is asleep.

## 8. Computed-answer endpoints — Q2 headers, Q10 git forensics, Q11 cosine search

These three are graded by `/backendVerify` on a pasted **answer**, not a submitted URL. The API computes the answer from the student's own data so the solver does not need to parse git streams or reproduce the seeded embeddings in the browser. Same exam signature as Q15, so one pasted `questionData` URL (any GA1 question) is enough.

| Q | Exam id | Call | Returns |
|---|---|---|---|
| Q11 | `q-cosine-similarity-server` | `GET {ORIGIN}/ga1/{email}/answers/cosine` | `answer_text` = JSON `{"Q001":["D000111",…5],…10 queries}`; no private URL needed |
| Q10 | `q-git-forensics-token-server` | `POST {ORIGIN}/ga1/{email}/answers/git-forensics` body `{"question_data_url":"…"}` | `answer_text` = `{"token":"stg_…","commit_subject":"…"}` |
| Q2 | `q-http-headers-server` | `POST {ORIGIN}/ga1/{email}/answers/headers` body `{"question_data_url":"…"}` | `answer_text` = the `X-Exam-Code` value |

`question_data_url` is validated (host `exam.sanand.workers.dev`, email must match, question must be a GA1 id, `path` optional); if omitted the signature saved by `/onboard` is used. Errors: `400 VALID_QUESTION_DATA_URL_REQUIRED`, `409 POST_YOUR_QUESTION_DATA_URL_OR_ONBOARD_FIRST`, `502 UPSTREAM_REJECTED` with `upstream_status` 401/403 (expired signature), `422 NO_STG_TOKEN_IN_HISTORY` / `NO_X_EXAM_CODE_HEADER`. Responses are `Cache-Control: no-store`.

Notes:
- The headers code **rotates every hour**; call the endpoint right before pressing Check.
- Git forensics replays the fast-import stream byte-exactly and returns the commit that *introduced* the token (not the later one that revoked it). Verified against real `git fast-import` + `git log -S`.
- Cosine: ties break by smaller `doc_id`; the dataset uses seed `tds-2026-05-ga3-cosine-sim-client-v1#{email}#` and is verified bit-for-bit against Node `seedrandom`.

Solver module pattern (Q11 shown; the others differ only in call and prompt for the URL):

```js
import { normalizeEmail } from './utils.js';
import { T3_GA1_API_ORIGIN } from './api-client.js';

export const id = 'q-cosine-similarity-server';
export const title = 'Q11: Cosine Similarity Search (VecSearch Labs)';

export async function solve(email) {
  const norm = normalizeEmail(email);
  const r = await fetch(`${T3_GA1_API_ORIGIN}/ga1/${encodeURIComponent(norm)}/answers/cosine`);
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || `HTTP ${r.status}`);
  return { type: 'solved', answer: data.answer_text, variant: 'Computed from your seeded corpus',
           answerDisplay: ['### ' + title, '```json', data.answer_text, '```'].join('
') };
}
```

For Q10/Q2 use `prompt()` for the signed URL exactly like Q15 (section 5), `POST` it as `{question_data_url}`, and return `data.answer_text`. Keep the URL out of storage and logs.

## 9. Not implemented on purpose

- **Faking exam checks in the browser.** Some public helpers patch `window.fetch` on the exam page to answer `/effective-config`, the GitHub-Pages proxy, or the AI Pipe model calls locally. The result is a green check that the real grader never gave. These are not ported here.
- **Q13 termlog automation.** Producing the signed recording on a server means handing it the student's Google login (`auth.json`), and the recording is the proof that the student ran the commands. Use the guided manual flow in `Q13_IMPLEMENTATION_GUIDE.md`.
- **Q1/Q3/Q4/Q5/Q7/Q8/Q9/Q12/Q16.** These are local-tool, file or live-model tasks with no server component; they stay in the browser solver.
