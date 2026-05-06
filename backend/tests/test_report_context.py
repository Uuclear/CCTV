"""Report context dict used by docxtpl."""
from datetime import date

from app.models import Project
from app.services.report_build import build_report_context


def test_build_report_context_includes_project_fields():
    p = Project(
        id=1,
        name="N",
        client_org="C",
        project_code="P",
        road_name="R",
        scope_text="S",
        contact_name="张",
        contact_phone="138",
    )
    ctx = build_report_context(p, [], report_date=date(2026, 5, 7))
    assert ctx["project_name"] == "N"
    assert ctx["client_org"] == "C"
    assert ctx["project_code"] == "P"
    assert ctx["road_name"] == "R"
    assert ctx["scope_text"] == "S"
    assert ctx["contact_name"] == "张"
    assert ctx["contact_phone"] == "138"
    assert ctx["report_date"] == "2026-05-07"
    assert "body" in ctx
