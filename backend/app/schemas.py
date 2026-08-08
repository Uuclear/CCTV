# Pydantic 请求/响应模型
from datetime import datetime

from pydantic import BaseModel, Field


class TokenOut(BaseModel):
    """登录成功返回的访问令牌。"""

    access_token: str
    token_type: str = "bearer"


class LoginIn(BaseModel):
    """管理员登录请求。"""

    username: str
    password: str


class CategoryIn(BaseModel):
    """分类创建/更新入参。"""

    name: str = Field(min_length=1, max_length=64)
    slug: str = Field(min_length=1, max_length=64)
    description: str = ""
    cover_url: str = ""
    sort_order: int = 0
    is_active: bool = True


class CategoryOut(BaseModel):
    """分类对外输出。"""

    id: int
    name: str
    slug: str
    description: str
    cover_url: str
    sort_order: int
    is_active: bool
    wallpaper_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}


class WallpaperIn(BaseModel):
    """壁纸创建/更新入参。"""

    title: str = Field(min_length=1, max_length=160)
    slug: str = ""
    description: str = ""
    image_url: str = ""
    thumb_url: str = ""
    width: int = 1920
    height: int = 1080
    tags: str = ""
    palette: str = "#1a2332"
    style_hint: str = "soft"
    is_featured: bool = False
    is_published: bool = True
    category_id: int | None = None


class WallpaperOut(BaseModel):
    """壁纸对外输出。"""

    id: int
    title: str
    slug: str
    description: str
    image_url: str
    thumb_url: str
    width: int
    height: int
    tags: str
    palette: str
    style_hint: str
    downloads: int
    views: int
    likes: int
    is_featured: bool
    is_published: bool
    category_id: int | None
    category_name: str | None = None
    category_slug: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WallpaperListOut(BaseModel):
    """壁纸分页列表。"""

    total: int
    items: list[WallpaperOut]


class StatsOut(BaseModel):
    """后台概览统计。"""

    wallpaper_count: int
    published_count: int
    featured_count: int
    category_count: int
    total_views: int
    total_downloads: int
    total_likes: int
    wish_count: int = 0
    wish_done_count: int = 0


class WishIn(BaseModel):
    """提交 AI 壁纸许愿（JSON：文生图或外链图生图）。"""

    prompt: str = Field(min_length=2, max_length=1200)
    author_name: str = Field(default="匿名", max_length=64)
    mode: str = Field(default="txt2img", pattern="^(txt2img|img2img)$")
    source_image_url: str = ""
    width: int = Field(default=1920, ge=512, le=2560)
    height: int = Field(default=1080, ge=512, le=2560)


class WishOut(BaseModel):
    """许愿对外输出。"""

    id: int
    prompt: str
    author_name: str
    mode: str = "txt2img"
    status: str
    width: int
    height: int
    provider: str
    source_image_url: str = ""
    image_url: str
    error_message: str
    wallpaper_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WishListOut(BaseModel):
    """许愿列表。"""

    total: int
    items: list[WishOut]
