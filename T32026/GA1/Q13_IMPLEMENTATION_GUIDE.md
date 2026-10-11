# Q13 — terminal decoding helper

Official question ID: `q-termlog-rec-server` (Decode it in the terminal).

**This is a helper API, not a submit-ready answer API.** The official exam
requires a publicly downloadable `submission.tar.gz` containing the student's
own `demo.cast` and Google-signed `demo.cast.jwt`. The code rotates every three
hours. Fetch and decode the current challenge within the same recording.
This service does not log in, sign recordings, execute submitted code, create
archives, or claim grader acceptance.

## API contract

POST `/ga1/q13/decode` on the mounted hub, or `/q13/decode` on the standalone
GA1 app. `/ga1/{encoded-email}/q13/decode` is also supported, but the decoder
is stateless and needs neither an email nor Ledger onboarding.

Request:

```json
{"ciphertext":"6162"}
```

Supply the encoded string or the complete text response from curl, including
its `#` comment lines. Do **not** supply JSON, a curl command, secret URL, or
quizSign. No outbound fetch occurs. The input is limited to 16,384 ASCII
characters (32 KiB JSON request). Blank lines and `#` comments are ignored;
exactly one payload line must remain. Surrounding whitespace is removed;
internal whitespace is not silently rewritten.

Response fields:

- `status`: `unique_readable_candidate`, `ambiguous`, or `no_readable_candidate`.
- `answer`: plaintext only if exactly one distinct readable candidate exists;
  otherwise `null`. Readability does not establish that this is the correct code.
- `candidates`: all distinct readable UTF-8 plaintexts with `decode_orders` and
  matching `shell_pipelines`. Orders are the **undo** sequence, not encoding order.
- `submission_type`: `public_url_of_signed_termlog_archive`.

The service tries all six permutations of ROT13, hex decoding, and whole-string
reversal. Some operations commute, and multiple valid outputs can exist. There
is no general way to prove the intended plaintext from these transforms alone
without additional challenge constraints. Inspect candidates against the actual
challenge's code format; do not auto-submit an arbitrary first candidate.

HTTP 200 means readable candidates exist (possibly ambiguous), 422 means none,
400 means invalid input, and 413 means the JSON body exceeds the limit. Responses
use `Cache-Control: no-store`. No input or plaintext is saved in the tenant store.

## Browser-solver integration

Use the shared `T3_GA1_API_ORIGIN` helper from `SOLVER_INTEGRATION_GUIDE.md`:

```js
import { T3_GA1_API_ORIGIN } from './api-client.js';

export async function getQ13DecodeHelp(ciphertext) {
  const r = await fetch(`${T3_GA1_API_ORIGIN.replace(/\/$/, '')}/ga1/q13/decode`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ciphertext }),
  });
  const data = await r.json();
  if (!r.ok) throw new Error(data.error || data.status || `HTTP ${r.status}`);
  return data;
}
```

Show candidates and instructions as guidance, **not** `makeApiAnswer(...)`.
Q13's final answer field must contain the student's public archive URL. Do not
persist ciphertext, plaintext, or signed questionData URLs in browser storage.

## Genuine terminal workflow (Linux / WSL / macOS)

Install and log in to termlog following its official documentation at
<https://github.com/mynkpdr/termlog>, using the student's own Google account.
Have `curl`, `tr`, `xxd`, Python 3, and `tar` available.

```sh
termlog login
termlog rec demo.cast
```

Inside the recording, fetch the current challenge. In Bash, hidden input keeps
the signed URL out of the terminal transcript; do not type passwords or keys:

```sh
read -r -s -p 'Paste your Q13 challenge URL: ' CHALLENGE_URL
printf '\n'
curl --fail --silent --show-error "$CHALLENGE_URL" -o cipher.txt
unset CHALLENGE_URL
cat cipher.txt
```

The observed challenge is plain text: `#` comments followed by a ciphertext
line. The fetch command above saves it as `cipher.txt`. You may also extract
its ciphertext line; the helper accepts either form.
If your response is an error or another format, inspect it rather than passing
it as ciphertext. Ask the dashboard helper for candidates, then run the chosen
pipeline **locally in the recording** against `cipher.txt`. For example, if the
reported undo order is hex → reverse → ROT13:

```sh
python3 -c 'import sys; lines=[s.strip() for s in sys.stdin.buffer.read().decode("ascii").splitlines() if s.strip() and not s.lstrip().startswith("#")]; assert len(lines)==1, "Expected one ciphertext line"; sys.stdout.buffer.write(lines[0].encode("ascii"))' < cipher.txt | xxd -r -p | python3 -c 'import sys; sys.stdout.buffer.write(sys.stdin.buffer.read().decode("utf-8")[::-1].encode("utf-8"))' | LC_ALL=C tr 'A-Za-z' 'N-ZA-Mn-za-m'
printf '\n'
```

Use the order returned for the current challenge, not necessarily this example.
`rev` reverses each line separately; Python's stdin reversal is used here so
the pipeline also handles whole-string reversal across multiple lines. Binary
stdin/stdout preserves CRLF and UTF-8 without newline translation. Never
execute the decoded plaintext as a command. API-side decoding alone does not
replace the exam's local shell-decoding requirement.

Finish and package outside the recording:

```sh
exit
tar -czf submission.tar.gz demo.cast demo.cast.jwt
```

Upload the archive to a location the exam server can fetch without login, then
submit its public URL. Keep local challenge data private. The official grader
is the authority on recording/signature validity.

## Validation and deployment

Run `python -m pytest tests/test_t32026_ga1.py tests/test_t32026_ga1_q13.py -q`.
Tests cover 250 generated strings across all six permutations (1,500 cases),
candidate round-trips, ambiguity, Unicode/multiline plaintext, input limits,
stateless tenant aliases, mounted hub middleware, real shell pipelines against
safe fixtures (when Bash/xxd/tr are installed), and existing GA1 regressions.
Tests also cover the observed commented response and 100 concurrent local
student requests. These are synthetic
decoder/API tests, not end-to-end official recording-grader validation.

The existing GA1 router mounting exposes this route when the updated code is
deployed. No new dependencies or service secrets are required. Redeploying a
host with ephemeral SQLite can erase existing Ledger registrations: configure
`GA1_REDIS_URL` or a persistent tenant database volume before relying on durable
multi-student onboarding. Merely changing local code does not update Render.
