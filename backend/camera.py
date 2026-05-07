"""Camera abstraction: gphoto2 DSLR or webcam fallback."""
from __future__ import annotations

import io
import os
import time
from abc import ABC, abstractmethod
from pathlib import Path


class Camera(ABC):
    @abstractmethod
    def capture(self) -> bytes:
        """Trigger shutter, return JPEG bytes."""

    @abstractmethod
    def close(self) -> None:
        ...


class DSLRCamera(Camera):
    """gphoto2-backed DSLR. Works with most Canon/Nikon/Fuji over USB."""

    def __init__(self) -> None:
        import gphoto2 as gp

        self._gp = gp
        self._camera = gp.Camera()
        self._camera.init()
        cfg = self._camera.get_summary()
        print(f"[camera] DSLR connected:\n{cfg}")

    def capture(self) -> bytes:
        gp = self._gp
        file_path = self._camera.capture(gp.GP_CAPTURE_IMAGE)
        camera_file = self._camera.file_get(
            file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL
        )
        data = memoryview(camera_file.get_data_and_size()).tobytes()
        try:
            self._camera.file_delete(file_path.folder, file_path.name)
        except Exception:
            pass
        return data

    def close(self) -> None:
        try:
            self._camera.exit()
        except Exception:
            pass


class WebcamCamera(Camera):
    """Fallback that captures via macOS `imagesnap` (built-in friendly) or OpenCV."""

    def __init__(self) -> None:
        try:
            import cv2  # type: ignore

            self._cv2 = cv2
            self._cap = cv2.VideoCapture(0)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            if not self._cap.isOpened():
                raise RuntimeError("Cannot open webcam")
            for _ in range(5):
                self._cap.read()
                time.sleep(0.05)
            self._mode = "cv2"
        except ImportError:
            self._mode = "imagesnap"
            print("[camera] opencv-python not installed, falling back to imagesnap")

    def capture(self) -> bytes:
        if self._mode == "cv2":
            ok, frame = self._cap.read()
            if not ok:
                raise RuntimeError("Webcam capture failed")
            ok, buf = self._cv2.imencode(".jpg", frame, [self._cv2.IMWRITE_JPEG_QUALITY, 92])
            if not ok:
                raise RuntimeError("JPEG encode failed")
            return bytes(buf)

        tmp = Path("/tmp") / f"booth_{int(time.time()*1000)}.jpg"
        os.system(f"imagesnap -q '{tmp}' >/dev/null 2>&1")
        if not tmp.exists():
            raise RuntimeError(
                "imagesnap not found. Install with: brew install imagesnap, "
                "or pip install opencv-python"
            )
        data = tmp.read_bytes()
        tmp.unlink(missing_ok=True)
        return data

    def close(self) -> None:
        if self._mode == "cv2":
            self._cap.release()


def make_camera(mode: str) -> Camera:
    mode = (mode or "webcam").lower()
    if mode == "dslr":
        return DSLRCamera()
    return WebcamCamera()
