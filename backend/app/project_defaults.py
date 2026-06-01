"""Project field defaults and code prefixes (report-mapping.md)."""
from __future__ import annotations

DEFAULT_INSPECTION_ORG = "上海建科检验检测认证有限公司"
DEFAULT_SITE_MANAGER = "胡跃进"
DEFAULT_REPORT_AUTHOR = "秦臻"
DEFAULT_QC_MANAGER = "张峙琪"
PREFIX_PROJECT_CODE = "CC01-"
PREFIX_REPORT_NO = "CC018-"
CODE_SUFFIX_DIGITS = 6


def with_prefix(value: str | None, prefix: str) -> str | None:
    if value is None:
        return None
    v = value.strip()
    if not v:
        return None
    if v.upper().startswith(prefix.upper()):
        return v
    return f"{prefix}{v}"


def apply_create_defaults(data: dict) -> dict:
    out = dict(data)
    if not out.get("inspection_org"):
        out["inspection_org"] = DEFAULT_INSPECTION_ORG
    if not out.get("site_manager"):
        out["site_manager"] = DEFAULT_SITE_MANAGER
    if not out.get("report_author"):
        out["report_author"] = DEFAULT_REPORT_AUTHOR
    if not out.get("qc_manager"):
        out["qc_manager"] = DEFAULT_QC_MANAGER
    if out.get("project_code"):
        out["project_code"] = with_prefix(out["project_code"], PREFIX_PROJECT_CODE)
    if out.get("report_no"):
        out["report_no"] = with_prefix(out["report_no"], PREFIX_REPORT_NO)
    return out
