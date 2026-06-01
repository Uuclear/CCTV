"""Project exports (statistics xlsx)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import Project
from app.services.statistics_xlsx import build_statistics_xlsx

router = APIRouter(tags=["exports"])


@router.get("/api/projects/{project_id}/export/statistics.xlsx")
async def export_statistics_xlsx(
    project_id: int,
    db: AsyncSession = Depends(get_db),
) -> Response:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    data = await build_statistics_xlsx(db, project_id, settings.repo_root)
    filename = f"statistics_project_{project_id}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
