/** 多风格壁纸画廊容器 */
import { useState } from "react";
import type { ViewMode, Wallpaper } from "../api/types";
import WallpaperTile from "./WallpaperTile";

interface Props {
  items: Wallpaper[];
  mode: ViewMode;
  onOpen: (item: Wallpaper, index: number) => void;
}

/** 影院模式舞台与胶片条 */
function CinemaView({
  items,
  onOpen,
}: {
  items: Wallpaper[];
  onOpen: (item: Wallpaper, index: number) => void;
}) {
  const [active, setActive] = useState(0);
  if (!items.length) return null;
  const current = items[Math.min(active, items.length - 1)];

  return (
    <div className="cinema">
      <div className="cinema-stage" onClick={() => onOpen(current, active)}>
        <img src={current.image_url} alt={current.title} />
        <div className="cinema-caption">
          <div>
            <h3>{current.title}</h3>
            <p>
              {current.category_name || "未分类"} · {current.description || "点击查看大图"}
            </p>
          </div>
          <button type="button" className="solid-btn" onClick={() => onOpen(current, active)}>
            沉浸查看
          </button>
        </div>
      </div>
      <div className="cinema-strip">
        {items.map((item, i) => (
          <button
            key={item.id}
            type="button"
            className={i === active ? "active" : ""}
            onClick={() => setActive(i)}
          >
            <img src={item.thumb_url || item.image_url} alt={item.title} />
          </button>
        ))}
      </div>
    </div>
  );
}

/** 按模式渲染瀑布 / 网格 / 影院 / 溪流 */
export default function WallpaperGallery({ items, mode, onOpen }: Props) {
  if (!items.length) {
    return <div className="empty">暂无匹配的壁纸，试试其他分类或关键词。</div>;
  }

  if (mode === "cinema") {
    return <CinemaView items={items} onOpen={onOpen} />;
  }

  return (
    <div className={`gallery ${mode}`}>
      {items.map((item, index) => (
        <WallpaperTile
          key={item.id}
          item={item}
          index={index}
          tall={mode === "masonry"}
          onOpen={() => onOpen(item, index)}
        />
      ))}
    </div>
  );
}
