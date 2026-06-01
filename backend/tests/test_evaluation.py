"""算例单测：锁定 rules.yaml + evaluation 行为（须与 DB31/CJJ 181 条文一起维护）。"""

import pytest

from app.config import settings
from app.services.evaluation import evaluate_segment, load_rules


def test_evaluate_structural_only():
    rules = load_rules(settings.standards_dir)
    r = evaluate_segment(rules, [("PL", 2, "structural")])
    # PL 2 级分值 3；默认 K=E=T=1 → RI=3
    assert r.ri == 3.0
    assert r.mi == 0.0
    assert r.ri_grade == "一级"
    assert r.mi_grade == "一级"


def test_evaluate_functional_only():
    rules = load_rules(settings.standards_dir)
    r = evaluate_segment(rules, [("CJ", 3, "functional")])
    # CJ 3 级分值 5；MI = G×K×E（无 T），默认 1 → 5
    assert r.mi == 5.0
    assert r.ri == 0.0


def test_mi_uses_k_and_e_not_t():
    """CJJ 181 8.4.4：养护指数式中含 K、E；不含土质 T。"""
    rules = load_rules(settings.standards_dir)
    r = evaluate_segment(rules, [("CJ", 1, "functional")], K=2.0, E=3.0, T=100.0)
    # G=1, MI = 1*1*2*3 = 6（若误乘 T 会得到 200）
    assert r.mi == 6.0


def test_ri_includes_t():
    rules = load_rules(settings.standards_dir)
    r = evaluate_segment(rules, [("PL", 2, "structural")], K=2.0, E=2.0, T=2.0)
    # F=3, RI = 3*2*2*2 = 24
    assert r.ri == 24.0


def test_computation_coefficients_apply():
    rules = load_rules(settings.standards_dir)
    rules = dict(rules)
    rules["computation"] = {
        "ri": {"coefficient": 0.7},
        "mi": {"coefficient": 0.7},
    }
    r = evaluate_segment(rules, [("PL", 4, "structural")], K=1.0, E=1.0, T=1.0)
    # F=10, RI=7
    assert r.ri == 7.0
    r2 = evaluate_segment(rules, [("CJ", 3, "functional")], K=1.0, E=1.0, T=1.0)
    assert r2.mi == 3.5


def test_grade_thresholds_level_2():
    rules = load_rules(settings.standards_dir)
    # F=5, 默认系数 1, K=E=T=1 → RI=5 → 二级（4≤x<7）
    r = evaluate_segment(rules, [("BX", 3, "structural")])
    assert r.ri_grade == "二级"


def test_max_of_multiple_structural_defects():
    """简化 F：取结构性缺陷最高分值（严重者优先）。"""
    rules = load_rules(settings.standards_dir)
    r = evaluate_segment(
        rules,
        [
            ("PL", 1, "structural"),
            ("CW", 4, "structural"),
        ],
    )
    assert r.ri == 10.0
