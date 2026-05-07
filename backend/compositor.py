"""Composite captured photo onto a themed frame."""
from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ASSETS = Path(__file__).resolve().parent.parent / "assets"
FRAMES_DIR = ASSETS / "frames"

CANVAS_W, CANVAS_H = 1200, 1800  # 4x6 inch @ 300dpi (10x15cm photo print)


def list_themes() -> list[str]:
    return sorted([p.name for p in FRAMES_DIR.iterdir() if p.is_dir()])


def _load_frame(theme: str) -> Image.Image:
    frame_path = FRAMES_DIR / theme / "frame.png"
    if not frame_path.exists():
        raise FileNotFoundError(f"Missing frame: {frame_path}")
    return Image.open(frame_path).convert("RGBA").resize((CANVAS_W, CANVAS_H))


def _load_event_text(event_name: str, hashtag: str) -> tuple[str, str]:
    return event_name or "", hashtag or ""


def composite(
    photo_jpeg: bytes,
    theme: str,
    event_name: str = "",
    hashtag: str = "",
) -> bytes:
    """Place captured photo onto themed frame, return final JPEG bytes."""
    photo = Image.open(io.BytesIO(photo_jpeg)).convert("RGB")
    frame = _load_frame(theme)

    # Photo window: centered, leaves room top/bottom for theme art + text
    win_w, win_h = 1000, 1300
    win_x, win_y = (CANVAS_W - win_w) // 2, 220

    # Cover-fit the photo into the window
    src_ratio = photo.width / photo.height
    dst_ratio = win_w / win_h
    if src_ratio > dst_ratio:
        new_h = win_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = win_w
        new_h = int(new_w / src_ratio)
    photo = photo.resize((new_w, new_h), Image.LANCZOS)
    crop_x = (new_w - win_w) // 2
    crop_y = (new_h - win_h) // 2
    photo = photo.crop((crop_x, crop_y, crop_x + win_w, crop_y + win_h))

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (255, 255, 255, 255))
    canvas.paste(photo, (win_x, win_y))
    canvas.alpha_composite(frame)

    if event_name or hashtag:
        draw = ImageDraw.Draw(canvas)
        font_path = _find_font()
        title_font = _font(font_path, 64)
        tag_font = _font(font_path, 42)
        if event_name:
            _draw_centered(draw, event_name, CANVAS_W // 2, 120, title_font, fill=(60, 40, 90))
        if hashtag:
            _draw_centered(
                draw, hashtag, CANVAS_W // 2, CANVAS_H - 90, tag_font, fill=(120, 80, 140)
            )

    out = io.BytesIO()
    canvas.convert("RGB").save(out, format="JPEG", quality=92, optimize=True)
    return out.getvalue()


def _find_font() -> str | None:
    candidates = [
        "/System/Library/Fonts/Supplemental/Comic Sans MS.ttf",
        "/System/Library/Fonts/Supplemental/Chalkboard.ttc",
        "/System/Library/Fonts/Avenir Next.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
    ]
    for c in candidates:
        if Path(c).exists():
            return c
    return None


def _font(path: str | None, size: int) -> ImageFont.ImageFont:
    if path:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _draw_centered(draw, text, cx, cy, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - w // 2, cy - h // 2), text, font=font, fill=fill)
