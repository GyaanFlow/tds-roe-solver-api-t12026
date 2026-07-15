# Q6 Korean Audio Solver — Current State

## Root Cause (why it fails for some users)

The Q6 solver requires **Gemini API access** to transcribe Korean audio. The grader sends `audio_base64` (WAV/MP3), and Gemini is the only reliable transcription method we have.

**The problem:** We use the student's JWT as the AIPIPE_TOKEN. Many student JWTs don't have Gemini permissions (they get `401` on Gemini routes). The HypeMonk reference works because it uses a **single hardcoded token** — the person deploying it puts their own token that has Gemini. Our multi-tenant system can't guarantee every JWT has Gemini.

## What we added to fix it

| Fix | Where | Status |
|-----|-------|--------|
| Server env `AIPIPE_TOKEN` as last-resort fallback | `get_tenant_config()` → `server_token` | committed (`31cc5b6`) |
| Whisper (OpenAI `/audio/transcriptions`) as Gemini fallback | `_whisper_transcribe()` in solvers.py | committed (`31cc5b6`) |
| Fixed Whisper URL to use student's API base | `_whisper_transcribe()` | committed (`afaa96d`) |
| 30s timeout on Gemini (was 10s, grader budget ~12s) | `gemini_timeout` param | committed (`31cc5b6`) |

## How the transcription chain works (after fixes)

```
1. Gemini (JWT → stored token → server env token, 30s timeout)
2. Whisper (if Gemini failed, via JWT or stored token)
3. CSV/gzip/zip decode (if both audio transcriptions failed)
4. LLM extraction (gpt-4o-mini → gpt-4o fallback)
5. Stats computation (mean, std, variance, min, max, median, mode, range, correlation, etc.)
```

## HypeMonk Reference Analysis

HypeMonk (`q6_audio_standalone.py`) was shared as a working reference. Key observations:

- **Single user:** `EMAIL` and `AIPIPE_TOKEN` hardcoded at top — NOT multi-tenant
- **Gemini ONLY:** No Whisper, no GPT-4o audio, no OpenRouter (but their token has Gemini!)
- **120s timeout** on Gemini (we use 30s to fit grader's ~12s budget — generous, might need tuning)
- **Debug endpoints:** `/debug`, `/transcripts`, `/last-audio` for troubleshooting
- **Multipart handling:** Captures raw body, handles both JSON and multipart/form-data
- **Correlation from data:** Computes correlation sign from numeric columns when transcript doesn't specify
- **Stats selection:** Logic to decide which stats to return based on explicit_stats vs requested_stats vs FULL list
- **Same prompt** as our current code (Rule 6 for constraint extraction)

**What we still need to port:**
1. Debug info tracking + debug endpoints (most important)
2. Cleaner correlation/stats selection logic

## Remaining risk

The server env `AIPIPE_TOKEN` must be set on Render (`AIPIPE_TOKEN` env var) with a token that has **both**:
- OpenAI chat API access (for gpt-4o-mini LLM extraction)
- Gemini audio transcription access (for Korean audio → transcript)

Without this, students whose JWTs lack Gemini will still fail.
