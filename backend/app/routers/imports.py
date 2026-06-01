"""Batch video import with watermark OCR parsing."""

from __future__ import annotations



import asyncio

import json

import shutil

import uuid

from pathlib import Path



from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from pydantic import BaseModel, Field

from sqlalchemy.ext.asyncio import AsyncSession



from app.config import settings

from app.db import get_db

from app.models import Project, Segment

from app.schemas import SegmentRead

from app.services import ocr_text

from app.services.import_scan import scan_video_file

from app.services.path_policy import resolve_absolute_allowed, resolve_path_under_roots, resolve_under_dir

from app.services.import_helpers import (
    chain_pair_key,
    find_duplicate_segment_ids,
    safe_video_basename,
    try_rename_file,
    unique_path,
)
from app.services.watermark_parse import ParseResult
from sqlalchemy import delete
from typing import Literal



router = APIRouter(tags=["imports"])





class ImportScanItem(BaseModel):

    path: str = Field(..., description="Absolute or repo-relative video path")





class ImportScanRequest(BaseModel):

    items: list[ImportScanItem] = Field(..., min_length=1)





class ImportDraftOut(BaseModel):

    draft_id: str

    source_path: str

    original_filename: str

    preview_frame_relpath: str | None = None

    parse: dict





class ImportCommitItem(BaseModel):

    draft_id: str | None = None

    source_path: str

    chain_start_label: str | None = None

    chain_end_label: str | None = None

    pipe_system: str | None = None

    diameter_mm: int | None = None

    pipe_length_m: float | None = None

    pipe_material: str | None = None

    inspection_date: str | None = None

    display_name: str | None = None

    preview_frame_relpath: str | None = None
    preview_sample_time_sec: float | None = None

    remark: str | None = None
    duplicate_policy: Literal["skip", "overwrite"] = "skip"


class ImportDuplicateCheckItem(BaseModel):
    source_path: str
    chain_start_label: str | None = None
    chain_end_label: str | None = None


class ImportDuplicateCheckRequest(BaseModel):
    items: list[ImportDuplicateCheckItem] = Field(..., min_length=1)


class ImportDuplicateHit(BaseModel):
    source_path: str
    segment_ids: list[int]
    chain_start_label: str | None = None
    chain_end_label: str | None = None


class ImportOcrOneRequest(BaseModel):
    source_path: str


class ImportCommitRequest(BaseModel):
    items: list[ImportCommitItem] = Field(..., min_length=1)





def _parse_result_to_dict(pr: ParseResult, meta: dict | None = None) -> dict:

    out = {

        "chain_start_label": pr.chain_start_label,

        "chain_end_label": pr.chain_end_label,

        "chain_parse_mode": pr.chain_parse_mode,

        "chain_confidence": pr.chain_confidence,

        "chain_source": pr.chain_source,

        "chain_warnings": pr.chain_warnings,

        "diameter_mm": pr.diameter_mm,

        "diameter_raw": pr.diameter_raw,

        "pipe_material": pr.pipe_material,

        "pipe_system": pr.pipe_system,

        "inspection_date": pr.inspection_date,

        "inspection_date_raw": pr.inspection_date_raw,

        "field_confidence": pr.field_confidence,

        "ocr_blocks_used": pr.ocr_blocks_used,

        "filename_stem": pr.filename_stem,

    }

    if meta:

        out["scan"] = meta

    return out





def _draft_stage_only(video_path: Path) -> ImportDraftOut:
    return ImportDraftOut(
        draft_id=uuid.uuid4().hex,
        source_path=str(video_path.resolve()),
        original_filename=video_path.name,
        preview_frame_relpath=None,
        parse={"pending_ocr": True, "scan": {}},
    )


def _draft_from_path(video_path: Path, project_id: int) -> ImportDraftOut:
    pr, preview_rel, meta = scan_video_file(video_path, project_id)
    return ImportDraftOut(
        draft_id=uuid.uuid4().hex,
        source_path=str(video_path.resolve()),
        original_filename=video_path.name,
        preview_frame_relpath=preview_rel,
        parse=_parse_result_to_dict(pr, meta),
    )





async def _scan_path_async(video_path: Path, project_id: int) -> ImportDraftOut:

    return await asyncio.to_thread(_draft_from_path, video_path, project_id)





@router.get("/api/imports/ocr-status")

async def get_ocr_status() -> dict:

    st = ocr_text.ocr_status()

    try:

        import shutil as sh



        st["ffmpeg_on_path"] = sh.which("ffmpeg") is not None

        st["ffprobe_on_path"] = sh.which("ffprobe") is not None

    except Exception:

        st["ffmpeg_on_path"] = False

        st["ffprobe_on_path"] = False

    return st


