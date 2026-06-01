"""Import helpers: duplicate keys, safe video rename."""
from __future__ import annotations

import re
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Segment

_INVALID_FS = re.compile(r'[<>:"/\\|?*\x00]')


def normalize_chain_label(label: str | None) -> str:
    return (label or "").strip().upper()


def chain_pair_key(start: str | None, end: str | None) -> tuple[str, str] | None:
    """Undirected pair: A–B equals B–A."""
    a = normalize_chain_label(start)
    b = normalize_chain_label(end)
    if not a or not b:
        return None
    return tuple(sorted((a, b)))


def safe_video_basename(start: str | None, end: str | None) -> str:
    a = (start or "?").strip()
    b = (end or "?").strip()
    name = f"{a}~{b}.mp4"
    name = _INVALID_FS.sub("_", name)
    return name[:180] if len(name) > 180 else name


def unique_path(directory: Path, filename: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename
    if not target.exists():
        return target
    stem = Path(filename).stem
    ext = Path(filename).suffix or ".mp4"
    n = 2
    while True:
        candidate = directory / f"{stem}（{n}）{ext}"
        if not candidate.exists():
            return candidate
        n += 1
        if n > 500:
            return directory / f"{stem}_{n}{ext}"


def try_rename_file(src: Path, dest: Path) -> Path:
    """Rename src → dest; return final path (dest if success, else src)."""
    if not src.is_file():
        return src
    dest.parent.mkdir(parents=True, exist_ok=True)
    final = unique_path(dest.parent, dest.name) if dest.exists() else dest
    try:
        src.rename(final)
        return final.resolve()
    except OSError:
        return src


async def find_duplicate_segment_ids(
    db: AsyncSession,
    project_id: int,
    start: str | None,
    end: str | None,
) -> list[int]:
    key = chain_pair_key(start, end)
    if not key:
        return []
    r = await db.execute(select(Segment).where(Segment.project_id == project_id))
    hits: list[int] = []
    for seg in r.scalars().all():
        sk = chain_pair_key(seg.chain_start_label, seg.chain_end_label)
        if sk == key:
            hits.append(seg.id)
    return hits
