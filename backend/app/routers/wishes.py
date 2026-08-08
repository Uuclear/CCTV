# AI 壁纸许愿池 API：文生图 / 图生图
import uuid
from pathlib import Path
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
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
    """返回生图能力与 Cursor 关联说明。"""
    return {
        "provider": settings.ai_image_provider,
        "txt2img_model": settings.ai_image_model,
        "img2img_model": settings.ai_img2img_model,
        "modes": ["txt2img", "img2img"],
        "cursor_native": False,
        "cursor_linkable": False,
        "note": (
            "Cursor 的 GenerateImage 只存在于 Cloud Agent 对话工具层，"
            "没有可供网站/APK/后端调用的官方 API，因此无法关联到 Cursor 生图。"
            "许愿池使用 Pollinations：文生图与图生图（参考图 URL / 上传）。"
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


def _enqueue(
    db: Session,
    background: BackgroundTasks,
    *,
    prompt: str,
    author_name: str,
    mode: str,
    source_image_url: str,
    width: int,
    height: int,
) -> Wish:
    """写入许愿并投递后台生成任务。"""
    wish = Wish(
        prompt=prompt,
        author_name=author_name,
        mode=mode,
        source_image_url=source_image_url,
        width=width,
        height=height,
        status="pending",
        provider=settings.ai_image_provider,
    )
    db.add(wish)
    db.commit()
    db.refresh(wish)
    background.add_task(fulfill_wish, wish.id, settings.public_base_url)
    return wish


@router.post("", response_model=WishOut, status_code=status.HTTP_201_CREATED)
def create_wish(
    body: WishIn,
    background: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
) -> WishOut:
    """JSON 提交：文生图，或带 source_image_url 的图生图。"""
    prompt = sanitize_prompt(body.prompt)
    if len(prompt) < 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="prompt 太短")
    mode = body.mode or "txt2img"
    source = (body.source_image_url or "").strip()
    if mode == "img2img" and not source:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="图生图需要 source_image_url")
    wish = _enqueue(
        db,
        background,
        prompt=prompt,
        author_name=(body.author_name or "匿名").strip()[:64] or "匿名",
        mode=mode,
        source_image_url=source,
        width=body.width or settings.ai_default_width,
        height=body.height or settings.ai_default_height,
    )
    return WishOut.model_validate(wish)


@router.post("/upload", response_model=WishOut, status_code=status.HTTP_201_CREATED)
async def create_wish_with_upload(
    background: BackgroundTasks,
    db: Annotated[Session, Depends(get_db)],
    prompt: str = Form(...),
    author_name: str = Form("匿名"),
    mode: str = Form("img2img"),
    width: int = Form(1080),
    height: int = Form(1920),
    file: UploadFile | None = File(None),
    source_image_url: str = Form(""),
) -> WishOut:
    """表单提交：可上传参考图做图生图，也可纯文生图。"""
    clean = sanitize_prompt(prompt)
    if len(clean) < 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="prompt 太短")
    if mode not in {"txt2img", "img2img"}:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="mode 无效")
    source = source_image_url.strip()
    if mode == "img2img":
        if file is not None and file.filename:
            if not file.content_type or not file.content_type.startswith("image/"):
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="仅支持图片文件")
            raw = await file.read()
            if len(raw) > settings.max_upload_mb * 1024 * 1024:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="文件过大")
            ext = Path(file.filename).suffix.lower() or ".jpg"
            name = f"wish-src-{uuid.uuid4().hex}{ext}"
            (settings.upload_dir / name).write_bytes(raw)
            source = f"/uploads/{name}"
        if not source:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="图生图需要参考图")
    wish = _enqueue(
        db,
        background,
        prompt=clean,
        author_name=(author_name or "匿名").strip()[:64] or "匿名",
        mode=mode,
        source_image_url=source,
        width=width,
        height=height,
    )
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
    background.add_task(fulfill_wish, wish.id, settings.public_base_url)
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
