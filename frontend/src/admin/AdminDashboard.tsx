/** 后台概览仪表盘 */
import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Stats } from "../api/types";

/** 展示壁纸与互动核心指标 */
export default function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    api.stats().then(setStats);
  }, []);

  if (!stats) return <div className="loading">加载统计…</div>;

  const cards = [
    { label: "壁纸总数", value: stats.wallpaper_count },
    { label: "已发布", value: stats.published_count },
    { label: "精选", value: stats.featured_count },
    { label: "分类", value: stats.category_count },
    { label: "总浏览", value: stats.total_views },
    { label: "总喜欢", value: stats.total_likes },
    { label: "总下载", value: stats.total_downloads },
  ];

  return (
    <div>
      <h2 style={{ fontFamily: "var(--font-display)", marginTop: 0 }}>运营概览</h2>
      <div className="stats-grid">
        {cards.map((c) => (
          <div className="stat" key={c.label}>
            <strong>{c.value}</strong>
            <span>{c.label}</span>
          </div>
        ))}
      </div>
      <div className="panel">
        <h2>快速指引</h2>
        <p style={{ color: "var(--muted)", margin: 0 }}>
          先在「分类管理」维护气质标签，再到「壁纸管理」通过外链或本地上传发布。前台支持瀑布、网格、影院、溪流四种展示风格，并按分类/搜索/排序筛选。
        </p>
      </div>
    </div>
  );
}
