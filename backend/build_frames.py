"""Convert SVG frames to PNG (1200x1800) for compositor.

Run once after editing SVGs:
    python -m backend.build_frames
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "frames"
W, H = 1200, 1800


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def convert_svg(src: Path, dst: Path) -> None:
    if have("rsvg-convert"):
        subprocess.run(
            ["rsvg-convert", "-w", str(W), "-h", str(H), "-o", str(dst), str(src)],
            check=True,
        )
        return
    if have("inkscape"):
        subprocess.run(
            ["inkscape", str(src), "-w", str(W), "-h", str(H), "-o", str(dst)],
            check=True,
        )
        return
    try:
        import cairosvg  # type: ignore

        cairosvg.svg2png(url=str(src), write_to=str(dst), output_width=W, output_height=H)
        return
    except ImportError:
        pass
    raise RuntimeError(
        "No SVG converter found. Install one of:\n"
        "  brew install librsvg     (recommended, fastest)\n"
        "  brew install inkscape\n"
        "  pip install cairosvg"
    )


def main() -> None:
    for theme_dir in sorted(ASSETS.iterdir()):
        if not theme_dir.is_dir():
            continue
        svg = theme_dir / "frame.svg"
        png = theme_dir / "frame.png"
        if not svg.exists():
            print(f"[skip] {theme_dir.name}: no frame.svg")
            continue
        print(f"[build] {theme_dir.name}")
        convert_svg(svg, png)
    print("Done.")


if __name__ == "__main__":
    main()
