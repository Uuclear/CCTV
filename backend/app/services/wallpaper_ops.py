# 壁纸序列化与 slug 辅助
import hashlib
import re
import unicodedata

from app.models import Wallpaper
from app.schemas import WallpaperOut


def slugify(text: str) -> str:
    """将标题转为 URL 友好 slug；中文标题回退短哈希。"""
    ascii_part = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    ascii_part = re.sub(r"[^\w\s-]", "", ascii_part.lower())
    ascii_part = re.sub(r"[-\s]+", "-", ascii_part).strip("-")
    if ascii_part:
        return ascii_part
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]
    return f"w-{digest}"


def to_wallpaper_out(item: Wallpaper) -> WallpaperOut:
    """将 ORM 壁纸转为对外 DTO。"""
    data = WallpaperOut.model_validate(item)
    if item.category:
        data.category_name = item.category.name
        data.category_slug = item.category.slug
    return data
