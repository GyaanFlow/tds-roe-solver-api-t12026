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
<title>T22026 API Hub</title><style>body{font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(120deg,#f3f9ff,#f7fff5);margin:0}.wrap{max-width:1000px;margin:24px auto;padding:20px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}a{display:block;margin:8px 0;color:#0f4c81;text-decoration:none;font-weight:600}</style></head>
<body><div class='wrap'><div class='card'><h2>T22026 GA0 Unified API Hub</h2><p>All question APIs are mounted below:</p>
<a href='/q5/'>Q5 UI</a>
<a href='/q10/'>Q10 UI</a>
<a href='/q11/'>Q11 UI</a>
<a href='/q14/'>Q14 UI</a>
<a href='/q16/'>Q16 UI</a>
<a href='/q18/'>Q18 UI</a>
<a href='/q19/'>Q19 UI</a>
<p>Health endpoints: <code>/q5/health</code>, <code>/q10/health</code>, etc.</p>
</div></div></body></html>
"""


app.mount("/q5", q5)
app.mount("/q10", q10)
app.mount("/q11", q11)
app.mount("/q14", q14)
app.mount("/q16", q16)
app.mount("/q18", q18)
app.mount("/q19", q19)
