"""Print final photo via macOS CUPS (lp command).

Configure printer name in .env (PRINTER_NAME). Find it with:
    lpstat -p
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile


def is_enabled() -> bool:
    return os.getenv("PRINT_ENABLED", "false").lower() == "true"


def list_printers() -> list[str]:
    if not shutil.which("lpstat"):
        return []
    try:
        out = subprocess.run(
            ["lpstat", "-p"], capture_output=True, text=True, timeout=5
        ).stdout
        return [line.split()[1] for line in out.splitlines() if line.startswith("printer ")]
    except Exception:
        return []


def print_photo(jpeg: bytes, copies: int = 1) -> tuple[bool, str]:
    """Send jpeg to printer. Returns (success, message)."""
    if not is_enabled():
        return False, "Print disabled (set PRINT_ENABLED=true in .env)"
    if not shutil.which("lp"):
        return False, "lp command not found (CUPS unavailable)"

    printer = os.getenv("PRINTER_NAME", "").strip()
    if not printer:
        return False, "PRINTER_NAME not set in .env. Run `lpstat -p` to find name."

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
        f.write(jpeg)
        tmp_path = f.name

    cmd = [
        "lp",
        "-d", printer,
        "-n", str(copies),
        "-o", "media=4x6",
        "-o", "fit-to-page",
        tmp_path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return True, result.stdout.strip() or "Printing..."
        return False, result.stderr.strip() or "Print failed"
    except subprocess.TimeoutExpired:
        return False, "Print timed out"
    finally:
        os.unlink(tmp_path)
