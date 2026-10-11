# Connect the T3 GA1 APIs to the browser solver

This is the browser-solver integration guide, separate from [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md), which explains deploying the API itself. Follow this when wiring the live API hub into the separate `tds-roe-solver` project, using the T2 GA1 `solved` result + `guide` pattern.

The browser solver is at `C:/Users/gaura/Downloads/tds-roe-solver/tds-roe-solver`. Its T3 GA1 API modules currently return “implementation pending” handoff cards. The API repo is separate: do not paste its private `quizSign` into solver source or browser storage.

## How the two projects fit together

1. Deploy the API hub and open its `/ga1/` dashboard.
2. Onboard the learner's exam email and complete signed Ledger `questionData` URL there. The API validates it and stores the signature privately for Q15.
3. In the browser solver, the T3 solver receives the normalized email and constructs the corresponding public route.
4. The solver returns that route as its `answer`, just like the older T2 API solvers.
5. The exam grader calls the submitted API URL live. A generated URL is not proof that the service is healthy; use the dashboard test bench and official grader to verify it.

## Files to edit in the browser-solver project

- `solvers/T32026/ga1/q06-config-precedence.js`
- `solvers/T32026/ga1/q14-mcp-server.js`
- `solvers/T32026/ga1/q15-ledger-agent.js`
- `solvers/T32026/ga1/registry.js` only if IDs/order change (normally they should not)
- Add a shared helper such as `solvers/T32026/ga1/api-client.js` for the deployed origin and URL validation.

Keep the exact official IDs and titles. The registry already lists the modules in official order, and its `apiHandoffQuestions` metadata may remain as a note that these answers are served by a separate API project; it is not a solver import.

## 1. Configure the deployed API origin once

Create `solvers/T32026/ga1/api-client.js` in the browser-solver repo. Replace the placeholder with the API service's public HTTPS origin (no `/ga1` suffix). Do not invent a host or use localhost in a submitted answer.

```js
import { normalizeEmail } from './utils.js';

export const T3_GA1_API_ORIGIN = 'https://REPLACE-WITH-THE-DEPLOYED-API-HOST';

export function buildT3Ga1Url(email, suffix) {
  const normalized = normalizeEmail(email);
  if (!normalized || !normalized.includes('@')) {
    throw new Error('A valid registered email is required to build the GA1 API URL.');
  }
  if (!T3_GA1_API_ORIGIN.startsWith('https://')) {
    throw new Error('Set T3_GA1_API_ORIGIN to the public HTTPS API origin.');
  }
  return `${T3_GA1_API_ORIGIN.replace(/\/$/, '')}/ga1/${encodeURIComponent(normalized)}${suffix}`;
}

export function makeApiAnswer(title, url, notes) {
  return {
    type: 'solved',
    answer: url,
    variant: `Live T3 GA1 endpoint for ${url}`,
    answerDisplay: [
      `### ${title}`,
      '',
      '**Submit this endpoint URL:**',
      '```text',
      url,
      '```',
      '',
      notes,
    ].join('\n'),
    guide: notes,
    debug: { integrationStatus: 'url-generated', apiEndpoint: url },
  };
}
```

The API hub's onboarding response also returns these routes. Using `buildT3Ga1Url` keeps the solver convention consistent and avoids hardcoding a learner email. If the deployed service changes domains, update only the origin constant.

## 2. Replace the three pending modules

### Q6 — config precedence

In `q06-config-precedence.js`, keep the exported `id` and `title`, and replace the pending `solve()` body with:

```js
import { buildT3Ga1Url, makeApiAnswer } from './api-client.js';

