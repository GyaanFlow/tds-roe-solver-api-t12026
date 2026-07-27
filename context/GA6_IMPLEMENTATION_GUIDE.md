# TDS GA6 "Web Scraping" — Implementation Guide (All 10 Questions)

Compiled by decompiling `https://exam.sanand.workers.dev/exam-tds-2026-05-ga6.js` directly (the
bundle ships all ten question generators as readable, if minified, JS) and cross-verifying every
seeded-derivation claim against the **real npm packages** the exam itself imports — not just this
guide's own reimplementation. Anything marked "verified" was checked bit-for-bit against Node
running the actual library; anything marked "read, not yet verified" was decompiled but not
independently cross-checked with a second implementation.

Only **Q7** is built as a live API in this repo (`T22026/GA6/`). This guide covers all ten so you can
implement whichever ones are worth it in your own stack.

---

## The one fact that decides everything: where does the per-student randomness come from?

Every GA6 question seeds its data from the student's email via `seedrandom`, imported one of two ways:

- **`seedrandom/lib/alea`** (the Alea algorithm specifically) — used by Q7 and Q2. Confirmed by
  reading the bundle's own vendor chunk: the module's export is `this.alea = <factory>` directly, not
  the whole `seedrandom` package.
- **`seedrandom` (the default import)** — used by the external `table.js` helper Q8/Q9 depend on, and
  it defaults to **ARC4**, a *different* algorithm from Alea. Getting this distinction wrong produces
  numbers that look plausible but are completely wrong — there is no error, no exception, just a
  silently incorrect derivation. Always confirm which one you're porting before trusting a value.

That distinction is *the* recurring trap in this exam bundle. Confirm it per-question before writing
code, don't assume.

---

## Quick verdict table

| Q | Title | Verdict | Why |
|---|---|---|---|
| 1 | Image forensics: rotated/mirrored grid | **Guide-only** | Fetches the actual puzzle BMP from `./questionData?...&quizSign=...` — `quizSign` is a live, per-session signed token, not derivable from email. |
| 2 | The Multi-Model Robustness Audit | **API-able** | Entirely seeded from email; a pure combinatorial optimization, zero external calls. Not yet built here. |
| 3 | DuckDB multi-table regression | **Guide-only** | Data is generated *and queried* inside an in-browser DuckDB-WASM instance. The thresholds are on the page; there's no data to fetch — just a SQL template to write. |
| 4 | Playwright: shadow-DOM incident audit | **Guide-only (hard to automate)** | Data is seeded, but delivered as a client-generated HTML file with async-rendered shadow DOM the student downloads and drives with a real browser. Re-deriving the data is possible in principle; replicating the render/reconciliation semantics is a much bigger job than Q7. |
| 5 | DuckDB nested-JSON ledger reconciliation | **API-able** | Seeded, delivered as static downloadable JSONL/CSV files (not a live DuckDB-WASM session) — a pure data problem. Not yet built here. |
| 6 | Crawl a static site respecting robots.txt | **API-able** | The entire "site" (robots.txt + HTML pages) is generated client-side from the seed, zipped, and downloaded — there is no live external site. Not yet built here. |
| 7 | Scrape Books to Scrape by category/value | **Built** (`T22026/GA6/`) | Real, external, static site; only the assignment is seeded. |
| 8 | GitHub Action + Playwright: scrape & sum tables | **Guide-only** | Requires the student's own GitHub repo, PAT, and a real Action run. Inherently personal infrastructure. |
| 9 | Sum table values with Playwright | **API-able** | Despite the title, verification only checks a plain integer sum — no browser automation is actually required if you replicate the (trivial, ARC4-seeded) table generator. Not yet built here. |
| 10 | Decode a hidden modem signal in audio | **Guide-only** | WAV is fetched from `/backendVerify` on the live exam server — not something outside visibility can regenerate. |

Four more questions (2, 5, 6, 9) turn out to be legitimately API-able, on top of Q7. None are built yet
— say the word and I'll add whichever you want next.

---

## Q1 — Image forensics: recover a rotated/mirrored grid (guide-only)

