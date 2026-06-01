"""Standard defect catalog for UI dropdowns."""
from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings
from app.services.evaluation import load_rules

router = APIRouter(tags=["standards"])


class DefectCatalogItem(BaseModel):
    code: str
    name: str
    kind: str
    max_level: int
    mi_exclude: bool = False


@router.get("/api/standards/defects", response_model=list[DefectCatalogItem])
async def list_defect_catalog() -> list[DefectCatalogItem]:
    rules = load_rules(settings.standards_dir)
    out: list[DefectCatalogItem] = []
    for code, row in (rules.get("structural_defects") or {}).items():
        levels = [k for k in row if isinstance(k, int) or (isinstance(k, str) and k.isdigit())]
        max_lv = max((int(k) for k in levels), default=4)
        out.append(
            DefectCatalogItem(
                code=code,
                name=str(row.get("name", code)),
                kind="structural",
                max_level=max_lv,
            )
        )
    for code, row in (rules.get("functional_defects") or {}).items():
        levels = [k for k in row if isinstance(k, int) or (isinstance(k, str) and k.isdigit())]
        max_lv = max((int(k) for k in levels), default=4)
        out.append(
            DefectCatalogItem(
                code=code,
                name=str(row.get("name", code)),
                kind="functional",
                max_level=max_lv,
                mi_exclude=bool(row.get("mi_exclude")),
            )
        )
    return sorted(out, key=lambda x: (x.kind, x.code))
