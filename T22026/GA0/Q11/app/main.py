from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

APP_NAME = "T22026 GA0 Q11 Batch Sentiment API"
APP_VERSION = "1.0.0"
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "2000"))
MAX_SENTENCE_LENGTH = int(os.getenv("MAX_SENTENCE_LENGTH", "2000"))

analyzer = SentimentIntensityAnalyzer()


class SentencesRequest(BaseModel):
    sentences: List[str] = Field(..., min_length=1, max_length=MAX_BATCH_SIZE)


class SentimentItem(BaseModel):
    sentence: str
    sentiment: str


class SentimentResponse(BaseModel):
    results: List[SentimentItem]


def classify(text: str) -> str:
    score = analyzer.polarity_scores(text).get("compound", 0.0)
    if score >= 0.05:
        return "happy"
    if score <= -0.05:
        return "sad"
    return "neutral"


app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": APP_NAME,
        "version": APP_VERSION,
        "max_batch_size": MAX_BATCH_SIZE,
    }


@app.post("/sentiment", response_model=SentimentResponse)
def sentiment_batch(req: SentencesRequest) -> SentimentResponse:
    if len(req.sentences) > MAX_BATCH_SIZE:
        raise HTTPException(status_code=400, detail=f"Batch too large. Max {MAX_BATCH_SIZE} sentences.")

    items: List[SentimentItem] = []
    for raw in req.sentences:
        text = "" if raw is None else str(raw)
        if len(text) > MAX_SENTENCE_LENGTH:
            raise HTTPException(status_code=400, detail=f"Sentence too long. Max {MAX_SENTENCE_LENGTH} chars.")
        items.append(SentimentItem(sentence=text, sentiment=classify(text)))

    return SentimentResponse(results=items)


@app.post("/ga0/q11/sentiment", response_model=SentimentResponse)
def sentiment_batch_ga0_q11(req: SentencesRequest) -> SentimentResponse:
    return sentiment_batch(req)


@app.post("/q11/sentiment", response_model=SentimentResponse)
def sentiment_batch_q11_alias(req: SentencesRequest) -> SentimentResponse:
    return sentiment_batch(req)


@app.post("/t22026/ga0/q11/sentiment", response_model=SentimentResponse)
def sentiment_batch_t22026_ga0_q11(req: SentencesRequest) -> SentimentResponse:
    return sentiment_batch(req)


# ── Exam-canonical route ──────────────────────────────────────────────────────
# The exam validator takes the submitted URL and calls POST {url} directly.
# Students should submit: https://<host>/q11/q-fastapi-sentiment-batch/sentiment
# The exam then calls:    POST  https://<host>/q11/q-fastapi-sentiment-batch/sentiment
@app.post("/q-fastapi-sentiment-batch/sentiment", response_model=SentimentResponse)
def sentiment_batch_exam_canonical(req: SentencesRequest) -> SentimentResponse:
    return sentiment_batch(req)

