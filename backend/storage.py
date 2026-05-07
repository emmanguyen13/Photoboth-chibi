"""Save photo locally + generate QR pointing to LAN URL.

Auto-detects local IP. Optional Supabase upload if configured.
"""
from __future__ import annotations

import io
import os
import socket
import uuid
from datetime import datetime
from pathlib import Path

import qrcode

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _detect_lan_ip() -> str:
    """Find the LAN IP this machine uses to reach the network."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


def get_public_url() -> str:
    """Return base URL for QR. Prefer .env PUBLIC_URL, else autodetect LAN IP."""
    explicit = os.getenv("PUBLIC_URL", "").strip()
    if explicit and "localhost" not in explicit and explicit != "http://0.0.0.0:8000":
        return explicit.rstrip("/")
    port = os.getenv("PORT", "8000")
    return f"http://{_detect_lan_ip()}:{port}"


def get_qr_target(photo_id: str) -> str:
    """Pick the URL the QR code should encode.

    Priority:
      1. GALLERY_URL (Vercel) if set → e.g. https://photoboth-chibi.vercel.app/photo/<id>
      2. Supabase public URL (direct .jpg)
      3. Local IP fallback
    """
    gallery = os.getenv("GALLERY_URL", "").strip().rstrip("/")
    if gallery and "xxxxx" not in gallery:
        return f"{gallery}/photo/{photo_id}"
    return upload_and_get_url_by_id(photo_id)


def upload_and_get_url_by_id(photo_id: str) -> str:
    """Return the canonical photo URL (Supabase public or local fallback)."""
    path = OUTPUT_DIR / f"{photo_id}.jpg"
    if not path.exists():
        return f"{get_public_url()}/photo/{photo_id}"
    return upload_and_get_url(path.read_bytes(), photo_id)


def _supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key or "xxxxx" in url:
        return None
    try:
        from supabase import create_client

        return create_client(url, key)
    except Exception as e:
        print(f"[storage] Supabase init failed: {e}")
        return None


def save_local(jpeg: bytes) -> tuple[str, Path]:
    """Save to disk, return (photo_id, path)."""
    photo_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    path = OUTPUT_DIR / f"{photo_id}.jpg"
    path.write_bytes(jpeg)
    return photo_id, path


def upload_and_get_url(jpeg: bytes, photo_id: str) -> str:
    """Upload to Supabase Storage, return public URL.

    Falls back to local URL if Supabase not configured.
    """
    client = _supabase_client()
    public_url = get_public_url()
    filename = f"{photo_id}.jpg"

    if client is None:
        return f"{public_url}/photo/{photo_id}"

    bucket = os.getenv("SUPABASE_BUCKET", "photobooth")
    try:
        client.storage.from_(bucket).upload(
            path=filename,
            file=jpeg,
            file_options={"content-type": "image/jpeg", "upsert": "true"},
        )
        return client.storage.from_(bucket).get_public_url(filename)
    except Exception as e:
        print(f"[storage] Supabase upload failed, falling back local: {e}")
        return f"{public_url}/photo/{photo_id}"


def make_qr(url: str) -> bytes:
    """Generate QR code PNG pointing to url."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=12,
        border=2,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a1a", back_color="#ffffff")
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()
