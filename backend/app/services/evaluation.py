"""Placeholder evaluation engine driven by rules.yaml (not official standard)."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class GradeResult:
    ri: float
    mi: float
    ri_grade: str
    mi_grade: str


def _grade_label(value: float, t1: float, t2: float) -> str:
    if value < t1:
        return "一级"
    if value < t2:
        return "二级"
    return "三级"


def load_rules(standards_dir: Path) -> dict[str, Any]:
    path = standards_dir / "rules.yaml"
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def defect_contribution(rules: dict[str, Any], code: str, level: int, kind: str) -> float:
    table_key = "structural_defects" if kind == "structural" else "functional_defects"
    table = rules.get(table_key, {})
    if code not in table:
        return 0.0
    by_level = table[code]
    return float(by_level.get(level, by_level.get(str(level), 0.0)))


def evaluate_segment(
    rules: dict[str, Any],
    defects: list[tuple[str, int, str]],
    *,
    K: float | None = None,
    E: float | None = None,
    T: float | None = None,
) -> GradeResult:
    """defects: list of (code, level, kind). kind in structural|functional."""
    d = rules.get("defaults", {})
    K = K if K is not None else float(d.get("K", 1.0))
    E = E if E is not None else float(d.get("E", 1.0))
    T = T if T is not None else float(d.get("T", 1.0))

    F = 0.0
    G = 0.0
    for code, level, kind in defects:
        w = defect_contribution(rules, code, level, kind)
        if kind == "structural":
            F = max(F, w)
        else:
            G = max(G, w)

    formulas = rules.get("formulas", {})
    if formulas.get("structural") == "F_times_K_E_T":
        ri = F * K * E * T
    else:
        ri = F * K * E * T

    if formulas.get("functional") == "G_times_K_T":
        mi = G * K * T
    else:
        mi = G * K * T

    gt = rules.get("grade_thresholds", {})
    t1 = float(gt.get("level_1_max", 4))
    t2 = float(gt.get("level_2_max", 7))

    return GradeResult(
        ri=round(ri, 3),
        mi=round(mi, 3),
        ri_grade=_grade_label(ri, t1, t2),
        mi_grade=_grade_label(mi, t1, t2),
    )
