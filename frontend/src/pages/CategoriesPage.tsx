/** 分类浏览页 */
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Category } from "../api/types";
import SiteHeader from "../components/SiteHeader";

/** 展示所有启用分类的封面入口 */
export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);

  useEffect(() => {
    api.categories().then(setCategories);
  }, []);

  return (
    <div className="app-shell">
      <SiteHeader />
      <section className="section">
        <div className="section-head">
          <div>
            <h2>按气质分类</h2>
            <p>从山海到抽象，找到与屏幕相符的情绪色调</p>
          </div>
        </div>
        <div className="category-grid">
          {categories.map((c) => (
            <Link key={c.id} to={`/gallery?category=${c.slug}`} className="category-card">
              <img src={c.cover_url} alt={c.name} loading="lazy" />
              <div className="body">
                <h3>{c.name}</h3>
                <p>
                  {c.description} · {c.wallpaper_count} 张
                </p>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
