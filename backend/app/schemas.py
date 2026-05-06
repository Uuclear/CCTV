"""Pydantic schemas."""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=256)
    client_org: Optional[str] = None
    project_code: Optional[str] = None
    road_name: Optional[str] = None
    scope_text: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    client_org: Optional[str]
    project_code: Optional[str]
    road_name: Optional[str]
    scope_text: Optional[str]
    contact_name: Optional[str]
    contact_phone: Optional[str]
    created_at: datetime


class SegmentCreate(BaseModel):
    original_filename: Optional[str] = None
    display_name: Optional[str] = None
    video_relpath: Optional[str] = None
    preview_frame_relpath: Optional[str] = None
    chain_start_label: Optional[str] = None
    chain_end_label: Optional[str] = None


class SegmentUpdate(BaseModel):
    display_name: Optional[str] = None
    video_relpath: Optional[str] = None
    preview_frame_relpath: Optional[str] = None
    chain_start_label: Optional[str] = None
    chain_end_label: Optional[str] = None


class SegmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    original_filename: Optional[str]
    display_name: Optional[str]
    video_relpath: Optional[str]
    preview_frame_relpath: Optional[str]
    chain_start_label: Optional[str]
    chain_end_label: Optional[str]
    ri: Optional[float]
    mi: Optional[float]
    ri_grade: Optional[str]
    mi_grade: Optional[str]
    created_at: datetime


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
