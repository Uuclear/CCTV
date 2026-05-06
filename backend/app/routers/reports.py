"""Generate inspection reports (docx / pdf)."""
from __future__ import annotations

import uuid
from datetime import date
from pathlib import Path

from docxtpl import DocxTemplate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import Project, Segment
from app.services.pdf_export import PdfExportError, docx_to_pdf
from app.services.report_build import build_report_context, segment_loader_options

router = APIRouter(tags=["reports"])


async def render_project_docx(project_id: int, db: AsyncSession) -> Path:
    proj = await db.get(Project, project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="project not found")
    r = await db.execute(
        select(Segment)
        .where(Segment.project_id == project_id)
        .options(*segment_loader_options())
        .order_by(Segment.id),
    )
    segments = list(r.scalars().all())
    tpl = settings.report_template_docx.resolve()
    if not tpl.is_file():
        raise HTTPException(status_code=500, detail=f"report template missing: {tpl}")
    out_dir = (settings.files_dir / "reports" / str(project_id)).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_name = f"report_{date.today().isoformat()}_{uuid.uuid4().hex[:8]}.docx"
    out_path = out_dir / out_name
    doc = DocxTemplate(str(tpl))
    doc.render(build_report_context(proj, segments, report_date=date.today()))
    doc.save(str(out_path))
    return out_path


@router.post("/api/projects/{project_id}/reports/docx")
async def export_docx(project_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    out_path = await render_project_docx(project_id, db)
    rel = out_path.relative_to(settings.files_dir.resolve()).as_posix()
    return {"docx_relpath": rel, "media_url": f"/media/{rel}"}


@router.post("/api/projects/{project_id}/reports/pdf")
async def export_pdf(project_id: int, db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    docx_path = await render_project_docx(project_id, db)
    pdf_path = docx_path.with_suffix(".pdf")
    try:
        docx_to_pdf(docx_path, pdf_path)
    except PdfExportError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    prel = pdf_path.relative_to(settings.files_dir.resolve()).as_posix()
    drel = docx_path.relative_to(settings.files_dir.resolve()).as_posix()
    return {"pdf_relpath": prel, "docx_relpath": drel, "media_url": f"/media/{prel}"}


@router.get("/api/projects/{project_id}/reports/download-docx")
async def download_latest_docx(project_id: int, db: AsyncSession = Depends(get_db)):
    """Render fresh docx and return as attachment (optional helper for browsers)."""
    from fastapi.responses import FileResponse

    path = await render_project_docx(project_id, db)
    return FileResponse(
        path,
        filename=path.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )
