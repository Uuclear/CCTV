/** 管理员登录页 */
import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api, setToken } from "../api/client";

/** 提交账号密码并跳转后台 */
export default function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await api.login(username, password);
      setToken(res.access_token);
      navigate("/admin");
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">
      <form className="login-card" onSubmit={onSubmit}>
        <h1>幕色管理</h1>
        <p>登录后可管理分类、上传与发布壁纸</p>
        <div className="form-grid" style={{ gridTemplateColumns: "1fr" }}>
          <label>
            用户名
            <input value={username} onChange={(e) => setUsername(e.target.value)} required />
          </label>
          <label>
            密码
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
        </div>
        {error && <p className="error-text">{error}</p>}
        <div style={{ display: "flex", gap: "0.6rem", marginTop: "1rem" }}>
          <button className="solid-btn" type="submit" disabled={loading}>
            {loading ? "登录中…" : "进入后台"}
          </button>
          <Link className="ghost-btn" to="/">
            返回前台
          </Link>
        </div>
      </form>
    </div>
  );
}
