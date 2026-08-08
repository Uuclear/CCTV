# 初始化管理员账号、分类与示例壁纸
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.config import settings
from app.models import AdminUser, Category, Wallpaper


SEED_CATEGORIES = [
    {
        "name": "山海",
        "slug": "landscape",
        "description": "远山、海岸与旷野的呼吸感",
        "cover_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&q=80",
        "sort_order": 1,
    },
    {
        "name": "都市",
        "slug": "urban",
        "description": "霓虹、街道与建筑的节奏",
        "cover_url": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=1200&q=80",
        "sort_order": 2,
    },
    {
        "name": "极简",
        "slug": "minimal",
        "description": "留白、几何与安静色块",
        "cover_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&q=80",
        "sort_order": 3,
    },
    {
        "name": "暗调",
        "slug": "noir",
        "description": "低光、雾气与戏剧阴影",
        "cover_url": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=1200&q=80",
        "sort_order": 4,
    },
    {
        "name": "植物",
        "slug": "flora",
        "description": "叶脉、苔藓与柔和绿色",
        "cover_url": "https://images.unsplash.com/photo-1518531933037-91b2375b2bf8?w=1200&q=80",
        "sort_order": 5,
    },
    {
        "name": "抽象",
        "slug": "abstract",
        "description": "纹理、流体与色彩实验",
        "cover_url": "https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=1200&q=80",
        "sort_order": 6,
    },
]


SEED_WALLPAPERS = [
    {
        "title": "晨雾阿尔卑斯",
        "slug": "alpine-mist",
        "description": "山脊被薄雾托起，适合桌面沉静开场。",
        "image_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "山,雾,清晨",
        "palette": "#6B8FA3",
        "style_hint": "soft",
        "category_slug": "landscape",
        "is_featured": True,
    },
    {
        "title": "海岸线黄昏",
        "slug": "coastal-dusk",
        "description": "金色海平线与缓慢退潮的沙纹。",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "海,黄昏,沙滩",
        "palette": "#C9895A",
        "style_hint": "warm",
        "category_slug": "landscape",
        "is_featured": True,
    },
    {
        "title": "雨后东京巷口",
        "slug": "tokyo-rain-alley",
        "description": "霓虹倒映在湿润路面上的都市夜色。",
        "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "城市,夜景,霓虹",
        "palette": "#2B3A55",
        "style_hint": "noir",
        "category_slug": "urban",
        "is_featured": True,
    },
    {
        "title": "钢与玻璃",
        "slug": "steel-and-glass",
        "description": "向上生长的摩天楼线条。",
        "image_url": "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1486325212027-8081e485255e?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "建筑,几何,现代",
        "palette": "#7A8B99",
        "style_hint": "cool",
        "category_slug": "urban",
    },
    {
        "title": "纸上几何",
        "slug": "paper-geometry",
        "description": "柔和折痕与干净留白。",
        "image_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "极简,抽象,折纸",
        "palette": "#D6CFC7",
        "style_hint": "soft",
        "category_slug": "minimal",
        "is_featured": True,
    },
    {
        "title": "单色沙丘",
        "slug": "monochrome-dune",
        "description": "风塑造的静谧曲线。",
        "image_url": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1509316785289-025f5b846b35?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "沙漠,极简,曲线",
        "palette": "#B8A089",
        "style_hint": "warm",
        "category_slug": "minimal",
    },
    {
        "title": "雾中森林",
        "slug": "fog-forest",
        "description": "低对比度的深绿与雾气。",
        "image_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "森林,雾,暗调",
        "palette": "#1F2E24",
        "style_hint": "noir",
        "category_slug": "noir",
        "is_featured": True,
    },
    {
        "title": "月光走廊",
        "slug": "moonlit-corridor",
        "description": "建筑阴影里的冷光。",
        "image_url": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1478760329108-5c3ed9d495a0?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "暗调,空间,光影",
        "palette": "#0D1117",
        "style_hint": "noir",
        "category_slug": "noir",
    },
    {
        "title": "苔藓细节",
        "slug": "moss-detail",
        "description": "近距离的绿色纹理。",
        "image_url": "https://images.unsplash.com/photo-1518531933037-91b2375b2bf8?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1518531933037-91b2375b2bf8?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "植物,纹理,绿",
        "palette": "#3D6B4F",
        "style_hint": "soft",
        "category_slug": "flora",
    },
    {
        "title": "晨露叶片",
        "slug": "dew-leaf",
        "description": "透光叶脉与细小水珠。",
        "image_url": "https://images.unsplash.com/photo-1465146633011-14f8e0781093?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1465146633011-14f8e0781093?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "叶片,露水,自然",
        "palette": "#5C8A5E",
        "style_hint": "soft",
        "category_slug": "flora",
        "is_featured": True,
    },
    {
        "title": "流体颜料",
        "slug": "fluid-paint",
        "description": "色彩在水中扩散的瞬间。",
        "image_url": "https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "抽象,流体,色彩",
        "palette": "#4A6FA5",
        "style_hint": "vivid",
        "category_slug": "abstract",
        "is_featured": True,
    },
    {
        "title": "丝绸褶皱",
        "slug": "silk-folds",
        "description": "柔顺布料的光泽层次。",
        "image_url": "https://images.unsplash.com/photo-1550684848-fac1c5b4da2d?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1550684848-fac1c5b4da2d?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "纹理,丝绸,抽象",
        "palette": "#8B6F8E",
        "style_hint": "soft",
        "category_slug": "abstract",
    },
    {
        "title": "北欧湖岸",
        "slug": "nordic-lake",
        "description": "冷色调湖面倒影。",
        "image_url": "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1439066615861-d1af74d74000?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "湖,山,冷色",
        "palette": "#5A7A8C",
        "style_hint": "cool",
        "category_slug": "landscape",
    },
    {
        "title": "午夜地铁",
        "slug": "midnight-metro",
        "description": "空荡站台的线性透视。",
        "image_url": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1514565131-fce0801e5785?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "地铁,夜,都市",
        "palette": "#1C2430",
        "style_hint": "noir",
        "category_slug": "urban",
    },
    {
        "title": "石灰墙面",
        "slug": "lime-wall",
        "description": "干净墙面适合文字桌面。",
        "image_url": "https://images.unsplash.com/photo-1557683316-973673baf926?w=2400&q=85",
        "thumb_url": "https://images.unsplash.com/photo-1557683316-973673baf926?w=800&q=80",
        "width": 2400,
        "height": 1600,
        "tags": "渐变,极简,背景",
        "palette": "#3A4A6B",
        "style_hint": "cool",
        "category_slug": "minimal",
    },
]


def ensure_seed(db: Session) -> None:
    """若库为空则写入默认管理员、分类与示例壁纸。"""
    if not db.query(AdminUser).first():
        db.add(
            AdminUser(
                username=settings.admin_username,
                password_hash=hash_password(settings.admin_password),
            )
        )
        db.commit()

    if db.query(Category).count() == 0:
        for item in SEED_CATEGORIES:
            db.add(Category(**item))
        db.commit()

    if db.query(Wallpaper).count() == 0:
        cats = {c.slug: c for c in db.query(Category).all()}
        for item in SEED_WALLPAPERS:
            payload = dict(item)
            slug = payload.pop("category_slug")
            cat = cats.get(slug)
            db.add(Wallpaper(**payload, category_id=cat.id if cat else None))
        db.commit()
