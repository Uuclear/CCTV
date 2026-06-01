"""Project API."""
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Project
from app.project_defaults import apply_create_defaults, with_prefix
from app.project_defaults import PREFIX_PROJECT_CODE, PREFIX_REPORT_NO
from app.schemas import ProjectCreate, ProjectRead, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _normalize_update(data: dict) -> dict:
    out = dict(data)
    if "project_code" in out and out["project_code"]:
        out["project_code"] = with_prefix(out["project_code"], PREFIX_PROJECT_CODE)
    if "report_no" in out and out["report_no"]:
        out["report_no"] = with_prefix(out["report_no"], PREFIX_REPORT_NO)
    return out


@router.post("", response_model=ProjectRead)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)) -> Project:
    p = Project(**apply_create_defaults(body.model_dump()))
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("", response_model=list[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_db)) -> Sequence[Project]:
    r = await db.execute(select(Project).order_by(Project.id.desc()))
    return r.scalars().all()


@router.patch("/{project_id}", response_model=ProjectRead)
async def patch_project(
    project_id: int,
    body: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
) -> Project:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    for k, v in _normalize_update(body.model_dump(exclude_unset=True)).items():
        setattr(p, k, v)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)) -> Project:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    return p
