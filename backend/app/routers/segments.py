"""Segment & defect API with index recompute."""
from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.db import get_db
from app.models import Defect, Project, Segment
from app.schemas import DefectCreate, DefectRead, SegmentCreate, SegmentRead, SegmentUpdate
from app.services.evaluation import evaluate_segment, load_rules

router = APIRouter(tags=["segments"])


async def _recompute_segment(db: AsyncSession, seg: Segment) -> None:
    rules = load_rules(settings.standards_dir)
    r = await db.execute(select(Defect).where(Defect.segment_id == seg.id))
    defects_rows = r.scalars().all()
    triples = [(d.defect_code, d.level, d.kind) for d in defects_rows]
    result = evaluate_segment(rules, triples)
    seg.ri = result.ri
    seg.mi = result.mi
    seg.ri_grade = result.ri_grade
    seg.mi_grade = result.mi_grade


@router.post("/api/projects/{project_id}/segments", response_model=SegmentRead)
async def create_segment(
    project_id: int,
    body: SegmentCreate,
    db: AsyncSession = Depends(get_db),
) -> Segment:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    seg = Segment(project_id=project_id, **body.model_dump())
    db.add(seg)
    await db.commit()
    await db.refresh(seg)
    await _recompute_segment(db, seg)
    await db.commit()
    await db.refresh(seg)
    return seg


@router.get("/api/projects/{project_id}/segments", response_model=list[SegmentRead])
async def list_segments(project_id: int, db: AsyncSession = Depends(get_db)) -> Sequence[Segment]:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    r = await db.execute(select(Segment).where(Segment.project_id == project_id).order_by(Segment.id))
    return r.scalars().all()


@router.get("/api/segments/{segment_id}", response_model=SegmentRead)
async def get_segment(segment_id: int, db: AsyncSession = Depends(get_db)) -> Segment:
    seg = await db.get(Segment, segment_id)
    if not seg:
        raise HTTPException(status_code=404, detail="segment not found")
    return seg


@router.patch("/api/segments/{segment_id}", response_model=SegmentRead)
async def patch_segment(
    segment_id: int,
    body: SegmentUpdate,
    db: AsyncSession = Depends(get_db),
) -> Segment:
    seg = await db.get(Segment, segment_id)
    if not seg:
        raise HTTPException(status_code=404, detail="segment not found")
    for k, v in body.model_dump(exclude_unset=True).items():
        setattr(seg, k, v)
    await db.commit()
    await db.refresh(seg)
    return seg


@router.post("/api/segments/{segment_id}/defects", response_model=DefectRead)
async def create_defect(
    segment_id: int,
    body: DefectCreate,
    db: AsyncSession = Depends(get_db),
) -> Defect:
    seg = await db.get(Segment, segment_id)
    if not seg:
        raise HTTPException(status_code=404, detail="segment not found")
    d = Defect(segment_id=segment_id, **body.model_dump())
    db.add(d)
    await db.commit()
    await db.refresh(d)
    seg2 = await db.get(Segment, segment_id)
    assert seg2 is not None
    await _recompute_segment(db, seg2)
    await db.commit()
    await db.refresh(d)
    return d


@router.get("/api/segments/{segment_id}/defects", response_model=list[DefectRead])
async def list_defects(segment_id: int, db: AsyncSession = Depends(get_db)) -> Sequence[Defect]:
    seg = await db.get(Segment, segment_id)
    if not seg:
        raise HTTPException(status_code=404, detail="segment not found")
    r = await db.execute(select(Defect).where(Defect.segment_id == segment_id).order_by(Defect.id))
    return r.scalars().all()
