"""Guess pipe segment labels (e.g. W11-W12) from OCR or raw text."""
from __future__ import annotations

import re

# 井号段：W11-W12、w1-w2、NH2W5-W11 等松散形式
_RANGE_PATTERNS = [
    re.compile(
        r"(?P<a>[A-Za-z]{0,4}\d+[A-Za-z0-9\-]*)\s*[-–—至~～]\s*(?P<b>[A-Za-z]{0,4}\d+[A-Za-z0-9\-]*)",
        re.UNICODE,
    ),
    re.compile(
        r"(?P<a>[A-Za-z]{0,4}\d+[A-Za-z0-9\-]*)\s*到\s*(?P<b>[A-Za-z]{0,4}\d+[A-Za-z0-9\-]*)",
        re.UNICODE,
    ),
]


def suggest_pipe_range(text: str) -> tuple[str | None, str | None]:
    if not text or not text.strip():
        return None, None
    for pat in _RANGE_PATTERNS:
        m = pat.search(text.replace("－", "-"))
        if m:
            a, b = m.group("a").strip(), m.group("b").strip()
            if a and b:
                return a, b
    return None, None
