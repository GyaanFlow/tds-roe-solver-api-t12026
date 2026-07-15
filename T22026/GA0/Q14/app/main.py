from __future__ import annotations

import io
import os
import tempfile
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
OUTPUT_DIR = Path(os.getenv("Q14_OUTPUT_DIR", "/tmp/q14_output"))
try:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    # Fallback for restricted/containerized filesystems (e.g. read-only HF Space FS).
    OUTPUT_DIR = Path(tempfile.gettempdir()) / "q14_output"
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

Q14_UI = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Q14 Jigsaw Rebuild & Grayscale Forensic Tool</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: rgba(22, 28, 45, 0.6);
      --border: rgba(245, 158, 11, 0.2);
      --border-hover: rgba(245, 158, 11, 0.4);
      --text: #f8fafc;
      --muted: #94a3b8;
      --accent: #f59e0b;
      --accent-rgb: 245, 158, 11;
      --success: #10b981;
      --success-bg: rgba(16, 185, 129, 0.1);
      --glass-blur: blur(16px);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Outfit', sans-serif;
      background-color: var(--bg);
      background-image: 
        radial-gradient(at 0% 0%, rgba(245, 158, 11, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(99, 102, 241, 0.1) 0px, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }
    .container {
      width: 100%;
      max-width: 900px;
      backdrop-filter: var(--glass-blur);
      -webkit-backdrop-filter: var(--glass-blur);
    }
    .header {
      text-align: center;
      margin-bottom: 30px;
    }
    .header h1 {
      font-size: 2.2rem;
      font-weight: 700;
      background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
    }
    .badge {
      display: inline-block;
      padding: 6px 12px;
      background: rgba(245, 158, 11, 0.1);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 20px;
      color: var(--accent);
      font-size: 0.85rem;
      font-weight: 500;
      margin-bottom: 15px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 30px;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
      margin-bottom: 25px;
      transition: border-color 0.3s ease;
    }
    .card:hover {
      border-color: var(--border-hover);
    }
    .intro-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 25px;
    }
    @media (max-width: 768px) {
      .intro-grid { grid-template-columns: 1fr; }
    }
    .intro-card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 18px;
    }
    .intro-card h3 {
      font-size: 1.1rem;
      color: var(--accent);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .intro-card p, .intro-card li {
      font-size: 0.9rem;
      color: var(--muted);
      line-height: 1.5;
    }
    .intro-card ol {
      margin-left: 20px;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 12px 24px;
      font-family: inherit;
      font-size: 0.95rem;
      font-weight: 600;
      color: #0b0f19;
      background: var(--accent);
      border: none;
      border-radius: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      text-decoration: none;
      box-shadow: 0 4px 12px rgba(245, 158, 11, 0.2);
    }
    .btn:hover {
      background: #fbbf24;
      transform: translateY(-1px);
      box-shadow: 0 6px 16px rgba(245, 158, 11, 0.3);
    }
    .btn-secondary {
      background: rgba(255, 255, 255, 0.08);
      color: var(--text);
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: none;
      margin-right: 10px;
    }
    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.15);
      box-shadow: none;
    }
    .dropzone {
      border: 2px dashed rgba(245, 158, 11, 0.3);
      border-radius: 16px;
      padding: 40px 20px;
      text-align: center;
      cursor: pointer;
      background: rgba(245, 158, 11, 0.02);
      transition: all 0.3s ease;
      margin-bottom: 25px;
      position: relative;
    }
    .dropzone:hover, .dropzone.dragover {
      border-color: var(--accent);
      background: rgba(245, 158, 11, 0.05);
    }
    .dropzone svg {
      width: 48px;
      height: 48px;
      fill: var(--accent);
      margin-bottom: 15px;
      opacity: 0.8;
      transition: transform 0.3s ease;
    }
    .dropzone:hover svg {
      transform: translateY(-5px);
    }
    .dropzone p {
      font-size: 1rem;
      color: var(--text);
      margin-bottom: 6px;
    }
    .dropzone span {
      font-size: 0.85rem;
      color: var(--muted);
    }
    .dropzone input {
      position: absolute;
      top: 0; left: 0; width: 100%; height: 100%;
      opacity: 0;
      cursor: pointer;
    }
    .alert-banner {
      background: var(--success-bg);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: 12px;
      padding: 15px 20px;
      display: flex;
      align-items: center;
      gap: 12px;
      margin-top: 25px;
      color: #a7f3d0;
    }
    .alert-banner strong {
      color: var(--success);
    }
    .preview-container {
      display: none;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-top: 25px;
    }
    @media (max-width: 768px) {
      .preview-container { grid-template-columns: 1fr; }
    }
    .preview-box {
      background: rgba(0, 0, 0, 0.2);
      border: 1px solid rgba(255, 255, 255, 0.05);
      border-radius: 12px;
      padding: 15px;
      text-align: center;
    }
    .preview-box h4 {
      font-size: 0.95rem;
      color: var(--muted);
      margin-bottom: 12px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .preview-box img {
      max-width: 100%;
      height: auto;
      border-radius: 8px;
      border: 1px solid rgba(255, 255, 255, 0.1);
      box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    .results-card {
      display: none;
    }
    .console-pre {
      background: rgba(0, 0, 0, 0.4);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 15px;
      color: #38bdf8;
      font-family: 'Courier New', Courier, monospace;
      font-size: 0.85rem;
      overflow-x: auto;
      max-height: 200px;
      text-align: left;
    }
    .download-section {
      text-align: center;
      margin-top: 20px;
    }
    .submit-box {
      background: rgba(16, 185, 129, 0.05);
      border: 1px dashed var(--success);
      border-radius: 12px;
      padding: 15px;
      margin-top: 20px;
      text-align: center;
    }
    .submit-box span {
      display: block;
      font-size: 0.9rem;
      color: var(--muted);
      margin-bottom: 8px;
    }
    .submit-box code {
      background: rgba(0,0,0,0.3);
      padding: 4px 8px;
      border-radius: 4px;
      color: var(--success);
      font-size: 0.95rem;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <span class="badge">Active & Certified</span>
      <h1>Forensic Image Reconstruction Service</h1>
      <p style="color: var(--muted);">T22026 GA0 Q14 Jigsaw Reassemble & Grayscale Converter</p>
    </div>

    <div class="card">
      <div class="intro-grid">
        <div class="intro-card">
          <h3>
            <svg style="width:18px;height:18px;" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm0 18c-4.4 0-8-3.6-8-8s3.6-8 8-8 8 3.6 8 8-3.6 8-8 8zm-1-13h2v6h-2zm0 8h2v2h-2z"/></svg>
            Background & Requirement
          </h3>
          <p>
            PixelGuard tampered puzzle files must be reconstructed using a fixed 5x5 spatial tile swap mapping. The legal team requires a losslessly exported grayscale output file derived strictly using luminance coefficients:
            <br><br>
            <code>Y = 0.2126R + 0.7152G + 0.0722B</code> (with round-to-nearest).
          </p>
        </div>
        <div class="intro-card">
          <h3>
            <svg style="width:18px;height:18px;" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2zm1 14h-2v-2h2v2zm0-4h-2V7h2v5z"/></svg>
            Submission Instructions
          </h3>
          <ol>
            <li>Go to your active <strong>IITM TDS exam page</strong> and find the <strong>"Reconstruct and desaturate an image"</strong> (Q14) question section.</li>
            <li>Click the <strong>"Download jigsaw.webp"</strong> button there to get your unique, dynamically seeded scrambled puzzle.</li>
            <li>Drag & drop that downloaded <strong>jigsaw.webp</strong> to the upload box below.</li>
            <li>Our secure sandbox will instantly swap the scrambled tiles and losslessly convert the image to perfect grayscale.</li>
            <li>Download the resulting reconstructed PNG and upload it back to the exam page field with ID <strong>q-image-grayscale-rebuild</strong>.</li>
          </ol>
        </div>
      </div>

      <div class="alert-banner" style="margin: 0 0 25px 0; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.25); color: #fcd34d;">
        <span>⚠️ <strong>Important:</strong> Do not use a static jigsaw.webp. The puzzle is dynamically generated based on your exam session email seed, so you must download it directly from your exam screen.</span>
      </div>

      <div class="dropzone" id="dropzone">
        <svg viewBox="0 0 24 24">
          <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
        </svg>
        <p>Drag & Drop jigsaw.webp here</p>
        <span>or click to browse from local disk</span>
        <input type="file" id="f" accept=".webp,image/webp">
      </div>

      <div class="alert-banner">
        <span>💡 <strong>Tip:</strong> The output will be a flawless, lossless PNG image ready for direct grading submission.</span>
      </div>
    </div>

    <div class="card results-card" id="resultsCard">
      <h3 style="color: var(--accent); margin-bottom: 20px; font-size: 1.25rem;">Reconstruction Sandbox Output</h3>
      
      <div class="preview-container" id="previewContainer">
        <div class="preview-box">
          <h4>Original Scrambled</h4>
          <img id="origImg" src="jigsaw.webp" alt="Original Scrambled">
        </div>
        <div class="preview-box">
          <h4>Reconstructed Grayscale</h4>
          <img id="reconImg" src="" alt="Reconstructed Grayscale">
        </div>
      </div>

      <div class="submit-box">
        <span>🚀 <strong>ACTION REQUIRED:</strong> Submit the generated PNG file below to the exam field:</span>
        <code>q-image-grayscale-rebuild</code>
      </div>

      <div class="download-section">
        <a id="dlBtn" href="" download="reconstructed_grayscale.png" class="btn">
          <svg style="width:18px;height:18px;" viewBox="0 0 24 24"><path fill="currentColor" d="M19 12v7H5v-7H3v7c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-7h-2zm-6 .67l2.59-2.58L17 11.5l-5 5-5-5 1.41-1.41L11 12.67V3h2v9.67z"/></svg>
          Download Lossless PNG
        </a>
      </div>

      <div style="margin-top: 25px;">
        <h4 style="font-size: 0.9rem; color: var(--muted); margin-bottom: 8px;">Metadata Logs</h4>
        <pre class="console-pre" id="out">Processing logs...</pre>
      </div>
    </div>
  </div>

  <script>
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('f');
    const resultsCard = document.getElementById('resultsCard');
    const previewContainer = document.getElementById('previewContainer');
    const reconImg = document.getElementById('reconImg');
    const dlBtn = document.getElementById('dlBtn');
    const out = document.getElementById('out');

    // Drag and drop visual events
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
      }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
      }, false);
    });

    dropzone.addEventListener('drop', (e) => {
      const dt = e.dataTransfer;
      const files = dt.files;
      if (files.length > 0) {
        fileInput.files = files;
        handleUpload(files[0]);
      }
    });

    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        handleUpload(e.target.files[0]);
      }
    });

    async function handleUpload(file) {
      if (!file) return;
      
      // Update original scrambled image preview dynamically
      const reader = new FileReader();
      reader.onload = function(e) {
        document.getElementById('origImg').src = e.target.result;
      };
      reader.readAsDataURL(file);
      
      resultsCard.style.display = 'block';
      out.textContent = 'Uploading scrambled puzzle for reassembly...';
      
      const fd = new FormData();
      fd.append('image', file);
      
      const path = window.location.pathname.endsWith('/') ? window.location.pathname : window.location.pathname + '/';
      try {
        const response = await fetch(window.location.origin + path + 'rebuild-grayscale', {
          method: 'POST',
          body: fd
        });
        
        const data = await response.json();
        
        if (!response.ok) {
          out.textContent = 'Error: ' + (data.detail || JSON.stringify(data));
          return;
        }
        
        out.textContent = [
          '🌟 Reconstruction complete!',
          'Request ID: ' + data.request_id,
          'Lossless PNG URL: ' + data.png_url,
          'Resolution: ' + data.input.size.width + 'x' + data.input.size.height + ' px',
          'Tile layout: ' + data.processing.grid + 'x' + data.processing.grid + ' grid',
          'Grayscale transformation: ' + data.processing.grayscale,
          '',
          'Full Response payload:',
          JSON.stringify(data, null, 2)
        ].join('\\n');
        
        previewContainer.style.display = 'grid';
        
        // Show reconstructed image
        // Resolve absolute URL from the relative file path (works whether mounted or standalone)
        const absBase = window.location.origin + window.location.pathname.replace(/\\/$/, '') + '/';
        const imgAbsUrl = absBase + data.png_url;
        reconImg.src = imgAbsUrl;
        dlBtn.href = imgAbsUrl;
        
      } catch (err) {
        out.textContent = 'Network or server error: ' + err.message;
      }
    }
  </script>
</body>
</html>"""


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


@app.get("/jigsaw.webp")
def get_jigsaw():
    p = Path(__file__).parent / "jigsaw.webp"
    if not p.exists():
        raise HTTPException(status_code=404, detail="jigsaw.webp not found")
    return FileResponse(str(p), media_type="image/webp")


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


_last_cleanup = 0.0
_CLEANUP_INTERVAL = 300.0
_MAX_OUTPUT_FILES = 50


def _cleanup_output_dir():
    global _last_cleanup
    now = time.time()
    if now - _last_cleanup < _CLEANUP_INTERVAL:
        return
    _last_cleanup = now
    try:
        files = sorted(OUTPUT_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        for f in files[_MAX_OUTPUT_FILES:]:
            f.unlink(missing_ok=True)
    except Exception:
        pass


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

    _cleanup_output_dir()

    return {
        "request_id": rid,
        "input": {"filename": image.filename, "bytes": len(data), "size": {"width": size[0], "height": size[1]}},
        "processing": {"grid": GRID, "tile_width": tile[0], "tile_height": tile[1], "grayscale": "luminance(0.2126,0.7152,0.0722)"},
        "png_url": f"files/{png_name}",
        "webp_url": f"files/{webp_name}" if webp_name else None,
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
