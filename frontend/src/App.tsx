import { useEffect, useState } from "react";
import { createProject, fetchProjects, type Project } from "./api";

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [name, setName] = useState("新检测工程");
  const [busy, setBusy] = useState(false);

  async function load() {
    setErr(null);
    try {
      setProjects(await fetchProjects());
    } catch (e) {
      setErr(String(e));
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function onCreate(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErr(null);
    try {
      await createProject({ name, client_org: null, project_code: null });
      setName("新检测工程");
      await load();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar-inner">
          <h1 className="title">CCTV 检测报告工作台</h1>
          <span className="pill">DB31/T 444-2022 · 规则占位</span>
        </div>
      </header>
      <main className="main">
        <section className="card">
          <h2 className="card-title">新建项目</h2>
          <form className="row" onSubmit={onCreate}>
            <label className="field">
              <span>工程名称</span>
              <input
                data-testid="project-name-input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                minLength={1}
              />
            </label>
            <button
              data-testid="create-project-submit"
              className="btn primary" type="submit" disabled={busy}>
              {busy ? "保存中…" : "创建"}
            </button>
          </form>
          {err ? <p className="error">{err}</p> : null}
        </section>
        <section className="card">
          <h2 className="card-title">项目列表</h2>
          {projects.length === 0 ? (
            <p className="muted">暂无项目。请先创建或启动后端。</p>
          ) : (
            <ul className="list">
              {projects.map((p) => (
                <li key={p.id} className="list-item">
                  <div className="list-main">{p.name}</div>
                  <div className="list-meta">
                    #{p.id}
                    {p.project_code ? ` · ${p.project_code}` : ""}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}