@router.post("/api/projects/{project_id}/imports/check-duplicates", response_model=list[ImportDuplicateHit])
async def check_import_duplicates(
    project_id: int,
    body: ImportDuplicateCheckRequest,
    db: AsyncSession = Depends(get_db),
) -> list[ImportDuplicateHit]:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    hits: list[ImportDuplicateHit] = []
    for item in body.items:
        ids = await find_duplicate_segment_ids(
            db, project_id, item.chain_start_label, item.chain_end_label
        )
        if ids:
            hits.append(
                ImportDuplicateHit(
                    source_path=item.source_path,
                    segment_ids=ids,
                    chain_start_label=item.chain_start_label,
                    chain_end_label=item.chain_end_label,
                )
            )
    return hits


@router.post("/api/projects/{project_id}/imports/ocr-one", response_model=ImportDraftOut)
async def ocr_one_video(
    project_id: int,
    body: ImportOcrOneRequest,
    db: AsyncSession = Depends(get_db),
) -> ImportDraftOut:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    roots = [settings.files_dir, settings.repo_root]
    video_path = resolve_absolute_allowed(body.source_path, roots)
    return await _scan_path_async(video_path, project_id)


@router.post("/api/projects/{project_id}/imports/scan", response_model=list[ImportDraftOut])

async def scan_videos(

    project_id: int,

    body: ImportScanRequest,

    db: AsyncSession = Depends(get_db),

) -> list[ImportDraftOut]:

    p = await db.get(Project, project_id)

    if not p:

        raise HTTPException(status_code=404, detail="project not found")



    roots = [settings.files_dir, settings.repo_root]

    out: list[ImportDraftOut] = []



    for item in body.items:

        video_path = resolve_absolute_allowed(item.path, roots)

        out.append(await _scan_path_async(video_path, project_id))

    return out





@router.post("/api/projects/{project_id}/imports/commit", response_model=list[SegmentRead])

async def commit_imports(

    project_id: int,

    body: ImportCommitRequest,

    db: AsyncSession = Depends(get_db),

) -> list[Segment]:

    p = await db.get(Project, project_id)

    if not p:

        raise HTTPException(status_code=404, detail="project not found")



    roots = [settings.files_dir, settings.repo_root]

    created: list[Segment] = []



    for item in body.items:
        dup_ids = await find_duplicate_segment_ids(
            db, project_id, item.chain_start_label, item.chain_end_label
        )
        if dup_ids and item.duplicate_policy == "skip":
            continue
        if dup_ids and item.duplicate_policy == "overwrite":
            await db.execute(delete(Segment).where(Segment.id.in_(dup_ids)))

        src = resolve_absolute_allowed(item.source_path, roots)
        named = safe_video_basename(item.chain_start_label, item.chain_end_label)
        dest_dir = settings.files_dir / f"videos/{project_id}"
        dest = unique_path(dest_dir, named)
        if not dest.exists() or src.resolve() != dest.resolve():
            shutil.copy2(src, dest)
        dest_rel = dest.relative_to(settings.files_dir).as_posix()

        if src.is_file():
            try_rename_file(src, src.parent / named)

        preview_rel: str | None = None
        if item.preview_frame_relpath:
            try:
                prev_src = resolve_under_dir(settings.files_dir, item.preview_frame_relpath)
                preview_rel = f"previews/{project_id}/{uuid.uuid4().hex}.png"
                prev_dest = settings.files_dir / preview_rel
                prev_dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(prev_src, prev_dest)
                preview_rel = preview_rel.replace("\\", "/")
            except Exception:
                preview_rel = item.preview_frame_relpath.replace("\\", "/")

        seg = Segment(
            project_id=project_id,
            original_filename=dest.name,
            display_name=item.display_name or _display_name(item),
            video_relpath=dest_rel,
            preview_frame_relpath=preview_rel,
            preview_sample_time_sec=item.preview_sample_time_sec,
            chain_start_label=item.chain_start_label,
            chain_end_label=item.chain_end_label,
            pipe_system=item.pipe_system,
            diameter_mm=item.diameter_mm,
            pipe_length_m=item.pipe_length_m,
            pipe_material=item.pipe_material,
            inspection_date=item.inspection_date,
            remark=item.remark,
            ri=0.0,
            mi=0.0,
            repair_index=0.0,
            ri_grade="一级",
            mi_grade="一级",
        )
        db.add(seg)
        created.append(seg)



    await db.commit()

    for seg in created:

        await db.refresh(seg)

    return created





