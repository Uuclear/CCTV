# AI 壁纸许愿池 API
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_admin
from app.config import settings
from app.db import get_db
from app.models import AdminUser, Wish
from app.schemas import WishIn, WishListOut, WishOut
from app.services.ai_generate import fulfill_wish, sanitize_prompt

router = APIRouter(prefix="/api/wishes", tags=["wishes"])


@router.get("/meta/provider")
def provider_info() -> dict:
    """返回当前生图提供方说明（含 Cursor 能力边界）。"""
    return {
        "provider": settings.ai_image_provider,
        "model": settings.ai_image_model,
        "cursor_native": False,
        "note": (
            "Cursor 的 GenerateImage 仅供 Cloud Agent 对话侧使用，"
            "无法被网站/APK 后端直接调用。"
            "许愿池运行时使用 Pollinations 文生图接口兑现 Prompt。"
        ),
    }


@router.get("", response_model=WishListOut)
def list_wishes(
    db: Annotated[Session, Depends(get_db)],
    status_filter: str | None = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100),
) -> WishListOut:
    """分页列出许愿（最新优先）。"""
    q = db.query(Wish)
    if status_filter:
        q = q.filter(Wish.status == status_filter)
    q = q.order_by(Wish.id.desc())
    total = q.count()
    rows = q.offset((page - 1) * page_size).limit(page_size).all()
    return WishListOut(total=total, items=[WishOut.model_validate(r) for r in rows])


@router.post("", response_model=WishOut, status_code=status.HTTP_201_CREATED)
def create_wish(
    body: WishIn,
    background: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
) -> WishOut:
    """提交 Prompt 到许愿池，并异步触发生成。"""
    prompt = sanitize_prompt(body.prompt)
    if len(prompt) < 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="prompt 太短")
    wish = Wish(
        prompt=prompt,
        author_name=(body.author_name or "匿名").strip()[:64] or "匿名",
        width=body.width or settings.ai_default_width,
        height=body.height or settings.ai_default_height,
        status="pending",
        provider=settings.ai_image_provider,
    )
    db.add(wish)
    db.commit()
    db.refresh(wish)
    background.add_task(fulfill_wish, wish.id)
    return WishOut.model_validate(wish)


@router.get("/{wish_id}", response_model=WishOut)
def get_wish(wish_id: int, db: Annotated[Session, Depends(get_db)]) -> WishOut:
    """查询单条许愿状态。"""
    wish = db.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="许愿不存在")
    return WishOut.model_validate(wish)


@router.post("/{wish_id}/retry", response_model=WishOut)
def retry_wish(
    wish_id: int,
    background: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
) -> WishOut:
    """失败/待处理许愿重新生成。"""
    wish = db.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="许愿不存在")
    if wish.status == "generating":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="正在生成中")
    wish.status = "pending"
    wish.error_message = ""
    db.commit()
    background.add_task(fulfill_wish, wish.id)
    return WishOut.model_validate(wish)


@router.delete("/{wish_id}")
def delete_wish(
    wish_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[AdminUser, Depends(get_current_admin)],
) -> dict:
    """管理员删除许愿记录。"""
    wish = db.get(Wish, wish_id)
    if not wish:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="许愿不存在")
    db.delete(wish)
    db.commit()
    return {"ok": True}
