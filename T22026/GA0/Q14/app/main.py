from __future__ import annotations

import io
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Tuple

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from PIL import Image

APP_NAME = "T22026 GA0 Q14 Image Rebuild API"
APP_VERSION = "1.0.0"
GRID = 5
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", "12"))
OUTPUT_DIR = Path(os.getenv("Q14_OUTPUT_DIR", "output"))
try:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    # Fallback for restricted/containerized filesystems.
    OUTPUT_DIR = Path("/tmp/q14_output")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TILE_MAP: Dict[Tuple[int, int], Tuple[int, int]] = {
    (0, 0): (2, 1), (0, 1): (1, 1), (0, 2): (4, 1), (0, 3): (0, 3), (0, 4): (0, 1),
    (1, 0): (1, 4), (1, 1): (2, 0), (1, 2): (2, 4), (1, 3): (4, 2), (1, 4): (2, 2),
    (2, 0): (0, 0), (2, 1): (3, 2), (2, 2): (4, 3), (2, 3): (3, 0), (2, 4): (3, 4),
    (3, 0): (1, 0), (3, 1): (2, 3), (3, 2): (3, 3), (3, 3): (4, 4), (3, 4): (0, 2),
    (4, 0): (3, 1), (4, 1): (1, 2), (4, 2): (1, 3), (4, 3): (0, 4), (4, 4): (4, 0),
}

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ALLOW_ORIGINS", "*").split(","),
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)

Q14_UI = """
<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Q14 Rebuild API</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;background:linear-gradient(120deg,#fff9ec,#eaf7ff);margin:0}
.wrap{max-width:980px;margin:24px auto;padding:20px}.card{background:#fff;border-radius:14px;padding:18px;box-shadow:0 8px 24px rgba(0,0,0,.08)}
button{background:#b45309;color:#fff;border:0;padding:10px 14px;border-radius:10px;cursor:pointer}
pre{background:#0b1020;color:#d1e7ff;padding:12px;border-radius:10px;overflow:auto}
</style></head><body><div class='wrap'><div class='card'>
<h2>T22026 GA0 Q14: Jigsaw Rebuild + Luminance Grayscale API</h2>
<p>Routes: <code>/rebuild-grayscale</code>, <code>/ga0/q14/rebuild-grayscale</code>, <code>/t22026/ga0/q14/rebuild-grayscale</code></p>
<p>Upload scrambled <code>jigsaw.webp</code>. Output is lossless PNG and optional WEBP.</p>
<input type='file' id='f' accept='.webp,image/webp'><br><br>
<button onclick='run()'>Upload and Process</button>
<pre id='out'>Waiting...</pre>
</div></div>
<script>
async function run(){
 const file=document.getElementById('f').files[0];
 if(!file){document.getElementById('out').textContent='Select a WEBP file first.';return;}
 const fd=new FormData(); fd.append('image',file);
 const r=await fetch('ga0/q14/rebuild-grayscale',{method:'POST',body:fd});
 const j=await r.json();
 if(!r.ok){document.getElementById('out').textContent=JSON.stringify(j,null,2);return;}
 const lines=[
  'Request ID: '+j.request_id,
  'PNG: '+location.origin+j.png_url,
  'WEBP: '+(j.webp_url?location.origin+j.webp_url:'not generated'),
  '',
  'Response JSON:', JSON.stringify(j,null,2)
 ];
 document.getElementById('out').textContent=lines.join('\n');
}
</script></body></html>
"""


def process_image(src_bytes: bytes) -> tuple[bytes, bytes | None, tuple[int, int], tuple[int, int]]:
    with Image.open(io.BytesIO(src_bytes)) as img:
        src = img.convert("RGBA")

    width, height = src.size
    if width % GRID != 0 or height % GRID != 0:
        raise HTTPException(status_code=400, detail="Image width/height must be divisible by 5.")

    tile_w = width // GRID
    tile_h = height // GRID
    recon = Image.new("RGBA", (width, height))

    for (scr_r, scr_c), (orig_r, orig_c) in TILE_MAP.items():
        left = scr_c * tile_w
        top = scr_r * tile_h
        tile = src.crop((left, top, left + tile_w, top + tile_h))
        recon.paste(tile, (orig_c * tile_w, orig_r * tile_h))

    pixels = recon.load()
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            gray = int(0.2126 * r + 0.7152 * g + 0.0722 * b + 0.5)
            if gray < 0:
                gray = 0
            elif gray > 255:
                gray = 255
            pixels[x, y] = (gray, gray, gray, a)

    png_buf = io.BytesIO()
    recon.save(png_buf, format="PNG")

    webp_bytes = None
    webp_buf = io.BytesIO()
    try:
        recon.save(webp_buf, format="WEBP", lossless=True)
        webp_bytes = webp_buf.getvalue()
    except Exception:
        webp_bytes = None

    return png_buf.getvalue(), webp_bytes, (width, height), (tile_w, tile_h)


@app.get("/", response_class=HTMLResponse)
def home() -> str:
    return Q14_UI


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION, "output_dir": str(OUTPUT_DIR)}


@app.get("/files/{name}")
def get_file(name: str):
    # Prevent path traversal outside output dir.
    if "/" in name or "\\" in name or ".." in name:
        raise HTTPException(status_code=400, detail="Invalid file name")
    path = OUTPUT_DIR / name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="File not found")
    media = "image/png" if name.lower().endswith(".png") else "image/webp"
    return FileResponse(path=str(path), media_type=media, filename=name)


def _rebuild_grayscale(image: UploadFile) -> dict:
    if not image.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")

    ext = Path(image.filename).suffix.lower()
    if ext != ".webp":
        raise HTTPException(status_code=400, detail="Only .webp input is supported for Q14.")

    data = image.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(data) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File too large. Max {MAX_UPLOAD_MB} MB.")

    png, webp, size, tile = process_image(data)

    rid = f"q14-{int(time.time())}-{uuid.uuid4().hex[:8]}"
    png_name = f"{rid}.png"
    png_path = OUTPUT_DIR / png_name
    png_path.write_bytes(png)

    webp_name = None
    if webp is not None:
        webp_name = f"{rid}.webp"
        (OUTPUT_DIR / webp_name).write_bytes(webp)

    return {
        "request_id": rid,
        "input": {"filename": image.filename, "bytes": len(data), "size": {"width": size[0], "height": size[1]}},
        "processing": {"grid": GRID, "tile_width": tile[0], "tile_height": tile[1], "grayscale": "luminance(0.2126,0.7152,0.0722)"},
        "png_url": f"/files/{png_name}",
        "webp_url": f"/files/{webp_name}" if webp_name else None,
    }


@app.post("/rebuild-grayscale")
def rebuild_grayscale(image: UploadFile = File(...)) -> dict:
    return _rebuild_grayscale(image)


@app.post("/ga0/q14/rebuild-grayscale")
def rebuild_grayscale_ga0_q14(image: UploadFile = File(...)) -> dict:
    return _rebuild_grayscale(image)


@app.post("/t22026/ga0/q14/rebuild-grayscale")
def rebuild_grayscale_t22026_ga0_q14(image: UploadFile = File(...)) -> dict:
    return _rebuild_grayscale(image)



