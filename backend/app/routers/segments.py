"""Segment & defect API with index recompute."""
import uuid
from typing import Sequence

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import Defect, Project, Segment
from app.schemas import (
    DefectCreate,
    DefectRead,
    ExtractPreviewBody,
    OcrPreviewOut,
    SegmentCreate,
    SegmentRead,
    SegmentReadWithSample,
    SegmentUpdate,
)
from app.services import ocr_text, pipe_regex, video_frames
from app.services.evaluation import evaluate_segment, load_rules
from app.services.path_policy import resolve_absolute_allowed, resolve_under_dir

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


def _safe_upload_name(name: str | None) -> str:
    raw = (name or "video.mp4").replace("\\", "/").split("/")[-1].strip()
    if not raw or raw in (".", ".."):
        return "video.mp4"
    return raw[-200:]


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


@router.post("/api/segments/{segment_id}/video", response_model=SegmentRead)
async def upload_segment_video(
    segment_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
) -> Segment:
    seg = await db.get(Segment, segment_id)
    if not seg:
        raise HTTPException(status_code=404, detail="segment not found")
    safe_name = _safe_upload_name(file.filename)
    rel_dir = f"uploads/{seg.project_id}/{seg.id}"
    dest_dir = (settings.files_dir / rel_dir).resolve()
    if not dest_dir.is_relative_to(settings.files_dir.resolve()):
        raise HTTPException(status_code=400, detail="invalid upload path")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = (dest_dir / safe_name).resolve()
    if not dest.is_relative_to(settings.files_dir.resolve()):
        raise HTTPException(status_code=400, detail="invalid file name")
    dest.write_bytes(await file.read())
    seg.video_relpath = f"{rel_dir}/{safe_name}".replace("\\", "/")
    await db.commit()
    await db.refresh(seg)
    return seg


@router.post("/api/segments/{segment_id}/extract-preview", response_model=SegmentReadWithSample)
async def extract_segment_preview(
    segment_id: int,
    body: ExtractPreviewBody = ExtractPreviewBody(),
    db: AsyncSession = Depends(get_db),
) -> SegmentReadWithSample:
    seg = await db.get(Segment, segment_id)
    if not seg:
        raise HTTPException(status_code=404, detail="segment not found")
    roots = [settings.files_dir, settings.repo_root]
    if body.source_absolute:
        video_path = resolve_absolute_allowed(body.source_absolute, roots)
    elif seg.video_relpath:
        video_path = resolve_under_dir(settings.files_dir, seg.video_relpath)
    else:
        raise HTTPException(
            status_code=400,
            detail="segment has no video_relpath; upload a video or pass source_absolute",
        )

    out_rel = f"previews/{seg.project_id}/{seg.id}/{uuid.uuid4().hex}.png"
    out_path = resolve_under_dir(settings.files_dir, out_rel)

    try:
        t = video_frames.extract_preview_png(
            video_path,
            out_path,
            margin_sec=body.margin_sec,
            seed=body.seed,
        )
    except video_frames.VideoProbeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except video_frames.FFmpegError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    seg.preview_frame_relpath = out_rel.replace("\\", "/")
    await db.commit()
    await db.refresh(seg)
    row = SegmentRead.model_validate(seg)
    return SegmentReadWithSample(**row.model_dump(), sample_time_sec=t)


@router.post("/api/segments/{segment_id}/ocr-preview", response_model=OcrPreviewOut)
async def ocr_segment_preview(
    segment_id: int,
    db: AsyncSession = Depends(get_db),
) -> OcrPreviewOut:
    seg = await db.get(Segment, segment_id)
    if not seg:
        raise HTTPException(status_code=404, detail="segment not found")
    if not seg.preview_frame_relpath:
        raise HTTPException(status_code=400, detail="no preview_frame_relpath; extract a preview first")
    img = resolve_under_dir(settings.files_dir, seg.preview_frame_relpath)
    if not img.is_file():
        raise HTTPException(status_code=400, detail="preview image missing on disk")
    raw = ocr_text.image_to_text(img)
    a, b = pipe_regex.suggest_pipe_range(raw)
    engine = "rapidocr_onnxruntime" if raw else "none"
    return OcrPreviewOut(
        raw_text=raw,
        suggested_chain_start=a,
        suggested_chain_end=b,
        engine=engine,
    )


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
