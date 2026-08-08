/** 壁纸缩略卡片 */
import type { Wallpaper } from "../api/types";

interface Props {
  item: Wallpaper;
  index: number;
  onOpen: (item: Wallpaper) => void;
  tall?: boolean;
}

/** 单张壁纸入口，支持悬停揭示元信息 */
export default function WallpaperTile({ item, index, onOpen, tall }: Props) {
  const ratio = item.width && item.height ? item.width / item.height : 1.5;
  const style = tall
    ? { aspectRatio: `${Math.max(0.65, Math.min(1.6, ratio))}` }
    : undefined;

  return (
    <article
      className="tile"
      style={{ animationDelay: `${Math.min(index, 12) * 40}ms` }}
      onClick={() => onOpen(item)}
      onKeyDown={(e) => e.key === "Enter" && onOpen(item)}
      role="button"
      tabIndex={0}
    >
      {item.is_featured && <span className="tile-badge">精选</span>}
      <div className="tile-media" style={style}>
        <img src={item.thumb_url || item.image_url} alt={item.title} loading="lazy" />
      </div>
      <div className="tile-meta">
        <h3>{item.title}</h3>
        <p>
          {item.category_name || "未分类"} · {item.width}×{item.height}
        </p>
      </div>
    </article>
  );
}