export async function solve(email) {
  const url = buildT3Ga1Url(email, '/effective-config');
  return makeApiAnswer(
    title,
    url,
    [
      'The grader sends fresh repeated `set=key=value` query parameters to this URL.',
      'The API applies CLI overrides, checks numeric and boolean types, maps `num_workers` to `workers`, and masks `api_key`.',
      'Test it in the API dashboard with multiple `set` parameters before submitting.',
    ].join('\n'),
  );
}
```

The grader appends query parameters to the endpoint. Do not append a sample `?set=` value to the answer URL; that would pin the endpoint to a test case and interfere with fresh randomized checks.

### Q14 — live MCP server

In `q14-mcp-server.js`, preserve its ID/title and use:

```js
import { buildT3Ga1Url, makeApiAnswer } from './api-client.js';

export async function solve(email) {
  const url = buildT3Ga1Url(email, '/mcp');
  return makeApiAnswer(
    title,
    url,
    [
      'The API exposes one `solve_challenge` MCP tool.',
      'Every tool call reads its fresh `X-Exam-Challenge` header and hashes it with the normalized email.',
      'Use the API dashboard MCP bench to verify initialize, tools/list, and multiple fresh challenges.',
    ].join('\n'),
  );
}
```

Do not compute a challenge digest in the browser solver. The grader sends a new challenge header to the deployed endpoint each time; the service must compute each response live.

### Q15 — Ledger Agent

In `q15-ledger-agent.js`, preserve its ID/title and use:

```js
import { buildT3Ga1Url, makeApiAnswer } from './api-client.js';

export async function solve(email) {
  const url = buildT3Ga1Url(email, '/ledger/answer');
  return makeApiAnswer(
    title,
    url,
    [
      'Before testing, onboard this email and its full signed Ledger `questionData` URL in the API dashboard.',
      'The grader POSTs JSON such as `{"question":"..."}` and expects JSON containing an `answer` field.',
      'Use the dashboard to inspect the schema manifest and try revenue, refund, product, and customer questions.',
    ].join('\n'),
  );
}
```

The browser solver must not fetch or embed the private Ledger dataset or signed questionData URL. The API hub fetches data server-side using the signature stored during onboarding; the route returned by the solver is only the public answer endpoint.

## 3. Keep the normal registry and runtime flow

`solvers/T32026/ga1/registry.js` imports these modules and wraps them with `wrapSolverModule`. Do not bypass that wrapper: it validates the learner email, checks the result shape, measures duration, and converts thrown failures into a visible structured error. Each API module should return the wrapper's supported shape (`type: 'solved'`, a non-empty string `answer`, optional `guide`/`debug`).

Do not return `makeGuideResult(...)` for a completed API handoff; it sets `type: 'guide'` and presents the answer as pending. Keep guide text for setup details, but return the endpoint URL in `answer` so the solver can copy/submit it like T2.

## 4. Live test bench procedure

Open the deployed API hub's `/ga1/` dashboard, enter the same email, paste that student's full signed Ledger `questionData` URL, and run each service-specific check:

- **Q6:** run the config override check. Confirm the response contains all five expected keys, with integer `port`/`workers`, boolean `debug`, and masked `api_key`.
- **Q14:** run the MCP handshake. Confirm exactly one tool named `solve_challenge`, then verify the response against a fresh header challenge.
- **Q15:** discover the Ledger schema, then try more than the dashboard's example question. Check date/region filters and compare totals against the discovered records; do not accept a plausible-looking total without checking the source rows.

After changing solver modules, run the browser-solver regression checks from that repository:

```powershell
node check.mjs --t3-ga1-only
node check.mjs --t3-ga1-scale
```

Then open the T3 GA1 solver in the app, confirm each module displays a `solved` result with the correct live endpoint, and submit through the official exam verifier. Local checks do not replace live grading or a concurrent-load test.

## Common mistakes

- Returning the API's `/onboard` URL instead of the question-specific endpoint.
- Omitting `/ga1/{encoded-email}` from the route.
- Hardcoding one email, quiz signature, or MCP challenge.
- Adding a fixed config query string to Q6's URL.
- Returning a guide-only result after the API is deployed.
- Treating successful URL construction or an HTTP 200 as proof that hidden Ledger questions are correct.
- Editing the current user's API origin in three separate question modules instead of the shared helper.
