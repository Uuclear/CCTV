import pytest

from app.services.evaluation import evaluate_segment, load_rules
from app.config import settings


def test_evaluate_structural_only():
    rules = load_rules(settings.standards_dir)
    r = evaluate_segment(rules, [("PL", 2, "structural")])
    assert r.ri > 0
    assert r.mi == 0.0
    assert r.ri_grade in ("一级", "二级", "三级")


def test_evaluate_functional_only():
    rules = load_rules(settings.standards_dir)
    r = evaluate_segment(rules, [("CJ", 3, "functional")])
    assert r.mi > 0
    assert r.ri == 0.0
