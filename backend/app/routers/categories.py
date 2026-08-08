# 分类公开查询与后台管理
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.db import get_db
from app.models import AdminUser, Category, Wallpaper
from app.schemas import CategoryIn, CategoryOut

router = APIRouter(prefix="/api/categories", tags=["categories"])


def _with_count(db: Session, cat: Category) -> CategoryOut:
    """附加分类下已发布壁纸数量。"""
    count = (
        db.query(func.count(Wallpaper.id))
        .filter(Wallpaper.category_id == cat.id, Wallpaper.is_published.is_(True))
        .scalar()
        or 0
    )
    out = CategoryOut.model_validate(cat)
    out.wallpaper_count = count
    return out


@router.get("", response_model=list[CategoryOut])
def list_categories(
    db: Annotated[Session, Depends(get_db)],
    active_only: bool = True,
) -> list[CategoryOut]:
    """列出分类，前台默认仅返回启用项。"""
    q = db.query(Category)
    if active_only:
        q = q.filter(Category.is_active.is_(True))
    rows = q.order_by(Category.sort_order.asc(), Category.id.asc()).all()
    return [_with_count(db, c) for c in rows]


@router.get("/{slug}", response_model=CategoryOut)
def get_category(slug: str, db: Annotated[Session, Depends(get_db)]) -> CategoryOut:
    """按 slug 获取单个分类。"""
    cat = db.query(Category).filter(Category.slug == slug).first()
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="分类不存在")
    return _with_count(db, cat)


@router.post("", response_model=CategoryOut)
def create_category(
    body: CategoryIn,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
) -> CategoryOut:
    """后台新建分类。"""
    if db.query(Category).filter(Category.slug == body.slug).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    cat = Category(**body.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return _with_count(db, cat)


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: int,
    body: CategoryIn,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
) -> CategoryOut:
    """后台更新分类。"""
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="分类不存在")
    clash = (
        db.query(Category)
        .filter(Category.slug == body.slug, Category.id != category_id)
        .first()
    )
    if clash:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="slug 已存在")
    for key, value in body.model_dump().items():
        setattr(cat, key, value)
    db.commit()
    db.refresh(cat)
    return _with_count(db, cat)


@router.delete("/{category_id}")
def delete_category(
    category_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
) -> dict:
    """删除分类；其下壁纸变为未分类。"""
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="分类不存在")
    db.query(Wallpaper).filter(Wallpaper.category_id == category_id).update(
        {"category_id": None}
    )
    db.delete(cat)
    db.commit()
    return {"ok": True}