```
GET ./questionData?email={email}&quizSign={quizSign}&questionId=q-rotated-image-grid-forensics-server&version=v1
  credentials: same-origin   →  returns a 600×600 BMP
POST /backendVerify  { email, quizSign, response, weight, questionId, version }
```

`quizSign` is issued by the exam page when the student's session starts and isn't derivable from
email. **Do it in the browser.** The puzzle: a 6×6 grid of 36 tiles, each independently rotated by a
multiple of 90° and optionally mirrored, all permuted. Reconstruct losslessly (Python + Pillow: try
all 8 orientations — 4 rotations × mirror — per tile against every open edge-matching slot; a proper
seam-matching solver, not brute-force placement, since 36! permutations is intractable but edge-pixel
matching between tile borders converges fast) and read the token printed across the reassembled
centre.

---

## Q2 — The Multi-Model Robustness Audit (API-able, not yet built)

Fully seeded, zero external calls — a pure optimization problem. Verified reading (not yet
cross-checked against a second implementation the way Q7's Alea port was).

**Seed** (Alea, `${email}#q-minimal-prompt-robustness`):

```
e(lo, hi) = lo + rng() * (hi - lo)
models = ["gpt-4o", "gpt-4.1", "gpt-4.1-mini", "gpt-5-mini"]
biases = {
  "gpt-4o":        round(e(-2.5, -1)   * 100) / 100,
  "gpt-4.1":       round(e(-2,   -0.5) * 100) / 100,
  "gpt-4.1-mini":  round(e(-3.5, -2)   * 100) / 100,
  "gpt-5-mini":    round(e(-1.5,  0.5) * 100) / 100,
}
# 21 fixed instruction texts (verbatim strings in the bundle, e.g. "Step-by-step.", "Act as Expert.", ...)
instructions = []
for c in 0..20:
    contribs = {}
    for model in models:
        d = e(-0.4, 1.4)
        if model == "gpt-5-mini"   and c < 6:  d -= 0.6
        if model == "gpt-4.1-mini" and c > 15: d += 0.5
        contribs[model] = round(d * 100) / 100
    instructions.append({id: f"I{c+1}", text: FIXED_TEXTS[c], word_count: floor(e(5, 18)), contribs})

interactions = []   # pairwise bonuses, up to 50 draws, deduped by unordered id pair
for c in 0..49:
    n, r = floor(rng()*21), floor(rng()*21)
    if n == r: continue
    ids = sorted([f"I{n+1}", f"I{r+1}"])
    if ids not already present: interactions.append({ids, bonus: round(e(-0.7, 0.7) * 100) / 100})

meanTarget, floorTarget = 0.97, 0.92
```

**Scoring a candidate subset** `S` (a set of instruction IDs):

```
for model in models:
    c = biases[model]
    for instr in instructions:
        if instr.id in S:
            c += instr.contribs[model]
            if model == models[0]:  # gpt-4o
                word_count += instr.word_count
    for inter in interactions:
        if inter.ids[0] in S and inter.ids[1] in S:
            c += inter.bonus
    metrics[model] = sigmoid(c)   # 1 / (1 + exp(-c))

meanAcc  = average(metrics.values())
floorAcc = min(metrics.values())
```

**Task:** find the subset `S` of the 21 instructions with the **smallest word_count** such that
`meanAcc >= 0.97` and `floorAcc >= 0.92`; break ties by the **largest meanAcc**. Brute force is 2²¹ ≈
2M — trivially fast in Python directly (no need for the JS's meet-in-the-middle split), just enumerate
every bitmask, filter, and pick the best. Submit as `IDs; WC; Mean%; Floor%` (see the placeholder in
the exam UI, e.g. `I1, I5; 18; 97.45; 93.12` — note Mean%/Floor% are percentages of the 0–1 accuracy,
matched to ±0.05%).

---

## Q3 — DuckDB multi-table regression (guide-only)

Every table (`stores`, `sales_data`, `marketing_spend`) is generated **and loaded into an in-browser
DuckDB-WASM connection** by the question itself — there is nothing to fetch, no digest to compute
server-side. The seeded generator (`@faker-js/faker`, seeded via `alea` too) deliberately plants mixed
datetime formats (ISO date, ISO datetime, `MM/DD/YYYY`, `DD/MM/YYYY`) across the three tables and one
outlier "location cluster" of the first 12 stores forced into a single seeded city with an inflated
square footage floor — read the on-page description for the exact regression question and thresholds,
since those are rendered directly for the student, not computed anywhere hidden. The task is a DuckDB
SQL query the student writes and runs **in their own tab**; no API can substitute for that.

---

## Q4 — Playwright: shadow-DOM incident audit (guide-only, likely not worth automating)

Seed function `ot(email, version)` returns `{pages, scenario}`, which the question renders into a
self-contained downloadable HTML file (via a `Blob`) containing async-rendered pages with two levels
of **open shadow roots**, replayed events, and corrected revisions. The student must:

1. Open the downloaded HTML in a real browser.
2. On every page, wait for `body[data-ready="true"]`.
3. Traverse both shadow-root levels and collect only the authoritative (non-replayed, most-recent
   revision) records.
4. Produce a reconciled SRE audit and submit its digest.

The seed data is technically re-derivable (it's a pure function of email+version), but the actual
work here — resolving which of several replayed/corrected events is authoritative per page, inside a
nested shadow-DOM structure — is the point of the question and would need the full reconciliation rule
set decompiled (not done in this pass) before a server-side re-implementation would be trustworthy.
Playwright/Selenium against the downloaded file, run by the student, is the intended and most reliable
path.

---

## Q5 — DuckDB nested-JSON ledger reconciliation (API-able, not yet built)

Unlike Q3, this one does **not** need a live browser DuckDB session — the seed function `rt(email,
version)` returns `{events, fxRates, scenario}`, rendered into two **downloadable static files**:

- `events.jsonl` — one JSON object per line (`p.map(g => JSON.stringify(g)).join("\n")`)
- an FX-rate CSV: header `currency,valid_from,usd_per_unit`, one row per `fxRates` entry

The scenario description (per the on-page text) mentions: exact transport replays, old revisions,
same-sequence corrections, tombstones, two incompatible payload schemas, nested line items, and
effective-dated FX rates. Since both files are pure functions of `(email, version)`, the path to an
API here is: reimplement `rt()` in Python (not yet decompiled in this pass — the function body needs
pulling the same way Q2's `Wt()` was), generate the identical JSONL/CSV content, run the *same*
reconciliation logic the student would write in DuckDB (dedupe replays, take latest revision per
sequence, drop tombstones, normalize the two payload schemas, join effective-dated FX rates), and
return the final computed digest. This is a bigger lift than Q7 (needs the reconciliation algorithm
worked out, not just a seed), but no live external call is involved anywhere in the pipeline.

---

## Q6 — Crawl a static site respecting robots.txt (API-able, not yet built)

The seed function `lt({email, version})` returns `{pages, disallowPrefixes}`. The question builds an
entire **synthetic static site as a ZIP** (via JSZip) client-side and offers it as a download — there
is no live external site to fetch:

- `robots.txt`: `User-agent: *` plus one `Disallow: /page-{prefix}` line per seeded disallowed prefix.
- `index.html`: a catalog page linking every `page-NNNN.html`.
- `page-NNNN.html` per seeded page: embeds a `<script type="application/json" id="record">` tag with
  either the real `{id, category, price}` (if the page is allowed) or a **decoy** `{id, decoyCategory,
  decoyPrice}` (if the page falls under a disallowed prefix) — i.e. the crawler is expected to *skip*
  disallowed pages entirely and must not accidentally scrape the decoy data sitting right there in the
  HTML. Data-record schema, key order, and the final digest requirement are on the page itself (the
  same "Serialize as `{"id":...,"category":...,"price":...}`, no reformatting" pattern as Q7).

Since `lt()` is a pure function of `(email, version)`, this is directly portable: reimplement it (not
yet pulled from the bundle in this pass), generate the same page set server-side, respect the same
disallow rule, extract only the allowed records, and hash. No live site, no CORS concern, no browser
needed at all — arguably the *easiest* of the four newly-identified candidates since there's no
external network call in the loop whatsoever, just a data-generation replica.

---

## Q7 — Scrape Books to Scrape by category/value (built)

See `T22026/GA6/solvers.py` and the earlier session notes. `GET /ga6/{email}/scrape-books`. Seed:
Alea, `${email}#q-scrape-books-server`, verified bit-for-bit against the real npm
`seedrandom/lib/alea` package across 8 emails.

---

## Q8 — GitHub Action + Playwright: scrape & sum tables (guide-only)

Requires a **real GitHub Action run** in the student's own repository, with a step whose logs contain
their email, running a Playwright script that visits 10 seeded pages at
`https://sanand0.github.io/tdsdata/js_table/?seed={n}`, sums every number in every table, and prints
the total. Inherently personal infrastructure (their repo, their PAT, their Action run inspected via
GitHub's API) — no hosted API can produce or verify this on their behalf. The 10 seeds and the table
data themselves are fully deterministic (see Q9 below, which uses the *same* generator) — the personal
part is proving it ran as a real GitHub Action, not computing the sum.

---

## Q9 — Sum table values with Playwright (API-able, not yet built — and easy)

The title says Playwright, but the actual verification (`kt`) only parses an integer and compares it
to a precomputed expected sum — **no proof of browser automation is checked at all**. Fully
self-contained:

**Seed** (verified: the DEFAULT `seedrandom` import — i.e. **ARC4**, not Alea; this is the exception to the "everything is Alea" pattern, confirmed by reading `table.js`'s own `import { default as seedrandom }` line):

```
seed_rng = ARC4_seedrandom(`${email}#q-playwright-table-server`)
u = floor(seed_rng() * 90)
seeds = [str(u), str(u+1), ..., str(u+9)]   # 10 consecutive integers, as strings
```

**Table generator**, fetched live from `https://sanand0.github.io/tdsdata/js_table/table.js` (trivial,
6 lines — copy verbatim):

```js
export function generate(seed, rows, cols) {
  const random = seedrandom(seed);   // ARC4 again, seeded with the seed STRING directly (not "email#...")
  return Array.from({ length: rows }, () =>
    Array.from({ length: cols }, () => Math.round(random() * 1000)));
}
```

**Expected answer:**

```
expected = sum(
    sum(cell for row in generate(seed, 50, 10) for cell in row)
    for seed in seeds
)
```

To build this as an API: port ARC4 `seedrandom` to Python (a well-documented, standard algorithm —
different from the Alea port already done for Q7, don't reuse that code), verify it against
`node -e "require('seedrandom')(...)"` for a few seeds exactly the way the Alea port was verified, then
port the 6-line `generate()` function, sum, and return the integer. This is likely the **lowest-effort
of the four remaining candidates** — no scenario/reconciliation logic to reverse-engineer, just one
PRNG port and a sum.

---

## Q10 — Decode a hidden modem signal in audio (guide-only)

```
POST /backendVerify  (fetches the WAV, per session)
```

The WAV containing the modem-encoded signal is fetched from the live exam server per the student's own
session — not something visible or regenerable from outside that session. **Do it in the browser /
locally with the downloaded WAV**: this is an FSK/AFSK-style demodulation task (decode a hidden digital
signal embedded in audio) — use a tool like `minimodem`, or a Python FFT-based bit-slicing script once
you have the actual WAV file in hand, which only the student's live session can produce.

---

## If you want the next one built

Ranked by effort-to-value for a hosted API, cheapest first:

1. **Q9** — one ARC4 PRNG port + a 6-line table generator + a sum. Smallest, safest addition.
2. **Q2** — seed generator is fully decompiled above; the "hard part" is just enumerating 2²¹ bitmasks
   in Python, which is fast and simple. No external calls at all.
3. **Q6** — needs `lt()` pulled from the bundle (not yet done), but no live network call once that's
   done.
4. **Q5** — needs `rt()` pulled from the bundle plus the reconciliation algorithm worked out; the
   biggest of the four, but still no live external dependency.
5. **Q4** — possible in principle, but the reconciliation-rule decoding is substantial and the intended
   solving path (real Playwright against a rendered shadow-DOM page) is genuinely well-suited to a
   real browser; lowest priority to fake server-side.
