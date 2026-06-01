"""OCR for CCTV watermark frames — RapidOCR singleton, thread-safe."""
from __future__ import annotations

import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_ocr_lock = threading.Lock()
_ocr_engine: Any | None = None
_ocr_init_error: str | None = None


@dataclass
class OcrImageResult:
    text: str
    lines: list[str] = field(default_factory=list)
    engine: str = "none"
    available: bool = False
    error: str | None = None


def ocr_status() -> dict[str, Any]:
    """Diagnostics for /health and UI."""
    with _ocr_lock:
        if _ocr_engine is not None:
            return {"available": True, "engine": "rapidocr_onnxruntime", "error": None}
        if _ocr_init_error:
            return {"available": False, "engine": "none", "error": _ocr_init_error}
    try:
        get_ocr_engine()
        return {"available": True, "engine": "rapidocr_onnxruntime", "error": None}
    except Exception as e:
        return {"available": False, "engine": "none", "error": str(e)}


def get_ocr_engine() -> Any:
    global _ocr_engine, _ocr_init_error
    with _ocr_lock:
        if _ocr_engine is not None:
            return _ocr_engine
        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError as e:
            _ocr_init_error = f"rapidocr_onnxruntime not installed: {e}"
            raise RuntimeError(_ocr_init_error) from e
        try:
            _ocr_engine = RapidOCR()
            _ocr_init_error = None
            return _ocr_engine
        except Exception as e:
            _ocr_init_error = str(e)
            raise RuntimeError(f"RapidOCR init failed: {e}") from e


def warmup() -> OcrImageResult:
    """Load ONNX models at startup (optional)."""
    try:
        get_ocr_engine()
        return OcrImageResult(text="", lines=[], engine="rapidocr_onnxruntime", available=True)
    except RuntimeError as e:
        return OcrImageResult(text="", lines=[], engine="none", available=False, error=str(e))


def _lines_from_result(result: Any) -> list[str]:
    if not result:
        return []
    lines: list[str] = []
    for item in result:
        if not item:
            continue
        if isinstance(item, (list, tuple)):
            if len(item) >= 2 and item[1]:
                lines.append(str(item[1]).strip())
            elif len(item) >= 1 and isinstance(item[0], str):
                lines.append(item[0].strip())
        elif isinstance(item, str):
            lines.append(item.strip())
    return [ln for ln in lines if ln]


def _preprocess_for_ocr(image_path: Path) -> Path:
    """Upscale + autocontrast OSD regions; falls back to original if Pillow missing."""
    try:
        from PIL import Image, ImageEnhance, ImageOps
    except ImportError:
        return image_path
    try:
        with Image.open(image_path) as im:
            im = im.convert("RGB")
            w, h = im.size
            if max(w, h) < 1280:
                scale = min(2.0, 1280 / max(w, h))
                im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
            im = ImageOps.autocontrast(im, cutoff=1)
            im = ImageEnhance.Sharpness(im).enhance(1.15)
            out_path = image_path.with_name(f"{image_path.stem}_ocr{image_path.suffix}")
            im.save(out_path, format="PNG", optimize=True)
            return out_path
    except Exception:
        return image_path


def image_to_text(image_path: Path) -> OcrImageResult:
    path = image_path.resolve()
    if not path.is_file():
        return OcrImageResult(
            text="",
            lines=[],
            engine="none",
            available=False,
            error=f"image not found: {path}",
        )
    try:
        ocr = get_ocr_engine()
    except RuntimeError as e:
        return OcrImageResult(text="", lines=[], engine="none", available=False, error=str(e))

    ocr_input = _preprocess_for_ocr(path)
    try:
        out = ocr(str(ocr_input))
        if isinstance(out, tuple):
            result = out[0]
        else:
            result = out
        lines = _lines_from_result(result)
        text = "\n".join(lines)
        return OcrImageResult(
            text=text,
            lines=lines,
            engine="rapidocr_onnxruntime",
            available=True,
        )
    except Exception as e:
        return OcrImageResult(
            text="",
            lines=[],
            engine="rapidocr_onnxruntime",
            available=True,
            error=f"OCR run failed: {e}",
        )


def merge_frame_results(results: list[OcrImageResult]) -> OcrImageResult:
    """Combine lines from multiple frames (dedupe, preserve order)."""
    seen: set[str] = set()
    lines: list[str] = []
    errors: list[str] = []
    engine = "none"
    available = False
    for r in results:
        if r.available:
            available = True
            engine = r.engine
        if r.error:
            errors.append(r.error)
        for ln in r.lines:
            key = ln.strip().lower()
            if key and key not in seen:
                seen.add(key)
                lines.append(ln.strip())
    return OcrImageResult(
        text="\n".join(lines),
        lines=lines,
        engine=engine,
        available=available,
        error="; ".join(errors) if errors else None,
    )
