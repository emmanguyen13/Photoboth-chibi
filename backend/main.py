"""Photobooth FastAPI server.

Run: uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
"""
from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from backend import camera, compositor, printer, storage

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
FRONTEND = ROOT / "frontend"
OUTPUT = ROOT / "output"

_camera: camera.Camera | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _camera
    mode = os.getenv("CAMERA_MODE", "webcam")
    try:
        _camera = camera.make_camera(mode)
        print(f"[startup] Camera ready: {mode}")
    except Exception as e:
        print(f"[startup] Camera init failed ({mode}): {e}")
        _camera = None
    yield
    if _camera:
        _camera.close()


app = FastAPI(title="Photobooth", lifespan=lifespan)


@app.get("/", response_class=HTMLResponse)
async def index() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


@app.get("/api/themes")
async def themes() -> dict:
    return {"themes": compositor.list_themes()}


@app.get("/api/status")
async def status() -> dict:
    return {
        "camera_mode": os.getenv("CAMERA_MODE", "webcam"),
        "camera_ready": _camera is not None,
        "print_enabled": printer.is_enabled(),
        "printer_name": os.getenv("PRINTER_NAME", ""),
        "available_printers": printer.list_printers(),
        "supabase_configured": bool(
            os.getenv("SUPABASE_URL") and "xxxxx" not in os.getenv("SUPABASE_URL", "xxxxx")
        ),
        "event_name": os.getenv("EVENT_NAME", ""),
        "hashtag": os.getenv("EVENT_HASHTAG", ""),
    }


@app.post("/api/capture")
async def capture(theme: str = Query("dinosaur"), print_copies: int = Query(0)) -> dict:
    if _camera is None:
        raise HTTPException(503, "Camera not ready. Check CAMERA_MODE in .env.")

    available = compositor.list_themes()
    if theme not in available:
        raise HTTPException(400, f"Unknown theme '{theme}'. Available: {available}")

    try:
        raw_jpeg = _camera.capture()
    except Exception as e:
        raise HTTPException(500, f"Capture failed: {e}")

    final_jpeg = compositor.composite(
        raw_jpeg,
        theme=theme,
        event_name=os.getenv("EVENT_NAME", ""),
        hashtag=os.getenv("EVENT_HASHTAG", ""),
    )

    photo_id, _ = storage.save_local(final_jpeg)
    public_url = storage.upload_and_get_url(final_jpeg, photo_id)

    print_result = None
    if print_copies > 0:
        ok, msg = printer.print_photo(final_jpeg, copies=print_copies)
        print_result = {"ok": ok, "message": msg}

    return {
        "photo_id": photo_id,
        "preview_url": f"/photo/{photo_id}",
        "public_url": public_url,
        "qr_url": f"/api/qr?photo_id={photo_id}",
        "print": print_result,
    }


@app.post("/api/print")
async def reprint(photo_id: str = Query(...), copies: int = Query(1)) -> dict:
    path = OUTPUT / f"{photo_id}.jpg"
    if not path.exists():
        raise HTTPException(404, "Photo not found")
    ok, msg = printer.print_photo(path.read_bytes(), copies=copies)
    return {"ok": ok, "message": msg}


@app.get("/api/qr")
async def qr(photo_id: str = Query(...)) -> Response:
    path = OUTPUT / f"{photo_id}.jpg"
    if not path.exists():
        raise HTTPException(404, "Photo not found")
    public_url = storage.upload_and_get_url(path.read_bytes(), photo_id)
    return Response(content=storage.make_qr(public_url), media_type="image/png")


@app.get("/photo/{photo_id}", response_class=HTMLResponse)
async def get_photo(photo_id: str) -> HTMLResponse:
    """Mobile-friendly page guests see when they scan the QR."""
    path = OUTPUT / f"{photo_id}.jpg"
    if not path.exists():
        raise HTTPException(404, "Photo not found")
    event = os.getenv("EVENT_NAME", "Photobooth")
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{event} — Ảnh của bạn</title>
<style>
  body {{
    margin: 0; padding: 24px;
    font-family: -apple-system, "Helvetica Neue", sans-serif;
    background: linear-gradient(135deg, #FFE0EC 0%, #C8E8FF 100%);
    min-height: 100vh; display: flex; flex-direction: column;
    align-items: center; gap: 20px;
  }}
  h1 {{ margin: 8px 0; color: #2D1B4E; font-size: 22px; text-align: center; }}
  img {{
    max-width: 100%; max-height: 75vh; border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.15);
  }}
  .btn {{
    display: inline-block; padding: 16px 28px; background: #FF4D8A;
    color: #fff; text-decoration: none; font-weight: bold; font-size: 18px;
    border-radius: 999px; box-shadow: 0 4px 16px rgba(255,77,138,0.3);
  }}
  .hint {{ color: #6B5B8B; font-size: 14px; text-align: center; line-height: 1.5; }}
</style>
</head>
<body>
  <h1>📸 Ảnh kỷ niệm của bạn</h1>
  <img src="/photo/{photo_id}.jpg" alt="Photo">
  <a href="/photo/{photo_id}.jpg" download class="btn">⬇️ Tải về máy</a>
  <p class="hint">Hoặc nhấn giữ vào ảnh → "Lưu vào ảnh"<br>Cám ơn bạn đã đến chung vui! 🎉</p>
</body>
</html>"""
    return HTMLResponse(html)


@app.get("/photo/{photo_id}.jpg")
async def get_photo_raw(photo_id: str) -> FileResponse:
    path = OUTPUT / f"{photo_id}.jpg"
    if not path.exists():
        raise HTTPException(404, "Photo not found")
    return FileResponse(path, media_type="image/jpeg")


app.mount("/static", StaticFiles(directory=FRONTEND), name="static")
