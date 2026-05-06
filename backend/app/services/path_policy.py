"""Resolve user-supplied paths under allowed roots only."""
from pathlib import Path

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


def resolve_absolute_allowed(path_str: str, roots: list[Path]) -> Path:
    p = Path(path_str).expanduser().resolve()
    if not p.is_file():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="video file not found")
    if not is_under_any_root(p, roots):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="video path must be under configured media roots",
        )
    return p
