"""Synchronous video watermark scan (ffmpeg + OCR) — run via asyncio.to_thread."""
from __future__ import annotations

import hashlib
import random
import uuid
from pathlib import Path

from app.config import settings
from app.services import ocr_text, video_frames
from app.services.watermark_parse import ocr_lines_to_blocks, parse_from_text_blocks, ParseResult

_SAMPLE_COUNT = 4


def _sample_times(duration: float, seed_key: str) -> list[float]:
    """Random timestamps within video (reproducible per file via seed_key)."""
    if duration <= 0.3:
        return [0.0]
    digest = hashlib.sha256(seed_key.encode("utf-8")).hexdigest()
    rng = random.Random(int(digest[:16], 16))
    hi = max(0.1, duration - 0.35)
    if hi < 0.5:
        return [rng.uniform(0.0, hi)]
    candidates = sorted({rng.uniform(0.0, hi) for _ in range(_SAMPLE_COUNT * 3)})
    times = candidates[:_SAMPLE_COUNT]
    if not times:
        times = [hi / 2.0]
    return times


def scan_video_file(video_path: Path, project_id: int) -> tuple[ParseResult, str | None, dict]:
    """Returns (parse_result, preview_relpath, scan_meta)."""
    stem = video_path.stem
    meta: dict = {
        "ffmpeg_ok": False,
        "ocr_available": False,
        "ocr_engine": "none",
        "ocr_error": None,
        "ffmpeg_error": None,
        "ocr_raw_text": "",
        "ocr_blocks": [],
        "sample_times_sec": [],
    }
    blocks: list[str] = []
    preview_rel: str | None = None
    frame_rels: list[str] = []
    ocr_results: list[ocr_text.OcrImageResult] = []

    try:
        duration = video_frames.probe_duration_sec(video_path)
        meta["duration_sec"] = duration
        times = _sample_times(duration, str(video_path.resolve()))
        meta["sample_times_sec"] = times
        meta["sample_strategy"] = "random"


        for i, t in enumerate(times):
            frame_rel = f"imports/{project_id}/{uuid.uuid4().hex}.png"
            frame_path = settings.files_dir / frame_rel
            try:
                video_frames.extract_frame_at(video_path, frame_path, t)
                meta["ffmpeg_ok"] = True
                rel = frame_rel.replace("\\", "/")
                frame_rels.append(rel)
                if preview_rel is None:
                    preview_rel = rel
                ocr_res = ocr_text.image_to_text(frame_path)
                ocr_results.append(ocr_res)
            except (video_frames.VideoProbeError, video_frames.FFmpegError, OSError) as e:
                if meta["ffmpeg_error"] is None:
                    meta["ffmpeg_error"] = str(e)
                continue

        merged = ocr_text.merge_frame_results(ocr_results)
        meta["ocr_available"] = merged.available
        meta["ocr_engine"] = merged.engine
        meta["ocr_error"] = merged.error
        meta["ocr_raw_text"] = merged.text
        blocks = ocr_lines_to_blocks(merged.text)
        meta["ocr_blocks"] = blocks
        meta["sample_frame_relpaths"] = frame_rels

    except video_frames.VideoProbeError as e:
        meta["ffmpeg_error"] = str(e)
    except Exception as e:
        meta["scan_error"] = str(e)

    pr = parse_from_text_blocks(blocks, stem)
    if meta["ffmpeg_error"] and not blocks:
        pr.chain_warnings.append("FFMPEG_FAILED")
    if not meta["ocr_available"]:
        pr.chain_warnings.append("OCR_UNAVAILABLE")
    elif meta["ocr_error"] and not blocks:
        pr.chain_warnings.append("OCR_FAILED")

    return pr, preview_rel, meta