def _display_name(item: ImportCommitItem) -> str:

    a = item.chain_start_label or "?"

    b = item.chain_end_label or "?"

    return f"{a}～{b}"





class ImportScanFolderRequest(BaseModel):

    folder: str = Field(..., description="Directory under repo or absolute")





@router.post("/api/projects/{project_id}/imports/scan-folder", response_model=list[ImportDraftOut])

async def scan_folder(

    project_id: int,

    body: ImportScanFolderRequest,

    db: AsyncSession = Depends(get_db),

) -> list[ImportDraftOut]:

    p = await db.get(Project, project_id)

    if not p:

        raise HTTPException(status_code=404, detail="project not found")



    roots = [settings.repo_root, settings.files_dir]

    folder = resolve_path_under_roots(body.folder, roots, kind="dir")



    seen: set[str] = set()

    mp4s: list[Path] = []

    for pat in ("*.mp4", "*.MP4", "*.Mp4"):

        for p in sorted(folder.glob(pat)):

            key = str(p.resolve()).lower()

            if key not in seen:

                seen.add(key)

                mp4s.append(p)

    if not mp4s:

        raise HTTPException(status_code=400, detail="no mp4 files in folder")



    out: list[ImportDraftOut] = []

    for mp4 in mp4s:
        out.append(_draft_stage_only(mp4))

    return out


@router.post(
    "/api/projects/{project_id}/imports/scan-folder-stage",
    response_model=list[ImportDraftOut],
)
async def scan_folder_stage(
    project_id: int,
    body: ImportScanFolderRequest,
    db: AsyncSession = Depends(get_db),
) -> list[ImportDraftOut]:
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    roots = [settings.repo_root, settings.files_dir]
    folder = resolve_path_under_roots(body.folder, roots, kind="dir")
    seen: set[str] = set()
    mp4s: list[Path] = []
    for pat in ("*.mp4", "*.MP4"):
        for path in sorted(folder.glob(pat)):
            key = str(path.resolve()).lower()
            if key not in seen:
                seen.add(key)
                mp4s.append(path)
    if not mp4s:
        raise HTTPException(status_code=400, detail="no mp4 files in folder")
    return [_draft_stage_only(mp4) for mp4 in mp4s]


def _safe_upload_name(name: str | None) -> str:

    raw = (name or "video.mp4").replace("\\", "/").split("/")[-1].strip()

    if not raw or raw in (".", ".."):

        return "video.mp4"

    return raw[-200:]





async def _save_upload(project_id: int, f: UploadFile) -> Path | None:

    name = _safe_upload_name(f.filename)

    if not name.lower().endswith(".mp4"):

        return None

    staging = settings.files_dir / "imports" / "staging" / str(project_id)

    staging.mkdir(parents=True, exist_ok=True)

    dest = staging / f"{uuid.uuid4().hex}_{name}"

    content = await f.read()

    if not content:

        return None

    dest.write_bytes(content)

    return dest.resolve()





@router.post("/api/projects/{project_id}/imports/upload-stage-one", response_model=ImportDraftOut)
async def upload_stage_one(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
) -> ImportDraftOut:
    """Upload mp4 only — OCR via /imports/ocr-one or batch OCR in UI."""
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    saved = await _save_upload(project_id, file)
    if saved is None:
        raise HTTPException(status_code=400, detail="file must be a non-empty .mp4")
    return _draft_stage_only(saved)


@router.post("/api/projects/{project_id}/imports/upload-scan-one", response_model=ImportDraftOut)
async def upload_scan_one(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
) -> ImportDraftOut:
    """Legacy: upload + immediate OCR."""
    p = await db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="project not found")
    saved = await _save_upload(project_id, file)
    if saved is None:
        raise HTTPException(status_code=400, detail="file must be a non-empty .mp4")
    return await _scan_path_async(saved, project_id)





@router.post("/api/projects/{project_id}/imports/upload-scan", response_model=list[ImportDraftOut])

async def upload_scan(

    project_id: int,

    db: AsyncSession = Depends(get_db),

    files: list[UploadFile] = File(...),

) -> list[ImportDraftOut]:

    p = await db.get(Project, project_id)

    if not p:

        raise HTTPException(status_code=404, detail="project not found")

    if not files:

        raise HTTPException(status_code=400, detail="no files uploaded")



    saved_paths: list[Path] = []

    for f in files:

        path = await _save_upload(project_id, f)

        if path is not None:

            saved_paths.append(path)



    if not saved_paths:

        raise HTTPException(status_code=400, detail="no mp4 files in upload")



    out: list[ImportDraftOut] = []

    for path in saved_paths:
        out.append(_draft_stage_only(path))

    return out


