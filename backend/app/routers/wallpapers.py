# 壁纸查询、互动与后台 CRUD / 上传
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from PIL import Image
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_admin, get_optional_admin
from app.config import settings
from app.db import get_db
from app.models import AdminUser, Category, Wallpaper
from app.schemas import WallpaperIn, WallpaperListOut, WallpaperOut
from app.services.wallpaper_ops import slugify, to_wallpaper_out

router = APIRouter(prefix="/api/wallpapers", tags=["wallpapers"])


def _base_query(db: Session, published_only: bool):
    """构造带分类关联的查询。"""
    q = db.query(Wallpaper).options(joinedload(Wallpaper.category))
    if published_only:
        q = q.filter(Wallpaper.is_published.is_(True))
    return q


@router.get("", response_model=WallpaperListOut)
def list_wallpapers(
    db: Annotated[Session, Depends(get_db)],
    admin: Annotated[AdminUser | None, Depends(get_optional_admin)],
    q: str | None = None,
    category: str | None = None,
    featured: bool | None = None,
    sort: str = Query("newest", pattern="^(newest|popular|likes|downloads)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
    include_drafts: bool = False,
) -> WallpaperListOut:
    """分页检索壁纸；草稿仅管理员可见。"""
    published_only = not (include_drafts and admin is not None)
    query = _base_query(db, published_only)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Wallpaper.title.ilike(like))
            | (Wallpaper.tags.ilike(like))
            | (Wallpaper.description.ilike(like))
        )
    if category:
        query = query.join(Category).filter(Category.slug == category)
    if featured is True:
        query = query.filter(Wallpaper.is_featured.is_(True))
    order_map = {
        "newest": Wallpaper.created_at.desc(),
        "popular": Wallpaper.views.desc(),
        "likes": Wallpaper.likes.desc(),
        "downloads": Wallpaper.downloads.desc(),
    }
    query = query.order_by(order_map[sort], Wallpaper.id.desc())
    total = query.count()
    rows = query.offset((page - 1) * page_size).limit(page_size).all()
    return WallpaperListOut(total=total, items=[to_wallpaper_out(r) for r in rows])


@router.post("/upload", response_model=WallpaperOut)
async def upload_wallpaper(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
    file: UploadFile = File(...),
    title: str = Form(...),
    slug: str = Form(""),
    description: str = Form(""),
    tags: str = Form(""),
    palette: str = Form("#1a2332"),
    style_hint: str = Form("soft"),
    category_id: int | None = Form(None),
    is_featured: bool = Form(False),
    is_published: bool = Form(True),
) -> WallpaperOut:
    """上传本地图片并创建壁纸。"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="仅支持图片文件")
    raw = await file.read()
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="文件过大")
    final_slug = slug or slugify(title)
    if db.query(Wallpaper).filter(Wallpaper.slug == final_slug).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    ext = Path(file.filename or "img.jpg").suffix.lower() or ".jpg"
    name = f"{uuid.uuid4().hex}{ext}"
    dest = settings.upload_dir / name
    dest.write_bytes(raw)
    width, height = 1920, 1080
    try:
        with Image.open(dest) as im:
            width, height = im.size
    except OSError:
        pass
    url = f"/uploads/{name}"
    item = Wallpaper(
        title=title,
        slug=final_slug,
        description=description,
        image_url=url,
        thumb_url=url,
        width=width,
        height=height,
        tags=tags,
        palette=palette,
        style_hint=style_hint,
        category_id=category_id,
        is_featured=is_featured,
        is_published=is_published,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_wallpaper_out(item)


@router.post("", response_model=WallpaperOut)
def create_wallpaper(
    body: WallpaperIn,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
) -> WallpaperOut:
    """后台创建壁纸（支持外链图片）。"""
    data = body.model_dump()
    if not data.get("slug"):
        data["slug"] = slugify(data["title"])
    if db.query(Wallpaper).filter(Wallpaper.slug == data["slug"]).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    if not data.get("image_url"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="需要 image_url 或上传文件")
    if not data.get("thumb_url"):
        data["thumb_url"] = data["image_url"]
    item = Wallpaper(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return to_wallpaper_out(item)


@router.get("/{wallpaper_id}", response_model=WallpaperOut)
def get_wallpaper(
    wallpaper_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> WallpaperOut:
    """获取壁纸详情并累加浏览量。"""
    item = (
        db.query(Wallpaper)
        .options(joinedload(Wallpaper.category))
        .filter(Wallpaper.id == wallpaper_id)
        .first()
    )
    if not item or not item.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="壁纸不存在")
    item.views += 1
    db.commit()
    db.refresh(item)
    return to_wallpaper_out(item)


@router.post("/{wallpaper_id}/like", response_model=WallpaperOut)
def like_wallpaper(
    wallpaper_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> WallpaperOut:
    """为壁纸点赞。"""
    item = db.get(Wallpaper, wallpaper_id)
    if not item or not item.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="壁纸不存在")
    item.likes += 1
    db.commit()
    db.refresh(item)
    return to_wallpaper_out(item)


@router.post("/{wallpaper_id}/download", response_model=WallpaperOut)
def download_wallpaper(
    wallpaper_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> WallpaperOut:
    """记录一次下载行为。"""
    item = db.get(Wallpaper, wallpaper_id)
    if not item or not item.is_published:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="壁纸不存在")
    item.downloads += 1
    db.commit()
    db.refresh(item)
    return to_wallpaper_out(item)


@router.put("/{wallpaper_id}", response_model=WallpaperOut)
def update_wallpaper(
    wallpaper_id: int,
    body: WallpaperIn,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
) -> WallpaperOut:
    """后台更新壁纸字段。"""
    item = db.get(Wallpaper, wallpaper_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="壁纸不存在")
    data = body.model_dump()
    if not data.get("slug"):
        data["slug"] = item.slug or slugify(data["title"])
    clash = (
        db.query(Wallpaper)
        .filter(Wallpaper.slug == data["slug"], Wallpaper.id != wallpaper_id)
        .first()
    )
    if clash:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    for key, value in data.items():
        if key in ("image_url", "thumb_url") and not value:
            continue
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return to_wallpaper_out(item)


@router.delete("/{wallpaper_id}")
def delete_wallpaper(
    wallpaper_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
) -> dict:
    """删除壁纸记录。"""
    item = db.get(Wallpaper, wallpaper_id)
    if not item:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="壁纸不存在")
    db.delete(item)
    db.commit()
    return {"ok": True}
