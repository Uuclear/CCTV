/** 分类 CRUD 管理页 */
import { useEffect, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { Category } from "../api/types";

const empty = {
  name: "",
  slug: "",
  description: "",
  cover_url: "",
  sort_order: 0,
  is_active: true,
};

/** 创建、编辑与删除分类 */
export default function AdminCategories() {
  const [rows, setRows] = useState<Category[]>([]);
  const [form, setForm] = useState({ ...empty });
  const [editId, setEditId] = useState<number | null>(null);
  const [error, setError] = useState("");

  /** 刷新分类列表（含未启用） */
  async function load() {
    setRows(await api.categories(false));
  }

  useEffect(() => {
    load();
  }, []);

  /** 提交新建或更新 */
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    try {
      if (editId) await api.updateCategory(editId, form);
      else await api.createCategory(form);
      setForm({ ...empty });
      setEditId(null);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "保存失败");
    }
  }

  return (
    <div>
      <h2 style={{ fontFamily: "var(--font-display)", marginTop: 0 }}>分类管理</h2>
      <div className="panel">
        <h2>{editId ? "编辑分类" : "新建分类"}</h2>
        <form className="form-grid" onSubmit={onSubmit}>
          <label>
            名称
            <input
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              required
            />
          </label>
          <label>
            Slug
            <input
              value={form.slug}
              onChange={(e) => setForm({ ...form, slug: e.target.value })}
              required
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
            封面 URL
            <input
              value={form.cover_url}
              onChange={(e) => setForm({ ...form, cover_url: e.target.value })}
            />
          </label>
          <label>
            排序
            <input
              type="number"
              value={form.sort_order}
              onChange={(e) => setForm({ ...form, sort_order: Number(e.target.value) })}
            />
          </label>
          <label>
            启用
            <select
              value={form.is_active ? "1" : "0"}
              onChange={(e) => setForm({ ...form, is_active: e.target.value === "1" })}
            >
              <option value="1">是</option>
              <option value="0">否</option>
            </select>
          </label>
          <div className="full" style={{ display: "flex", gap: "0.6rem" }}>
            <button className="solid-btn" type="submit">
              {editId ? "保存修改" : "创建分类"}
            </button>
            {editId && (
              <button
                className="ghost-btn"
                type="button"
                onClick={() => {
                  setEditId(null);
                  setForm({ ...empty });
                }}
              >
                取消编辑
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
              <th>名称</th>
              <th>Slug</th>
              <th>数量</th>
              <th>排序</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.slug}</td>
                <td>{c.wallpaper_count}</td>
                <td>{c.sort_order}</td>
                <td>{c.is_active ? "启用" : "停用"}</td>
                <td>
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={() => {
                      setEditId(c.id);
                      setForm({
                        name: c.name,
                        slug: c.slug,
                        description: c.description,
                        cover_url: c.cover_url,
                        sort_order: c.sort_order,
                        is_active: c.is_active,
                      });
                    }}
                  >
                    编辑
                  </button>{" "}
                  <button
                    type="button"
                    className="ghost-btn"
                    onClick={async () => {
                      if (!confirm(`删除分类「${c.name}」？`)) return;
                      await api.deleteCategory(c.id);
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
