# AI 壁纸生成：文生图 / 图生图（Pollinations）
"""Cursor 的 GenerateImage 仅供 Cloud Agent 对话使用，应用后端无法调用。
许愿池运行时使用 Pollinations：
- txt2img: flux 文生图
- img2img: kontext 图生图（需参考图 URL）
"""

from __future__ import annotations

import re
import uuid
from urllib.parse import quote

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.db import SessionLocal
from app.models import Category, Wallpaper, Wish
from app.services.wallpaper_ops import slugify


def build_txt2img_url(prompt: str, width: int, height: int) -> str:
    """构造文生图 URL（flux）。"""
    text = quote(prompt.strip(), safe="")
    return (
        f"https://image.pollinations.ai/prompt/{text}"
        f"?width={width}&height={height}&nologo=true"
        f"&model={settings.ai_image_model}&enhance=true"
    )


def build_img2img_url(prompt: str, source_image: str, width: int, height: int) -> str:
    """构造图生图 URL（参考图 image + 选定模型）。"""
    text = quote(prompt.strip(), safe="")
    # 参考图 URL 原样放入查询参数（httpx/服务端会处理）
    model = settings.ai_img2img_model
    return (
        f"https://image.pollinations.ai/prompt/{text}"
        f"?model={model}&image={quote(source_image, safe='')}"
        f"&width={width}&height={height}&nologo=true&enhance=true"
    )


def download_image(url: str) -> bytes:
    """下载生成结果图片字节。"""
    with httpx.Client(timeout=180.0, follow_redirects=True) as client:
        res = client.get(url)
        res.raise_for_status()
        ctype = res.headers.get("content-type", "")
        if "image" not in ctype and len(res.content) < 1024:
            raise RuntimeError(f"生成结果不是图片: {ctype}")
        return res.content


def ensure_ai_category(db: Session) -> Category:
    """确保存在「AI许愿」分类。"""
    cat = db.query(Category).filter(Category.slug == "ai-wish").first()
    if cat:
        return cat
    cat = Category(
        name="AI许愿",
        slug="ai-wish",
        description="由许愿池 Prompt 生成的 AI 壁纸",
        cover_url="",
        sort_order=99,
        is_active=True,
    )
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


def publish_wallpaper(db: Session, wish: Wish, local_url: str) -> Wallpaper:
    """将生成结果发布为壁纸条目。"""
    cat = ensure_ai_category(db)
    title = wish.prompt.strip().replace("\n", " ")
    if len(title) > 40:
        title = title[:40] + "…"
    mode_tag = "文生图" if wish.mode != "img2img" else "图生图"
    base_slug = slugify(f"ai-{wish.id}-{title}") or f"ai-wish-{wish.id}"
    slug = base_slug
    n = 1
    while db.query(Wallpaper).filter(Wallpaper.slug == slug).first():
        slug = f"{base_slug}-{n}"
        n += 1
    item = Wallpaper(
        title=f"许愿·{title}",
        slug=slug,
        description=f"AI {mode_tag}：{wish.prompt}",
        image_url=local_url,
        thumb_url=local_url,
        width=wish.width,
        height=wish.height,
        tags=f"AI,许愿,{mode_tag}",
        palette="#3F8F7A",
        style_hint="vivid",
        is_featured=False,
        is_published=settings.ai_wish_auto_publish,
        category_id=cat.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def fulfill_wish(wish_id: int, public_base: str = "") -> None:
    """后台兑现单条许愿：文生图或图生图。"""
    db = SessionLocal()
    try:
        wish = db.get(Wish, wish_id)
        if not wish:
            return
        wish.status = "generating"
        wish.error_message = ""
        wish.provider = settings.ai_image_provider
        db.commit()

        if wish.mode == "img2img":
            source = wish.source_image_url
            if source.startswith("/"):
                if not public_base:
                    raise RuntimeError("图生图缺少公网 Base URL，无法让生图服务读取参考图")
                source = public_base.rstrip("/") + source
            remote = build_img2img_url(wish.prompt, source, wish.width, wish.height)
        else:
            remote = build_txt2img_url(wish.prompt, wish.width, wish.height)

        raw = download_image(remote)
        name = f"wish-{wish.id}-{uuid.uuid4().hex[:10]}.jpg"
        dest = settings.upload_dir / name
        dest.write_bytes(raw)
        local_url = f"/uploads/{name}"

        wish.image_url = local_url
        if settings.ai_wish_auto_publish:
            paper = publish_wallpaper(db, wish, local_url)
            wish.wallpaper_id = paper.id
        wish.status = "done"
        db.commit()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        wish = db.get(Wish, wish_id)
        if wish:
            wish.status = "failed"
            wish.error_message = str(exc)[:500]
            db.commit()
    finally:
        db.close()


def sanitize_prompt(prompt: str) -> str:
    """轻度清洗 prompt，去掉控制字符。"""
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", prompt).strip()
