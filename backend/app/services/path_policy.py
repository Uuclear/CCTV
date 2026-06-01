"""Resolve user-supplied paths under allowed roots only."""
from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import HTTPException, status


def resolve_under_dir(base: Path, relative_posix: str) -> Path:
    if not relative_posix or relative_posix.strip() == "":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="empty relative path")
    rel = relative_posix.replace("\\", "/").lstrip("/")
    if ".." in rel.split("/"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="invalid path")
    out = (base / rel).resolve()
    base_r = base.resolve()
    if not out.is_relative_to(base_r):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="path escapes base directory")
    return out


def is_under_any_root(path: Path, roots: list[Path]) -> bool:
    pr = path.resolve()
    for root in roots:
        rr = root.resolve()
        try:
            pr.relative_to(rr)
            return True
        except ValueError:
            continue
    return False


def _candidate_paths(path_str: str, roots: list[Path]) -> list[Path]:
    raw = Path(path_str).expanduser()
    if raw.is_absolute():
        return [raw.resolve()]
    return [(root / raw).resolve() for root in roots]


def resolve_path_under_roots(
    path_str: str,
    roots: list[Path],
    *,
    kind: Literal["file", "dir", "any"] = "any",
) -> Path:
    """Resolve absolute or root-relative path; must exist under one of roots."""
    tried: list[str] = []
    for p in _candidate_paths(path_str, roots):
        tried.append(str(p))
        if not p.exists():
            continue
        if not is_under_any_root(p, roots):
            continue
        if kind == "file" and not p.is_file():
            continue
        if kind == "dir" and not p.is_dir():
            continue
        return p

    if kind == "dir":
        detail = f"directory not found or not allowed: {path_str}"
    elif kind == "file":
        detail = f"file not found or not allowed: {path_str}"
    else:
        detail = f"path not found or not allowed: {path_str}"
    raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=detail)


def resolve_absolute_allowed(path_str: str, roots: list[Path]) -> Path:
    """Backward-compatible alias for video / file paths."""
    return resolve_path_under_roots(path_str, roots, kind="file")
