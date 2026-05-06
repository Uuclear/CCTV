"""Assemble docx context from ORM."""
from __future__ import annotations

from sqlalchemy.orm import selectinload

from app.models import Segment


def build_segments_body(segments: list[Segment]) -> str:
    lines: list[str] = []
    for seg in segments:
        ri, mi = seg.ri, seg.mi
        lines.append(
            f"管段 ID-{seg.id} 起止:{seg.chain_start_label or '-'}～{seg.chain_end_label or '-'} "
            f"RI={ri if ri is not None else '-'}({seg.ri_grade or '-'}) "
            f"MI={mi if mi is not None else '-'}({seg.mi_grade or '-'})"
        )
        for d in seg.defects:
            k = "结构" if d.kind == "structural" else "功能"
            note = f" 备注:{d.note}" if d.note else ""
            lines.append(f"  · 缺陷 {d.defect_code} 等级{d.level} {k}{note}")
    return "\n".join(lines) if lines else "（暂无管段）"


def segment_loader_options():
    return [selectinload(Segment.defects)]
