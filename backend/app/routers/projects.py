"""Project API."""
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import Project
from app.schemas import ProjectCreate, ProjectRead

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.post("", response_model=ProjectRead)
async def create_project(body: ProjectCreate, db: AsyncSession = Depends(get_db)) -> Project:
    p = Project(**body.model_dump())
    db.add(p)
    await db.commit()
    await db.refresh(p)
    return p


@router.get("", response_model=list[ProjectRead])
async def list_projects(db: AsyncSession = Depends(get_db)) -> Sequence[Project]:
    r = await db.execute(select(Project).order_by(Project.id.desc()))
    return r.scalars().all()


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, db: AsyncSession = Depends(get_db)) -> Project:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    return p
