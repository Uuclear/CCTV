import { useEffect, useState } from "react";
import { fetchProjects, type Project } from "./api";
import { formatFetchError } from "./apiErrors";
import { ProjectCreateForm } from "./ProjectCreateForm";
import { ProjectWorkbench } from "./ProjectWorkbench";

export default function App() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [workbenchId, setWorkbenchId] = useState<number | null>(null);

  async function load() {
    setErr(null);
    setLoading(true);
    try {
      setProjects(await fetchProjects());
    } catch (e) {
      setErr(formatFetchError(e));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  if (workbenchId != null) {
    return (
      <ProjectWorkbench
        projectId={workbenchId}
        onBack={() => {
          setWorkbenchId(null);
          void load();
        }}
      />
    );
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar-inner">
          <h1 className="title">CCTV 检测报告工作台</h1>
          <span className="pill">DB31/T 444-2022 · 规则工程版</span>
        </div>
      </header>
      <main className="main">
        <ProjectCreateForm
          onCreated={(id) => {
            setWorkbenchId(id);
            void load();
          }}
        />
        {err ? (
          <div className="error-block">
            <pre className="error-pre">{err}</pre>
            <button type="button" className="btn secondary" onClick={() => void load()}>
              重试连接后端
            </button>
          </div>
        ) : null}
        <section className="card">
          <h2 className="card-title">项目列表</h2>
          {loading ? (
            <p className="muted">正在连接后端…</p>
          ) : projects.length === 0 ? (
            <p className="muted">暂无项目。请先创建工程，或确认已用 run-dev.ps1 启动前后端。</p>
          ) : (
            <ul className="list">
              {projects.map((p) => (
                <li key={p.id} className="list-item list-item-row">
                  <div>
                    <div className="list-main">{p.name}</div>
                    <div className="list-meta">
                      #{p.id}
                      {p.project_code ? ` · ${p.project_code}` : ""}
                    </div>
                  </div>
                  <button
                    type="button"
                    className="btn secondary"
                    data-testid={`open-project-${p.id}`}
                    onClick={() => setWorkbenchId(p.id)}
                  >
                    进入工作台
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  );
}