Q11_UI = """<!doctype html>
<html>
<head>
  <meta charset='utf-8'>
  <meta name='viewport' content='width=device-width,initial-scale=1'>
  <title>Q11 - FastAPI Batch Sentiment Solver</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --primary: #10b981;
      --primary-hover: #059669;
      --primary-glow: rgba(16, 185, 129, 0.25);
      --bg: #090d16;
      --card-bg: rgba(17, 24, 39, 0.7);
      --border: rgba(255, 255, 255, 0.08);
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at top left, #090d16, #062016, #090d16);
      color: var(--text);
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .wrap {
      width: 100%;
      max-width: 800px;
      padding: 24px;
      box-sizing: border-box;
    }
    .card {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--border);
      border-radius: 24px;
      padding: 32px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
    }
    h2 {
      margin-top: 0;
      font-weight: 700;
      font-size: 1.8rem;
      background: linear-gradient(to right, #34d399, #10b981);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 8px;
    }
    p {
      color: var(--text-muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }
    .routes {
      background: rgba(15, 23, 42, 0.6);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 12px;
      font-size: 0.85rem;
      margin-bottom: 24px;
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
    }
    .routes code {
      color: #34d399;
    }
    .submit-container {
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      border-radius: 16px;
      padding: 20px;
      margin-bottom: 28px;
      text-align: center;
    }
    .submit-title {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #a7f3d0;
      font-weight: 600;
      margin-bottom: 8px;
    }
    .submit-url-box {
      background: rgba(15, 23, 42, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 12px;
      padding: 12px;
      font-family: monospace;
      font-size: 0.95rem;
      color: #34d399;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      word-break: break-all;
    }
    .btn-copy {
      background: #059669;
      color: white;
      border: none;
      padding: 6px 12px;
      border-radius: 8px;
      cursor: pointer;
      font-family: 'Plus Jakarta Sans', sans-serif;
      font-size: 0.8rem;
      font-weight: 600;
      transition: all 0.2s;
    }
    .btn-copy:hover {
      background: #047857;
    }
    .form-group {
      margin-bottom: 24px;
    }
    label {
      display: block;
      font-weight: 500;
      margin-bottom: 8px;
      font-size: 0.9rem;
      color: #e2e8f0;
    }
    textarea {
      width: 100%;
      padding: 14px 16px;
      background: rgba(15, 23, 42, 0.5);
      border: 1px solid var(--border);
      border-radius: 12px;
      color: var(--text);
      font-family: inherit;
      font-size: 0.95rem;
      transition: all 0.3s;
      box-sizing: border-box;
      resize: vertical;
    }
    textarea:focus {
      outline: none;
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-glow);
    }
    button.btn-solve {
      width: 100%;
      background: linear-gradient(135deg, #10b981, #059669);
      color: #fff;
      border: 0;
      padding: 14px;
      font-size: 1rem;
      font-weight: 600;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.3s;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
    }
    button.btn-solve:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(16, 185, 129, 0.35);
    }
    button.btn-solve:active {
      transform: translateY(0);
    }
    .results-area {
      margin-top: 28px;
      display: none;
    }
    .grid {
      display: grid;
      gap: 12px;
      margin-top: 16px;
      max-height: 320px;
      overflow-y: auto;
      padding-right: 4px;
    }
    .item {
      padding: 16px;
      border-radius: 12px;
      background: rgba(15, 23, 42, 0.4);
      border: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
    }
    .sentence-text {
      font-size: 0.9rem;
      line-height: 1.4;
    }
    .tag {
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      border: 1px solid transparent;
    }
    .happy {
      background: rgba(16, 185, 129, 0.15);
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.3);
    }
    .sad {
      background: rgba(239, 68, 68, 0.15);
      color: #fca5a5;
      border-color: rgba(239, 68, 68, 0.3);
    }
    .neutral {
      background: rgba(148, 163, 184, 0.15);
      color: #cbd5e1;
      border-color: rgba(148, 163, 184, 0.3);
    }
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: #10b981;
      color: white;
      padding: 12px 24px;
      border-radius: 8px;
      font-weight: 600;
      box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);
      transform: translateY(100px);
      opacity: 0;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .toast.show {
      transform: translateY(0);
      opacity: 1;
    }
  </style>
</head>
<body>
  <div class='wrap'>
    <div class='card'>
      <h2>T22026 GA0 Q11: Sentiment API Service</h2>
      <p>FastAPI microservice running robust batch sentiment analysis using VADER Sentiment Intensity Analyzer.</p>
      
      <div class='routes'>
        <span>Exam Canonical: <code>/q-fastapi-sentiment-batch/sentiment</code></span>
      </div>

      <div class='submit-container'>
        <div class='submit-title'>Submit this endpoint URL on the exam page</div>
        <div class='submit-url-box'>
          <span id='sub-url'></span>
          <button class='btn-copy' onclick='copyEndpoint()'>Copy URL</button>
        </div>
        <p style="margin: 8px 0 0; font-size: 0.85rem; color: #10b981; font-weight: 600;">✅ SUBMIT THIS URL FOR Q11</p>
      </div>

      <div class='form-group'>
      </div>
    </div>
  </div>

  <div id="toast" class="toast">Copied to clipboard!</div>

  <script>
    // Exam validator calls POST {url} directly — submit the full /sentiment path
    const prefix = window.location.origin;
    document.getElementById('sub-url').textContent = prefix + '/q-fastapi-sentiment-batch/sentiment';

    function copyEndpoint() {
      const url = document.getElementById('sub-url').textContent;
      navigator.clipboard.writeText(url);
      showToast();
    }

    function showToast() {
      const t = document.getElementById('toast');
      t.classList.add('show');
      setTimeout(() => t.classList.remove('show'), 2000);
    }
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def q11_home() -> str:
    return Q11_UI


@app.get("/sentiment", response_class=HTMLResponse)
def q11_sentiment_page() -> str:
    return Q11_UI


@app.get("/q11/sentiment", response_class=HTMLResponse)
def q11_sentiment_page_alias() -> str:
    return Q11_UI





