/** 首页：品牌 Hero + 精选壁纸入口 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Wallpaper } from "../api/types";
import SiteHeader from "../components/SiteHeader";
import WallpaperGallery from "../components/WallpaperGallery";
import Lightbox from "../components/Lightbox";

/** 渲染幕色落地页首屏与精选区 */
export default function HomePage() {
  const [featured, setFeatured] = useState<Wallpaper[]>([]);
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  useEffect(() => {
    api.wallpapers({ featured: true, page_size: 8, sort: "popular" }).then((res) => {
      setFeatured(res.items);
    });
  }, []);

  const hero = featured[0];

  return (
    <div className="app-shell">
      <SiteHeader />
      <section className="hero">
        <div className="hero-media">
          {hero ? (
            <img src={hero.image_url} alt={hero.title} />
          ) : (
            <div style={{ width: "100%", height: "100%", background: "var(--ink-2)" }} />
          )}
        </div>
        <div className="hero-copy">
          <h1 className="hero-brand">幕色</h1>
          <p className="hero-title">为屏幕找到恰到好处的气息</p>
          <p className="hero-desc">
            按山海、都市、极简、暗调等气质分类浏览，在瀑布、网格、影院与溪流四种风格间切换，沉浸挑选你的下一张壁纸。
          </p>
          <div className="hero-actions">
            <Link className="solid-btn" to="/gallery">
              进入壁纸馆
            </Link>
            <Link className="ghost-btn" to="/categories">
              浏览分类
            </Link>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-head">
          <div>
            <h2>本周精选</h2>
            <p>编辑挑选的气质画面，点击即可沉浸查看</p>
          </div>
          <Link className="ghost-btn" to="/gallery">
            查看全部
          </Link>
        </div>
        {featured.length ? (
          <WallpaperGallery
            items={featured}
            mode="masonry"
            onOpen={(_, index) => setOpenIndex(index)}
          />
        ) : (
          <div className="loading">正在点亮精选…</div>
        )}
      </section>

      <footer className="site-footer">
        <span>幕色 Muse · 壁纸馆</span>
        <span>默认管理员 admin / admin123</span>
      </footer>

      {openIndex !== null && (
        <Lightbox
          items={featured}
          index={openIndex}
          onClose={() => setOpenIndex(null)}
          onIndexChange={setOpenIndex}
          onUpdate={(item) =>
            setFeatured((prev) => prev.map((w) => (w.id === item.id ? item : w)))
          }
        />
      )}
    </div>
  );
}
