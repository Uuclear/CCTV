/** 全屏灯箱：键盘切换、点赞与下载 */
import { useEffect } from "react";
import type { Wallpaper } from "../api/types";
import { api } from "../api/client";

interface Props {
  items: Wallpaper[];
  index: number;
  onClose: () => void;
  onIndexChange: (index: number) => void;
  onUpdate: (item: Wallpaper) => void;
}

/** 壁纸沉浸查看器 */
export default function Lightbox({ items, index, onClose, onIndexChange, onUpdate }: Props) {
  const item = items[index];

  useEffect(() => {
    /** 键盘：Esc 关闭，左右键切换 */
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      if (e.key === "ArrowRight") onIndexChange((index + 1) % items.length);
      if (e.key === "ArrowLeft") onIndexChange((index - 1 + items.length) % items.length);
    };
    window.addEventListener("keydown", handler);
    document.body.style.overflow = "hidden";
    return () => {
      window.removeEventListener("keydown", handler);
      document.body.style.overflow = "";
    };
  }, [index, items.length, onClose, onIndexChange]);

  if (!item) return null;

  /** 点赞并回写状态 */
  async function handleLike() {
    const updated = await api.like(item.id);
    onUpdate(updated);
  }

  /** 记录下载并打开原图 */
  async function handleDownload() {
    const updated = await api.download(item.id);
    onUpdate(updated);
    window.open(item.image_url, "_blank", "noopener,noreferrer");
  }

  return (
    <div className="lightbox" role="dialog" aria-modal="true" aria-label={item.title}>
      <button type="button" className="lightbox-close" onClick={onClose} aria-label="关闭">
        ×
      </button>
      <button
        type="button"
        className="lightbox-nav prev"
        onClick={() => onIndexChange((index - 1 + items.length) % items.length)}
        aria-label="上一张"
      >
        ‹
      </button>
      <button
        type="button"
        className="lightbox-nav next"
        onClick={() => onIndexChange((index + 1) % items.length)}
        aria-label="下一张"
      >
        ›
      </button>
      <div className="lightbox-panel">
        <div className="lightbox-image">
          <img src={item.image_url} alt={item.title} />
        </div>
        <aside className="lightbox-side">
          <h2>{item.title}</h2>
          <p style={{ margin: 0, color: "var(--muted)" }}>{item.description || "暂无描述"}</p>
          <div className="meta-row">
            <span className="meta-pill">{item.category_name || "未分类"}</span>
            <span className="meta-pill">
              {item.width}×{item.height}
            </span>
            <span className="meta-pill">浏览 {item.views}</span>
            <span className="meta-pill">喜欢 {item.likes}</span>
            <span className="meta-pill">下载 {item.downloads}</span>
          </div>
          {item.tags && (
            <div className="meta-row">
              {item.tags.split(/[,，]/).map((t) => (
                <span className="meta-pill" key={t}>
                  #{t.trim()}
                </span>
              ))}
            </div>
          )}
          <div className="lightbox-actions">
            <button type="button" className="solid-btn" onClick={handleLike}>
              喜欢
            </button>
            <button type="button" className="ghost-btn" onClick={handleDownload}>
              下载原图
            </button>
            <button type="button" className="ghost-btn" onClick={onClose}>
              关闭
            </button>
          </div>
        </aside>
      </div>
    </div>
  );
}
