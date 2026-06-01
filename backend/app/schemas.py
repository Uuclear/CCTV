"""Pydantic schemas."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    client_org: Optional[str] = None
    build_org: Optional[str] = None
    supervision_org: Optional[str] = None
    design_org: Optional[str] = None
    construction_org: Optional[str] = None
    project_code: Optional[str] = None
    report_no: Optional[str] = None
    road_name: Optional[str] = None
    scope_text: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    site_address: Optional[str] = None
    inspection_org: Optional[str] = None
    site_manager: Optional[str] = None
    report_author: Optional[str] = None
    qc_manager: Optional[str] = None
    k_value_default: Optional[int] = Field(None, ge=0, le=10)


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    client_org: Optional[str]
    build_org: Optional[str]
    supervision_org: Optional[str]
    design_org: Optional[str]
    construction_org: Optional[str]
    project_code: Optional[str]
    report_no: Optional[str]
    road_name: Optional[str]
    scope_text: Optional[str]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    site_address: Optional[str]
    inspection_org: Optional[str]
    site_manager: Optional[str]
    report_author: Optional[str]
    qc_manager: Optional[str]
    k_value_default: Optional[int]
    created_at: datetime


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=256)
    client_org: Optional[str] = None
    build_org: Optional[str] = None
    supervision_org: Optional[str] = None
    design_org: Optional[str] = None
    construction_org: Optional[str] = None
    project_code: Optional[str] = None
    report_no: Optional[str] = None
    road_name: Optional[str] = None
    scope_text: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    site_address: Optional[str] = None
    inspection_org: Optional[str] = None
    site_manager: Optional[str] = None
    report_author: Optional[str] = None
    qc_manager: Optional[str] = None
    k_value_default: Optional[int] = Field(None, ge=0, le=10)


class SegmentCreate(BaseModel):
    original_filename: Optional[str] = None
    display_name: Optional[str] = None
    video_relpath: Optional[str] = None
    preview_frame_relpath: Optional[str] = None
    chain_start_label: Optional[str] = None
    chain_end_label: Optional[str] = None
    pipe_system: Optional[str] = None
    diameter_mm: Optional[int] = Field(None, ge=0)
    pipe_length_m: Optional[float] = Field(None, ge=0)
    pipe_material: Optional[str] = None
    repair_index: Optional[float] = None
    remark: Optional[str] = None
    inspection_date: Optional[str] = None


class SegmentUpdate(BaseModel):
    display_name: Optional[str] = None
    video_relpath: Optional[str] = None
    preview_frame_relpath: Optional[str] = None
    chain_start_label: Optional[str] = None
    chain_end_label: Optional[str] = None
    pipe_system: Optional[str] = None
    diameter_mm: Optional[int] = None
    pipe_length_m: Optional[float] = None
    pipe_material: Optional[str] = None
    repair_index: Optional[float] = None
    remark: Optional[str] = None
    inspection_date: Optional[str] = None


class SegmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    original_filename: Optional[str]
    display_name: Optional[str]
    video_relpath: Optional[str]
    preview_frame_relpath: Optional[str]
    preview_sample_time_sec: Optional[float] = None
    chain_start_label: Optional[str]
    chain_end_label: Optional[str]
    pipe_system: Optional[str]
    diameter_mm: Optional[int]
    pipe_length_m: Optional[float]
    pipe_material: Optional[str]
    repair_index: Optional[float]
    remark: Optional[str]
    inspection_date: Optional[str]
    parse_confidence: Optional[float]
    parse_warnings: Optional[str]
    ri: Optional[float]
    mi: Optional[float]
    ri_grade: Optional[str]
    mi_grade: Optional[str]
    created_at: datetime


class SegmentSummaryRead(SegmentRead):
    defect_count: int = 0
    defect_summary: Optional[str] = None


class DefectCreate(BaseModel):
    defect_code: str = Field(..., min_length=1, max_length=64)
    level: int = Field(1, ge=1, le=4)
    kind: Literal["structural", "functional"] = "structural"
    clock_position: Optional[str] = None
    distance_m: Optional[float] = None
    note: Optional[str] = None


class DefectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    segment_id: int
    defect_code: str
    level: int
    kind: str
    clock_position: Optional[str]
    distance_m: Optional[float]
    note: Optional[str]
    created_at: datetime


class ExtractPreviewBody(BaseModel):
    """Optional overrides for ffmpeg preview."""

    margin_sec: float = Field(1.0, ge=0.0, le=600.0)
    seed: Optional[int] = None
    source_absolute: Optional[str] = None
    """Absolute path on server (must be under repo or files_dir). Dev / LAN convenience."""


class SegmentReadWithSample(SegmentRead):
    sample_time_sec: Optional[float] = None


class OcrPreviewOut(BaseModel):
    raw_text: str
    suggested_chain_start: Optional[str] = None
    suggested_chain_end: Optional[str] = None
    suggested_diameter_mm: Optional[int] = None
    suggested_pipe_material: Optional[str] = None
    suggested_inspection_date: Optional[str] = None
    parse: Optional[dict] = None
    engine: str = "none"
