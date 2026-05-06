"""Extract preview frames via ffmpeg (requires `ffmpeg` and `ffprobe` on PATH)."""
from __future__ import annotations

import random
import subprocess
from pathlib import Path


class VideoProbeError(RuntimeError):
    pass


class FFmpegError(RuntimeError):
    pass


def probe_duration_sec(video_path: Path) -> float:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(video_path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=120)
    except FileNotFoundError as e:
        raise VideoProbeError("ffprobe not found — install ffmpeg and ensure it is on PATH") from e
    if proc.returncode != 0:
        raise VideoProbeError(proc.stderr.strip() or "ffprobe failed")
    try:
        return float(proc.stdout.strip())
    except ValueError as e:
        raise VideoProbeError(f"invalid duration output: {proc.stdout!r}") from e


def extract_frame_at(
    video_path: Path,
    output_png: Path,
    time_sec: float,
    *,
    timeout_sec: int = 300,
) -> None:
    output_png.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-y",
        "-ss",
        str(max(0.0, time_sec)),
        "-i",
        str(video_path),
        "-vframes",
        "1",
        "-q:v",
        "2",
        str(output_png),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=timeout_sec)
    except FileNotFoundError as e:
        raise FFmpegError("ffmpeg not found — install ffmpeg and ensure it is on PATH") from e
    if proc.returncode != 0 or not output_png.is_file():
        raise FFmpegError(proc.stderr.strip() or proc.stdout.strip() or "ffmpeg failed")


def pick_random_timestamp(duration: float, *, margin_sec: float = 1.0, seed: int | None = None) -> float:
    if seed is not None:
        random.seed(seed)
    if duration <= 0:
        return 0.0
    low = margin_sec
    high = max(margin_sec, duration - margin_sec)
    if low >= high:
        return duration / 2.0
    return random.uniform(low, high)


def extract_preview_png(
    video_path: Path,
    output_png: Path,
    *,
    margin_sec: float = 1.0,
    seed: int | None = None,
) -> float:
    duration = probe_duration_sec(video_path)
    t = pick_random_timestamp(duration, margin_sec=margin_sec, seed=seed)
    extract_frame_at(video_path, output_png, t)
    return t
