from pathlib import Path

import pytest
from fastapi import HTTPException

from app.services.path_policy import resolve_under_dir


def test_resolve_under_rejects_traversal(tmp_path: Path) -> None:
    base = tmp_path / "root"
    base.mkdir()
    with pytest.raises(HTTPException) as ei:
        resolve_under_dir(base, "a/../../../secret")
    assert ei.value.status_code == 400


def test_resolve_under_ok(tmp_path: Path) -> None:
    base = tmp_path / "root"
    base.mkdir()
    out = resolve_under_dir(base, "sub/file.mp4")
    assert out.resolve().is_relative_to(base.resolve())
