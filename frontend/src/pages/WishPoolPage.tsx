/** AI 壁纸许愿池：文生图 / 图生图 */
import { useEffect, useState, type FormEvent } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { Wish } from "../api/types";
import SiteHeader from "../components/SiteHeader";

const STATUS_LABEL: Record<string, string> = {
  pending: "排队中",
  generating: "生成中",
  done: "已兑现",
  failed: "失败",
};

/** 许愿池主页面 */
export default function WishPoolPage() {
  const [prompt, setPrompt] = useState("");
  const [author, setAuthor] = useState("");
  const [mode, setMode] = useState<"txt2img" | "img2img">("txt2img");
  const [sourceUrl, setSourceUrl] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [ratio, setRatio] = useState("1080x1920");
  const [items, setItems] = useState<Wish[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [note, setNote] = useState("");
  const [provider, setProvider] = useState("");

  /** 刷新许愿列表 */
  async function load() {
    const res = await api.wishes({ page_size: 36 });
    setItems(res.items);
    setTotal(res.total);
  }

  useEffect(() => {
    setLoading(true);
    Promise.all([load(), api.wishProvider()])
      .then(([, meta]) => {
        setProvider(
          `${meta.provider} · 文生图 ${meta.txt2img_model} / 图生图 ${meta.img2img_model}`,
        );
        setNote(meta.note);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "加载失败"))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const busy = items.some((w) => w.status === "pending" || w.status === "generating");
    if (!busy) return;
    const timer = window.setInterval(() => {
      load().catch(() => undefined);
    }, 4000);
    return () => window.clearInterval(timer);
  }, [items]);

  /** 提交文生图或图生图许愿 */
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const [width, height] = ratio.split("x").map(Number);
      if (mode === "img2img" && (file || sourceUrl)) {
        const fd = new FormData();
        fd.append("prompt", prompt);
        fd.append("author_name", author || "匿名");
        fd.append("mode", "img2img");
        fd.append("width", String(width));
        fd.append("height", String(height));
        if (file) fd.append("file", file);
        if (sourceUrl) fd.append("source_image_url", sourceUrl);
        await api.createWishUpload(fd);
      } else if (mode === "img2img") {
        throw new Error("图生图请上传参考图或填写参考图 URL");
      } else {
        await api.createWish({
          prompt,
          author_name: author || "匿名",
          mode: "txt2img",
          width,
          height,
        });
      }
      setPrompt("");
      setFile(null);
      setSourceUrl("");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交失败");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="app-shell">
      <SiteHeader />
      <section className="section wish-section">
        <div className="section-head">
          <div>
            <h2>AI 壁纸许愿池</h2>
            <p>文生图 / 图生图 · 后端异步生成 · 共 {total} 条</p>
          </div>
          <Link className="ghost-btn" to="/gallery?category=ai-wish">
            查看 AI 分类
          </Link>
        </div>

        <div className="wish-layout">
          <form className="wish-form panel" onSubmit={onSubmit}>
            <h3>许下愿望</h3>
            <div className="chip-row" style={{ marginBottom: "0.85rem" }}>
              <button
                type="button"
                className={`chip ${mode === "txt2img" ? "active" : ""}`}
                onClick={() => setMode("txt2img")}
              >
                文生图
              </button>
              <button
                type="button"
                className={`chip ${mode === "img2img" ? "active" : ""}`}
                onClick={() => setMode("img2img")}
              >
                图生图
              </button>
            </div>
            <label>
              Prompt
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder={
                  mode === "txt2img"
                    ? "例如：薄雾雪山湖面，电影感光线，手机竖屏壁纸"
                    : "例如：把这张图改成赛博朋克夜景，保留构图"
                }
                required
                minLength={2}
              />
            </label>
            {mode === "img2img" && (
              <>
                <label>
                  上传参考图
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => setFile(e.target.files?.[0] || null)}
                  />
                </label>
                <label>
                  或参考图 URL
                  <input
                    value={sourceUrl}
                    onChange={(e) => setSourceUrl(e.target.value)}
                    placeholder="https://..."
                  />
                </label>
              </>
            )}
            <div className="wish-form-row">
              <label>
                署名
                <input
                  value={author}
                  onChange={(e) => setAuthor(e.target.value)}
                  placeholder="匿名"
                />
              </label>
              <label>
                尺寸
                <select value={ratio} onChange={(e) => setRatio(e.target.value)}>
                  <option value="1080x1920">竖屏 1080×1920</option>
                  <option value="1920x1080">横屏 1920×1080</option>
                  <option value="1440x2560">竖屏 1440×2560</option>
                  <option value="1024x1024">方图 1024×1024</option>
                </select>
              </label>
            </div>
            {error && <p className="error-text">{error}</p>}
            <button className="solid-btn" type="submit" disabled={submitting}>
              {submitting ? "许愿中…" : mode === "img2img" ? "图生图许愿" : "文生图许愿"}
            </button>
            <p className="wish-note">
              引擎：{provider || "加载中…"}
              <br />
              <strong style={{ color: "var(--amber)" }}>无法关联 Cursor 生图。</strong> {note}
            </p>
          </form>

          <div className="wish-feed">
            {loading ? (
              <div className="loading">正在唤醒许愿池…</div>
            ) : items.length === 0 ? (
              <div className="empty">还没有愿望，来写下第一条吧。</div>
            ) : (
              <div className="wish-grid">
                {items.map((w) => (
                  <article className="wish-card" key={w.id}>
                    <div className="wish-status">
                      {(w.mode === "img2img" ? "图生图 · " : "文生图 · ") +
                        (STATUS_LABEL[w.status] || w.status)}
                    </div>
                    {w.image_url ? (
                      <img src={w.image_url} alt={w.prompt} loading="lazy" />
                    ) : (
                      <div className="wish-placeholder">
                        {w.status === "failed" ? "生成失败" : "画面酝酿中…"}
                      </div>
                    )}
                    <div className="wish-body">
                      <p className="wish-prompt">{w.prompt}</p>
                      <p className="wish-meta">
                        {w.author_name} · {w.width}×{w.height}
                        {w.wallpaper_id ? ` · 壁纸 #${w.wallpaper_id}` : ""}
                      </p>
                      {w.source_image_url && (
                        <p className="wish-meta">参考图已附带</p>
                      )}
                      {w.error_message && <p className="error-text">{w.error_message}</p>}
                      {(w.status === "failed" || w.status === "pending") && (
                        <button
                          type="button"
                          className="ghost-btn"
                          onClick={() => api.retryWish(w.id).then(load)}
                        >
                          重新生成
                        </button>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
