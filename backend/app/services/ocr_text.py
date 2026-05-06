"""OCR preview images — RapidOCR (onnx) when available, else empty string."""
from __future__ import annotations

from pathlib import Path


def image_to_text(image_path: Path) -> str:
    path_str = str(image_path.resolve())
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        return ""

    ocr = RapidOCR()
    result, _ = ocr(path_str)
    if not result:
        return ""
    lines: list[str] = []
    for item in result:
        if len(item) >= 2 and item[1]:
            lines.append(str(item[1]))
    return "\n".join(lines)
