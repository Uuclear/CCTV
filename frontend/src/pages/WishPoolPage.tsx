/** AI 壁纸许愿池：提交 Prompt 并由后端异步生成 */
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
  const [ratio, setRatio] = useState("1920x1080");
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
        setProvider(`${meta.provider} / ${meta.model}`);
        setNote(meta.note);
      })
      .catch((e) => setError(e instanceof Error ? e.message : "加载失败"))
      .finally(() => setLoading(false));
  }, []);

  // 对进行中的许愿轮询状态
  useEffect(() => {
    const busy = items.some((w) => w.status === "pending" || w.status === "generating");
    if (!busy) return;
    const timer = window.setInterval(() => {
      load().catch(() => undefined);
    }, 4000);
    return () => window.clearInterval(timer);
  }, [items]);

  /** 提交新许愿 */
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      const [width, height] = ratio.split("x").map(Number);
      await api.createWish({
        prompt,
        author_name: author || "匿名",
        width,
        height,
      });
      setPrompt("");
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
            <p>写下画面愿望，后端异步生成并自动进入「AI许愿」分类 · 共 {total} 条</p>
          </div>
          <Link className="ghost-btn" to="/gallery?category=ai-wish">
            查看 AI 分类
          </Link>
        </div>

        <div className="wish-layout">
          <form className="wish-form panel" onSubmit={onSubmit}>
            <h3>许下愿望</h3>
            <label>
              Prompt
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="例如：薄雾中的雪山湖面，电影感光线，超宽桌面壁纸，细腻写实"
                required
                minLength={2}
              />
            </label>
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
                  <option value="1920x1080">横屏 1920×1080</option>
                  <option value="1080x1920">竖屏 1080×1920</option>
                  <option value="2560x1440">2K 2560×1440</option>
                  <option value="1440x2560">竖屏 1440×2560</option>
                </select>
              </label>
            </div>
            {error && <p className="error-text">{error}</p>}
            <button className="solid-btn" type="submit" disabled={submitting}>
              {submitting ? "许愿中…" : "投入许愿池"}
            </button>
            <p className="wish-note">
              生图引擎：{provider || "加载中…"}
              <br />
              {note}
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
                    <div className="wish-status">{STATUS_LABEL[w.status] || w.status}</div>
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
