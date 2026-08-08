/** 壁纸馆：筛选、排序、多风格展示 */
import { startTransition, useDeferredValue, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type { Category, SortKey, ViewMode, Wallpaper } from "../api/types";
import SiteHeader from "../components/SiteHeader";
import CategoryChips from "../components/CategoryChips";
import ViewSwitch from "../components/ViewSwitch";
import WallpaperGallery from "../components/WallpaperGallery";
import Lightbox from "../components/Lightbox";

/** 主浏览页：分类 + 搜索 + 四种布局 */
export default function GalleryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [categories, setCategories] = useState<Category[]>([]);
  const [items, setItems] = useState<Wallpaper[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState(searchParams.get("category") || "");
  const [sort, setSort] = useState<SortKey>("newest");
  const [query, setQuery] = useState("");
  const deferredQuery = useDeferredValue(query);
  const [mode, setMode] = useState<ViewMode>(() => {
    return (localStorage.getItem("muse_view_mode") as ViewMode) || "masonry";
  });
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  useEffect(() => {
    api.categories().then(setCategories);
  }, []);

  /** 同步分类到地址栏，便于从分类页跳转 */
  function changeCategory(slug: string) {
    setCategory(slug);
    const next = new URLSearchParams(searchParams);
    if (slug) next.set("category", slug);
    else next.delete("category");
    setSearchParams(next, { replace: true });
  }

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .wallpapers({
        category: category || undefined,
        q: deferredQuery || undefined,
        sort,
        page_size: 48,
      })
      .then((res) => {
        if (cancelled) return;
        setItems(res.items);
        setTotal(res.total);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [category, deferredQuery, sort]);

  /** 切换展示风格并持久化 */
  function changeMode(next: ViewMode) {
    startTransition(() => {
      setMode(next);
      localStorage.setItem("muse_view_mode", next);
    });
  }

  return (
    <div className="app-shell">
      <SiteHeader />
      <section className="section">
        <div className="section-head">
          <div>
            <h2>壁纸馆</h2>
            <p>
              共 {total} 张 · 当前风格「
              {{ masonry: "瀑布", grid: "网格", cinema: "影院", river: "溪流" }[mode]}」
            </p>
          </div>
          <ViewSwitch value={mode} onChange={changeMode} />
        </div>

        <div className="toolbar">
          <input
            className="search-box"
            placeholder="搜索标题、标签或描述…"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <select
            className="select-box"
            value={sort}
            onChange={(e) => setSort(e.target.value as SortKey)}
          >
            <option value="newest">最新</option>
            <option value="popular">最热浏览</option>
            <option value="likes">最多喜欢</option>
            <option value="downloads">最多下载</option>
          </select>
        </div>

        <CategoryChips categories={categories} value={category} onChange={changeCategory} />

        <div style={{ marginTop: "1.25rem" }}>
          {loading ? (
            <div className="loading">正在铺开画面…</div>
          ) : (
            <WallpaperGallery
              items={items}
              mode={mode}
              onOpen={(_, index) => setOpenIndex(index)}
            />
          )}
        </div>
      </section>

      {openIndex !== null && (
        <Lightbox
          items={items}
          index={openIndex}
          onClose={() => setOpenIndex(null)}
          onIndexChange={setOpenIndex}
          onUpdate={(item) =>
            setItems((prev) => prev.map((w) => (w.id === item.id ? item : w)))
          }
        />
      )}
    </div>
  );
}
