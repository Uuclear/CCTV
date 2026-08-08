# 批量写入约 2000 张壁纸（picsum 确定性外链）
"""用法: cd backend && PYTHONPATH=. python scripts/bulk_seed_wallpapers.py [--count 2000]"""

from __future__ import annotations

import argparse
import random
from datetime import UTC, datetime, timedelta

from app.db import Base, SessionLocal, engine
from app.models import Category, Wallpaper
from app.seed import ensure_seed

# 标题词库：按分类组合生成中文名
TITLE_PARTS = {
    "landscape": (["晨雾", "暮色", "远山", "湖畔", "海岸", "旷野", "雪岭", "峡谷"], ["阿尔卑斯", "北境", "东岸", "高原", "岛屿", "河谷"]),
    "urban": (["雨夜", "霓虹", "午夜", "钢骨", "巷口", "天桥", "车站", "天际"], ["东京", "上海", "纽约", "首尔", "伦敦", "都市"]),
    "minimal": (["留白", "几何", "单色", "静物", "折纸", "沙丘", "光斑", "线条"], ["空间", "墙面", "曲面", "晨光", "余白", "秩序"]),
    "noir": (["低光", "雾廊", "阴影", "暗巷", "月光", "烟尘", "深井", "黑潮"], ["剧场", "走廊", "森林", "码头", "屋顶", "隧道"]),
    "flora": (["苔藓", "晨露", "叶脉", "竹影", "藤蔓", "松针", "花瓣", "青苔"], ["细部", "庭院", "雨林", "温室", "溪边", "山径"]),
    "abstract": (["流体", "纹理", "丝绸", "波纹", "色块", "噪点", "渐变", "漩涡"], ["实验", "颜料", "织物", "光晕", "节奏", "梦境"]),
}

TAG_POOL = {
    "landscape": "山,水,自然,风景",
    "urban": "城市,建筑,夜景,街道",
    "minimal": "极简,留白,几何,干净",
    "noir": "暗调,雾,阴影,低对比",
    "flora": "植物,绿色,纹理,自然",
    "abstract": "抽象,色彩,纹理,艺术",
}

PALETTES = [
    "#6B8FA3",
    "#C9895A",
    "#2B3A55",
    "#7A8B99",
    "#D6CFC7",
    "#1F2E24",
    "#0D1117",
    "#3D6B4F",
    "#4A6FA5",
    "#8B6F8E",
    "#5A7A8C",
    "#1C2430",
    "#3A4A6B",
    "#B8A089",
]

STYLE_HINTS = ["soft", "warm", "cool", "noir", "vivid"]
RESOLUTIONS = [(3840, 2160), (2560, 1440), (2400, 1600), (1920, 1080), (1600, 2400), (1440, 2560)]


def make_title(rng: random.Random, slug: str, index: int) -> str:
    """按分类词库拼出可读标题。"""
    left, right = TITLE_PARTS[slug]
    return f"{rng.choice(left)}·{rng.choice(right)} #{index:04d}"


def build_rows(categories: list[Category], count: int, start_index: int) -> list[Wallpaper]:
    """构造待写入的壁纸 ORM 列表。"""
    rng = random.Random(20260808)
    rows: list[Wallpaper] = []
    if not categories:
        return rows
    for i in range(count):
        n = start_index + i
        cat = categories[i % len(categories)]
        width, height = RESOLUTIONS[i % len(RESOLUTIONS)]
        seed = f"muse-{n}"
        image = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        thumb = f"https://picsum.photos/seed/{seed}/800/{max(400, int(800 * height / width))}"
        created = datetime.now(UTC).replace(tzinfo=None) - timedelta(
            hours=rng.randint(0, 24 * 120)
        )
        rows.append(
            Wallpaper(
                title=make_title(rng, cat.slug, n),
                slug=f"bulk-{n:05d}",
                description=f"{cat.name}气质壁纸，适合桌面与锁屏。编号 {n:04d}。",
                image_url=image,
                thumb_url=thumb,
                width=width,
                height=height,
                tags=TAG_POOL.get(cat.slug, "壁纸"),
                palette=PALETTES[i % len(PALETTES)],
                style_hint=STYLE_HINTS[i % len(STYLE_HINTS)],
                downloads=rng.randint(0, 800),
                views=rng.randint(0, 5000),
                likes=rng.randint(0, 400),
                is_featured=(n % 37 == 0),
                is_published=True,
                category_id=cat.id,
                created_at=created,
                updated_at=created,
            )
        )
    return rows


def main() -> None:
    """执行批量写入。"""
    parser = argparse.ArgumentParser(description="批量写入壁纸")
    parser.add_argument("--count", type=int, default=2000, help="新增数量")
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_seed(db)
        categories = (
            db.query(Category)
            .filter(Category.is_active.is_(True))
            .order_by(Category.sort_order.asc())
            .all()
        )
        existing_bulk = (
            db.query(Wallpaper).filter(Wallpaper.slug.like("bulk-%")).count()
        )
        start = existing_bulk + 1
        rows = build_rows(categories, args.count, start)
        batch = 200
        for i in range(0, len(rows), batch):
            db.add_all(rows[i : i + batch])
            db.commit()
            print(f"已写入 {min(i + batch, len(rows))}/{len(rows)}")
        total = db.query(Wallpaper).count()
        print(f"完成：新增 {len(rows)} 张，库内合计 {total} 张")
    finally:
        db.close()


if __name__ == "__main__":
    main()
