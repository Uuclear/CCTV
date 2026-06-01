"""Condition grade labels — 一级 / 二级 / 三级 only (DB31 表16、表21)."""
from __future__ import annotations

VALID_GRADES = ("一级", "二级", "三级")


def normalize_condition_grade(grade: str | None, index: float | None = None) -> str:
    """Map DB/UI garbage ('0', numeric) to 一级|二级|三级."""
    if grade:
        g = str(grade).strip()
        if g in VALID_GRADES:
            return g
        if g in ("0", "0级", "0.0", ""):
            return "一级"
        if g in ("1", "1级"):
            return "一级"
        if g in ("2", "2级"):
            return "二级"
        if g in ("3", "3级"):
            return "三级"
        if g in VALID_GRADES:
            return g
    if index is None:
        return "一级"
    if index < 4:
        return "一级"
    if index < 7:
        return "二级"
    return "三级"
