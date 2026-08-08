/** 后台布局：侧栏导航与鉴权守卫 */
import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { api, getToken, setToken } from "../api/client";

/** 校验登录态并渲染管理壳层 */
export default function AdminLayout() {
  const navigate = useNavigate();
  const [ready, setReady] = useState(false);
  const [username, setUsername] = useState("");

  useEffect(() => {
    if (!getToken()) {
      navigate("/admin/login");
      return;
    }
    api
      .me()
      .then((u) => {
        setUsername(u.username);
        setReady(true);
      })
      .catch(() => {
        setToken(null);
        navigate("/admin/login");
      });
  }, [navigate]);

  if (!ready) return <div className="loading">校验登录状态…</div>;

  return (
    <div className="admin-layout app-shell">
      <aside className="admin-side">
        <h1>幕色后台</h1>
        <p style={{ color: "var(--muted)", marginTop: "-0.6rem" }}>@{username}</p>
        <nav>
          <NavLink to="/admin" end>
            概览
          </NavLink>
          <NavLink to="/admin/categories">分类管理</NavLink>
          <NavLink to="/admin/wallpapers">壁纸管理</NavLink>
          <Link to="/">返回前台</Link>
          <button
            type="button"
            className="ghost-btn"
            style={{ marginTop: "0.5rem", textAlign: "left" }}
            onClick={() => {
              setToken(null);
              navigate("/admin/login");
            }}
          >
            退出登录
          </button>
        </nav>
      </aside>
      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
}
