from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

BASE = Path(__file__).resolve().parents[1]


def load_app(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load module from {file_path}")
    mod = importlib.util.module_from_spec(spec)
    # Register module so Pydantic forward-ref resolution can find typing symbols
    # under the module namespace during route/model construction.
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    if not hasattr(mod, "app"):
        raise RuntimeError(f"Module {file_path} has no 'app'")
    return mod.app


q5 = load_app("q5_app", BASE / "T22026" / "GA0" / "Q05" / "app" / "main.py")
q10 = load_app("q10_app", BASE / "T22026" / "GA0" / "Q10" / "app" / "main.py")
q11 = load_app("q11_app", BASE / "T22026" / "GA0" / "Q11" / "app" / "main.py")
q14 = load_app("q14_app", BASE / "T22026" / "GA0" / "Q14" / "app" / "main.py")
q16 = load_app("q16_app", BASE / "T22026" / "GA0" / "Q16" / "app" / "main.py")
q18 = load_app("q18_app", BASE / "T22026" / "GA0" / "Q18" / "app" / "main.py")
q19 = load_app("q19_app", BASE / "T22026" / "GA0" / "Q19" / "app" / "main.py")

app = FastAPI(title="T22026 GA0 Unified API Hub", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>T22026 API Hub</title>
<style>
:root{--bg1:#e9f4ff;--bg2:#f4ffe9;--ink:#0f172a;--muted:#475569;--card:#ffffff;--accent:#0f4c81}
*{box-sizing:border-box} body{margin:0;font-family:ui-sans-serif,Segoe UI,Arial;background:linear-gradient(120deg,var(--bg1),var(--bg2));color:var(--ink)}
.wrap{max-width:1100px;margin:24px auto;padding:20px}
.hero{background:var(--card);border-radius:18px;padding:22px;box-shadow:0 10px 30px rgba(2,8,23,.08)}
.hero h1{margin:0 0 6px;font-size:1.7rem}.hero p{margin:0;color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px;margin-top:18px}
.tile{background:var(--card);border-radius:14px;padding:14px 14px 10px;box-shadow:0 8px 24px rgba(2,8,23,.06)}
.tile h3{margin:0 0 8px;font-size:1.05rem}
.tile a{display:inline-block;margin:4px 0;padding:7px 10px;border-radius:10px;text-decoration:none;background:#eef6ff;color:var(--accent);font-weight:600}
.foot{margin-top:14px;color:var(--muted);font-size:.95rem}
</style></head>
<body><div class='wrap'>
<div class='hero'>
<h1>T22026 GA0 Unified API Hub</h1>
<p>All questions are live here with interactive UIs and APIs. Open a card, test quickly, then use route aliases for submissions.</p>
<div class='grid'>
<div class='tile'><h3>Q5 Code Interpreter</h3><a href='/q5/'>Open UI</a> <a href='/q5/health'>Health</a></div>
<div class='tile'><h3>Q10 Student API</h3><a href='/q10/'>Open UI</a> <a href='/q10/health'>Health</a></div>
<div class='tile'><h3>Q11 Sentiment</h3><a href='/q11/'>Open UI</a> <a href='/q11/health'>Health</a></div>
<div class='tile'><h3>Q14 Image Rebuild</h3><a href='/q14/'>Open UI</a> <a href='/q14/health'>Health</a></div>
<div class='tile'><h3>Q16 Move/Rename</h3><a href='/q16/'>Open UI</a> <a href='/q16/health'>Health</a></div>
<div class='tile'><h3>Q18 Proxy Helper</h3><a href='/q18/'>Open UI</a> <a href='/q18/health'>Health</a></div>
<div class='tile'><h3>Q19 Replace/Hash</h3><a href='/q19/'>Open UI</a> <a href='/q19/health'>Health</a></div>
</div>
<p class='foot'>If one question fails, check its health endpoint first. Upload-based routes (Q14/Q16/Q19) run in temporary storage and auto-clean.</p>
</div>
</div></body></html>
"""


app.mount("/q5", q5)
app.mount("/q10", q10)
app.mount("/q11", q11)
app.mount("/q14", q14)
app.mount("/q16", q16)
app.mount("/q18", q18)
app.mount("/q19", q19)
