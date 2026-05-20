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


@app.post("/t22026/ga0/q11/sentiment", response_model=SentimentResponse)
def sentiment_batch_t22026_ga0_q11(req: SentencesRequest) -> SentimentResponse:
    return sentiment_batch(req)

Q11_UI = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Q11 API</title><style>body{font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(120deg,#eefcf6,#e9f1ff);margin:0}.wrap{max-width:960px;margin:24px auto;padding:20px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}textarea{width:100%;padding:10px;border:1px solid #cfd8e3;border-radius:10px}button{background:#047857;color:#fff;border:0;padding:10px 14px;border-radius:10px;cursor:pointer}.grid{display:grid;gap:10px;margin-top:12px}.item{padding:10px;border-radius:10px;background:#f8fafc;border:1px solid #e2e8f0}.tag{padding:3px 8px;border-radius:999px;font-size:12px;font-weight:700}.happy{background:#dcfce7;color:#166534}.sad{background:#fee2e2;color:#991b1b}.neutral{background:#e2e8f0;color:#334155}</style></head><body><div class='wrap'><div class='card'><h2>T22026 GA0 Q11: Sentiment API</h2><p>Routes: <code>/sentiment</code>, <code>/ga0/q11/sentiment</code>, <code>/t22026/ga0/q11/sentiment</code></p><p>Enter one sentence per line:</p><textarea id='txt' rows='8'>I love this
This is bad
It is okay</textarea><br><br><button onclick='run()'>Analyze</button><div id='out' class='grid'></div></div></div><script>async function run(){const s=document.getElementById('txt').value.split(/\\r?\\n/).filter(Boolean);const r=await fetch('ga0/q11/sentiment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({sentences:s})});const data=await r.json();const out=document.getElementById('out');if(!r.ok){out.innerHTML='<div class=\"item\">'+(data.detail||'Request failed')+'</div>';return;}out.innerHTML=(data.results||[]).map(x=>`<div class=\"item\"><div>${x.sentence}</div><div style=\"margin-top:6px\"><span class=\"tag ${x.sentiment}\">${x.sentiment}</span></div></div>`).join('');}</script></body></html>
"""

@app.get("/", response_class=HTMLResponse)
def q11_home() -> str:
    return Q11_UI


@app.get("/sentiment", response_class=HTMLResponse)
def q11_sentiment_page() -> str:
    return Q11_UI





