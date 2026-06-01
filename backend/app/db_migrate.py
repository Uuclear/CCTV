"""Lightweight SQLite column migrations (create_all does not ALTER)."""
from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.engine import Connection


_PROJECT_COLUMNS: list[tuple[str, str]] = [
    ("report_no", "VARCHAR(128)"),
    ("build_org", "VARCHAR(256)"),
    ("supervision_org", "VARCHAR(256)"),
    ("design_org", "VARCHAR(256)"),
    ("construction_org", "VARCHAR(256)"),
    ("site_address", "VARCHAR(512)"),
    ("inspection_org", "VARCHAR(256)"),
    ("site_manager", "VARCHAR(128)"),
    ("k_value_default", "INTEGER"),
    ("report_author", "VARCHAR(128)"),
    ("qc_manager", "VARCHAR(128)"),
]

_SEGMENT_COLUMNS: list[tuple[str, str]] = [
    ("diameter_mm", "INTEGER"),
    ("pipe_material", "VARCHAR(128)"),
    ("inspection_date", "VARCHAR(16)"),
    ("parse_confidence", "FLOAT"),
    ("parse_warnings", "TEXT"),
    ("pipe_system", "VARCHAR(32)"),
    ("pipe_length_m", "FLOAT"),
    ("repair_index", "FLOAT"),
    ("remark", "TEXT"),
    ("preview_sample_time_sec", "FLOAT"),
]


def _has_column(conn: Connection, table: str, column: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
    return any(row[1] == column for row in rows)


def _add_column(conn: Connection, table: str, column: str, sql_type: str) -> None:
    if not _has_column(conn, table, column):
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {sql_type}"))


def migrate_sqlite_schema(sync_conn: Connection) -> None:
    if sync_conn.dialect.name != "sqlite":
        return
    for col, typ in _PROJECT_COLUMNS:
        _add_column(sync_conn, "projects", col, typ)
    for col, typ in _SEGMENT_COLUMNS:
        _add_column(sync_conn, "segments", col, typ)
    # 历史数据：状况等级应为「一级」而非 0
    sync_conn.execute(
        text(
            "UPDATE segments SET ri_grade='一级' "
            "WHERE ri_grade IS NULL OR trim(ri_grade) IN ('0', '0级', '0.0', '', '1', '1级')"
        )
    )
    sync_conn.execute(
        text(
            "UPDATE segments SET mi_grade='一级' "
            "WHERE mi_grade IS NULL OR trim(mi_grade) IN ('0', '0级', '0.0', '', '1', '1级')"
        )
    )
