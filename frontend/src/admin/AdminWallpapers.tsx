/** 壁纸管理：外链创建、本地上传与列表编辑 */
import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { Category, Wallpaper } from "../api/types";

const emptyForm = {
  title: "",
  slug: "",
  description: "",
  image_url: "",
  thumb_url: "",
  tags: "",
  palette: "#1a2332",
  style_hint: "soft",
  category_id: "" as string | number,
  is_featured: false,
  is_published: true,
  width: 1920,
  height: 1080,
};

/** 管理全部壁纸内容 */
export default function AdminWallpapers() {
  const [items, setItems] = useState<Wallpaper[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [form, setForm] = useState({ ...emptyForm });
  const [file, setFile] = useState<File | null>(null);
  const [editId, setEditId] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  /** 拉取草稿可见的壁纸列表 */
  async function load() {
    const [list, cats] = await Promise.all([
      api.wallpapers({ include_drafts: true, page_size: 100, sort: "newest" }, true),
      api.categories(false),
    ]);
    setItems(list.items);
    setCategories(cats);
  }

  useEffect(() => {
    load();
  }, []);

  /** 提交创建/更新或上传 */
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const categoryId = form.category_id === "" ? null : Number(form.category_id);
      if (file && !editId) {
        const fd = new FormData();
        fd.append("file", file);
        fd.append("title", form.title);
        fd.append("slug", form.slug);
        fd.append("description", form.description);
        fd.append("tags", form.tags);
        fd.append("palette", form.palette);
        fd.append("style_hint", form.style_hint);
        fd.append("is_featured", String(form.is_featured));
        fd.append("is_published", String(form.is_published));
        if (categoryId) fd.append("category_id", String(categoryId));
        await api.uploadWallpaper(fd);
      } else {
        const body = {
          ...form,
          category_id: categoryId,
          thumb_url: form.thumb_url || form.image_url,
        };
        if (editId) await api.updateWallpaper(editId, body);
        else await api.createWallpaper(body);
      }
      setForm({ ...emptyForm });
      setFile(null);
      setEditId(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h2 style={{ fontFamily: "var(--font-display)", marginTop: 0 }}>壁纸管理</h2>
      <div className="panel">
        <h2>{editId ? "编辑壁纸" : "发布壁纸"}</h2>
        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            标题
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              required
            />
          </label>
          <label>
            Slug
            <input
              value={form.slug}
              onChange={(e) => setForm({ ...form, slug: e.target.value })}
              placeholder="可留空由上传接口生成"
            />
          </label>
          <label className="full">
            描述
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </label>
          <label className="full">
            图片 URL（外链）
            <input
              value={form.image_url}
              onChange={(e) => setForm({ ...form, image_url: e.target.value })}
              disabled={!!file}
            />
          </label>
          <label className="full">
            或上传本地图片
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              disabled={!!editId}
            />
          </label>
          <label>
            分类
            <select
              value={form.category_id}
              onChange={(e) => setForm({ ...form, category_id: e.target.value })}
            >
              <option value="">未分类</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            标签
            <input
              value={form.tags}
              onChange={(e) => setForm({ ...form, tags: e.target.value })}
              placeholder="逗号分隔"
            />
          </label>
          <label>
            色板
            <input
              value={form.palette}
              onChange={(e) => setForm({ ...form, palette: e.target.value })}
            />
          </label>
          <label>
            风格提示
            <select
              value={form.style_hint}
              onChange={(e) => setForm({ ...form, style_hint: e.target.value })}
            >
              <option value="soft">soft</option>
              <option value="warm">warm</option>
              <option value="cool">cool</option>
              <option value="noir">noir</option>
              <option value="vivid">vivid</option>
            </select>
          </label>
          <label>
            精选
            <select
              value={form.is_featured ? "1" : "0"}
              onChange={(e) => setForm({ ...form, is_featured: e.target.value === "1" })}
            >
              <option value="0">否</option>
              <option value="1">是</option>
            </select>
          </label>
          <label>
            发布
            <select
              value={form.is_published ? "1" : "0"}
              onChange={(e) => setForm({ ...form, is_published: e.target.value === "1" })}
            >
              <option value="1">是</option>
              <option value="0">草稿</option>
            </select>
          </label>
          <div className="full" style={{ display: "flex", gap: "0.6rem" }}>
            <button className="solid-btn" type="submit" disabled={busy}>
              {busy ? "保存中…" : editId ? "保存修改" : "发布"}
            </button>
            {editId && (
              <button
                type="button"
                className="ghost-btn"
                onClick={() => {
                  setEditId(null);
                  setForm({ ...emptyForm });
                }}
              >
                取消
              </button>
            )}
          </div>
          {error && <p className="error-text full">{error}</p>}
        </form>
      </div>

      <div className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>预览</th>
              <th>标题</th>
              <th>分类</th>
              <th>状态</th>
              <th>数据</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {items.map((w) => (
              <tr key={w.id}>
                <td>
                  <img className="thumb" src={w.thumb_url || w.image_url} alt="" />
                </td>
                <td>{w.title}</td>
                <td>{w.category_name || "-"}</td>
                <td>
                  {w.is_published ? "已发布" : "草稿"}
                  {w.is_featured ? " · 精选" : ""}
                </td>
                <td>
                  {w.views}/{w.likes}/{w.downloads}
                </td>
                <td>
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={() => {
                      setEditId(w.id);
                      setFile(null);
                      setForm({
                        title: w.title,
                        slug: w.slug,
                        description: w.description,
                        image_url: w.image_url,
                        thumb_url: w.thumb_url,
                        tags: w.tags,
                        palette: w.palette,
                        style_hint: w.style_hint,
                        category_id: w.category_id ?? "",
                        is_featured: w.is_featured,
                        is_published: w.is_published,
                        width: w.width,
                        height: w.height,
                      });
                    }}
                  >
                    编辑
                  </button>{" "}
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={async () => {
                      if (!confirm(`删除「${w.title}」？`)) return;
                      await api.deleteWallpaper(w.id);
                      await load();
                    }}
                  >
                    删除
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
