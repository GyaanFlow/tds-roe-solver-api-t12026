# GA6 Q7 API — Usage Guide (consuming it from another solver)

This is a **consumer** guide: how to call the already-deployed GA6 Q7 endpoint from a different
codebase, so you don't have to re-implement the seed derivation or scraper anywhere else. For how the
endpoint itself works internally, or specs for the other 9 GA6 questions, see
`GA6_IMPLEMENTATION_GUIDE.md` in this same folder.

> **Fixed since the last version of this guide:** the seed derivation was using the wrong PRNG
> algorithm (Alea instead of the real ARC4 default), which silently produced the wrong assigned
> categories/thresholds/digest for every email. If you called this endpoint before and cached the
> result, re-fetch it now — the digest for the same email has changed.

---

## Base URL

```
https://tds-roe-solver-api-t12026.onrender.com
```

---

## Endpoint

```
GET {base}/ga6/{email}/scrape-books
```

- `{email}` — the student's email, URL-encoded or not (both `test@example.com` and
  `test%40example.com` work identically — the `@` doesn't need escaping in practice, but encode it if
  your HTTP client insists).
- No auth, no token, no request body. It's a plain `GET`.
- **No email validation** — any non-empty string is accepted and deterministically hashed into a seed.
  If you pass something that isn't really an email, you'll just get a differently-seeded (but still
  internally consistent) result. Validate on your side if that matters to you.

Two path aliases exist for the same handler, in case your other solver's routing conventions expect a
question-ID-style path instead:

```
GET {base}/ga6/{email}/q7/scrape-books
GET {base}/ga6/{email}/q7
```

Health check (no email needed):

```
GET {base}/ga6/health   →  {"status": "ok"}
```

---

## Success response — `200 OK`

```json
{
  "email": "test@example.com",
  "assignedCategories": ["Academic", "Art", "Biography", "Humor", "Religion"],
  "minRating": 3,
  "minPrice": 21,
  "maxPrice": 60,
  "minAvailability": 8,
  "matchCount": 9,
  "digest": "2ba172846275719d729346b8d1e8603da1587ec5db4a76536f3563d303ca3ddc",
  "hint": "Submit only the 'digest' value (64 lowercase hex characters) to the exam question."
}
```

The field your other solver actually needs to submit to the exam is **`digest`** — a 64-character
lowercase hex SHA-256 string. Everything else is context (assigned categories/thresholds, how many
books matched) in case you want to log or display it, but the exam only wants the digest.

## Error response — `502 Bad Gateway`

```json
{
  "error": "Could not complete the live scrape of books.toscrape.com. The site may be temporarily unreachable -- try again."
}
```

This is the *only* error path — it fires if books.toscrape.com itself is unreachable or errors out
mid-scrape. There is no 4xx path for this endpoint (no auth, no body to validate, and any string is
accepted as `{email}`). **Retry on 502** — it's transient by nature (an external site hiccup), not a
sign anything is wrong with the request itself. A couple of retries with a short backoff is enough;
don't build elaborate retry logic around it.

---

## Latency

Each call does a **live** scrape: fetch the home page, discover the assigned category pages, crawl
their pagination, then fetch every matching book's detail page concurrently (up to 16 at a time).
Typical latency is **2–6 seconds** depending on how many books the student's seeded thresholds match
(anywhere from a handful to 30+ books). There's no server-side cache — set a client-side timeout of at
least 15–20 seconds to be safe, and don't call it in a tight loop.

---

## Determinism

For a **fixed email**, the assigned categories and thresholds (`assignedCategories`, `minRating`,
`minPrice`, `maxPrice`, `minAvailability`) never change — they're derived purely from the email string,
no network call involved.

The `digest` itself depends on the **live state of books.toscrape.com** at the moment of the call. In
practice this is a long-standing static demo site that essentially never changes, so repeated calls
for the same email consistently return the same digest — but it is not a mathematical guarantee the
way the threshold derivation is. If your other solver caches results, key the cache on `email` and
treat a cache-miss re-fetch as authoritative over a stale cached digest if the two ever disagree.

---

## Example calls

**curl:**

```bash
curl "https://tds-roe-solver-api-t12026.onrender.com/ga6/YOUR_EMAIL/scrape-books"
```

**Python (`requests`):**

```python
import requests

def get_ga6_q7_digest(email: str, base_url: str = "https://tds-roe-solver-api-t12026.onrender.com") -> str:
    r = requests.get(f"{base_url}/ga6/{email}/scrape-books", timeout=20)
    r.raise_for_status()  # raises on the 502 path too -- catch and retry if needed
    return r.json()["digest"]
```

**Python (async, `httpx` — matches this repo's own style if your other solver is also FastAPI):**

```python
import httpx

async def get_ga6_q7_digest(email: str, base_url: str = "https://tds-roe-solver-api-t12026.onrender.com") -> str:
    async with httpx.AsyncClient(timeout=20.0) as client:
        r = await client.get(f"{base_url}/ga6/{email}/scrape-books")
        r.raise_for_status()
        return r.json()["digest"]
```

**JavaScript / Node (`fetch`):**

```javascript
async function getGa6Q7Digest(email, baseUrl = "https://tds-roe-solver-api-t12026.onrender.com") {
  const res = await fetch(`${baseUrl}/ga6/${encodeURIComponent(email)}/scrape-books`);
  if (!res.ok) throw new Error(`GA6 Q7 API returned ${res.status}`);
  const body = await res.json();
  return body.digest;
}
```

**With a simple retry-on-502 (Python):**

```python
import time
import requests

def get_ga6_q7_digest(email, base_url="https://tds-roe-solver-api-t12026.onrender.com", retries=3):
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.get(f"{base_url}/ga6/{email}/scrape-books", timeout=20)
            if r.status_code == 502:
                last_err = r.json().get("error", "502")
                time.sleep(1.5 * (attempt + 1))
                continue
            r.raise_for_status()
            return r.json()["digest"]
        except requests.RequestException as exc:
            last_err = str(exc)
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"GA6 Q7 API failed after {retries} attempts: {last_err}")
```

---

## Wiring it into "your other solver"

If your other solver is itself an exam-answering hub (the way this repo's GA2–GA5 hubs work), the
natural place to call this is wherever it resolves a per-student answer for the GA6 Q7 question ID
(`q-scrape-books-server`): resolve the student's email the same way you already do for other
questions, call the function above, and return `{"digest": ...}` (or however your hub's response
schema is shaped) instead of re-implementing the scrape.

If your other solver is a *different* tool entirely (a script, a grading harness, a CLI) — the four
snippets above are self-contained; there's no shared state or session needed beyond the email string.
