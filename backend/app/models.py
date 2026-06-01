"""ORM models."""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(256), index=True)
    client_org: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    build_org: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    supervision_org: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    design_org: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    construction_org: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    project_code: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    report_no: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    road_name: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    scope_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    contact_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    site_address: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    inspection_org: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    site_manager: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    report_author: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    qc_manager: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    k_value_default: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=3)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    segments: Mapped[list["Segment"]] = relationship("Segment", back_populates="project", cascade="all, delete-orphan")


class Segment(Base):
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True)
    original_filename: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    video_relpath: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    preview_frame_relpath: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    preview_sample_time_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    chain_start_label: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    chain_end_label: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    pipe_system: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    diameter_mm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pipe_length_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pipe_material: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    repair_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    remark: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    inspection_date: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    parse_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    parse_warnings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ri: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mi: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ri_grade: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    mi_grade: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="segments")
    defects: Mapped[list["Defect"]] = relationship("Defect", back_populates="segment", cascade="all, delete-orphan")


class Defect(Base):
    __tablename__ = "defects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id", ondelete="CASCADE"), index=True)
    defect_code: Mapped[str] = mapped_column(String(64))
    level: Mapped[int] = mapped_column(Integer, default=1)
    kind: Mapped[str] = mapped_column(String(16), default="structural")
    clock_position: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    distance_m: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    segment: Mapped["Segment"] = relationship("Segment", back_populates="defects")
