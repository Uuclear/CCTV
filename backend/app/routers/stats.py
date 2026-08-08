# 后台统计概览
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.db import get_db
from app.models import AdminUser, Category, Wallpaper, Wish
from app.schemas import StatsOut

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=StatsOut)
def get_stats(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
) -> StatsOut:
    """汇总壁纸与互动数据供后台仪表盘使用。"""
    wallpaper_count = db.query(func.count(Wallpaper.id)).scalar() or 0
    published_count = (
        db.query(func.count(Wallpaper.id)).filter(Wallpaper.is_published.is_(True)).scalar() or 0
    )
    featured_count = (
        db.query(func.count(Wallpaper.id)).filter(Wallpaper.is_featured.is_(True)).scalar() or 0
    )
    category_count = db.query(func.count(Category.id)).scalar() or 0
    total_views = db.query(func.coalesce(func.sum(Wallpaper.views), 0)).scalar() or 0
    total_downloads = db.query(func.coalesce(func.sum(Wallpaper.downloads), 0)).scalar() or 0
    total_likes = db.query(func.coalesce(func.sum(Wallpaper.likes), 0)).scalar() or 0
    wish_count = db.query(func.count(Wish.id)).scalar() or 0
    wish_done_count = (
        db.query(func.count(Wish.id)).filter(Wish.status == "done").scalar() or 0
    )
    return StatsOut(
        wallpaper_count=wallpaper_count,
        published_count=published_count,
        featured_count=featured_count,
        category_count=category_count,
        total_views=int(total_views),
        total_downloads=int(total_downloads),
        total_likes=int(total_likes),
        wish_count=wish_count,
        wish_done_count=wish_done_count,
    )
