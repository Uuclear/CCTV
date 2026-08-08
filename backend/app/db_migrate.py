# SQLite 轻量迁移：为已有库补齐许愿池新列
from sqlalchemy import inspect, text

from app.db import engine


def ensure_wish_columns() -> None:
    """给 wishes 表补上 mode / source_image_url（若不存在）。"""
    insp = inspect(engine)
    if "wishes" not in insp.get_table_names():
        return
    cols = {c["name"] for c in insp.get_columns("wishes")}
    with engine.begin() as conn:
        if "mode" not in cols:
            conn.execute(text("ALTER TABLE wishes ADD COLUMN mode VARCHAR(16) DEFAULT 'txt2img'"))
        if "source_image_url" not in cols:
            conn.execute(
                text("ALTER TABLE wishes ADD COLUMN source_image_url VARCHAR(512) DEFAULT ''")
            )
