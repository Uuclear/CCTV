import { useEffect, useState } from "react";
import {
  createDefect,
  createSegment,
  exportProjectDocx,
  extractPreview,
  fetchDefects,
  fetchProject,
  fetchSegments,
  ocrSegmentPreview,
  patchSegment,
  patchProject,
  uploadSegmentVideo,
  type Defect,
  type OcrPreviewOut,
  type Project,
  type Segment,
} from "./api";

function mediaUrl(relpath: string): string {
  return `/media/${relpath}`;
}

export function ProjectWorkbench({
  projectId,
  onBack,
}: {
  projectId: number;
  onBack: () => void;
}) {
  const [project, setProject] = useState<Project | null>(null);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [defects, setDefects] = useState<Defect[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [ocr, setOcr] = useState<OcrPreviewOut | null>(null);
  const [draftStart, setDraftStart] = useState("");
  const [draftEnd, setDraftEnd] = useState("");
  const [defectCode, setDefectCode] = useState("PL");
  const [defectLevel, setDefectLevel] = useState(2);
  const [defectKind, setDefectKind] = useState<"structural" | "functional">("structural");
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const [pjName, setPjName] = useState("");
  const [pjClient, setPjClient] = useState("");
  const [pjCode, setPjCode] = useState("");
  const [pjRoad, setPjRoad] = useState("");
  const [pjScope, setPjScope] = useState("");
  const [pjContact, setPjContact] = useState("");
  const [pjPhone, setPjPhone] = useState("");

  const selected = segments.find((s) => s.id === selectedId) ?? null;

  async function reloadAll() {
    setErr(null);
    const [p, segs] = await Promise.all([fetchProject(projectId), fetchSegments(projectId)]);
    setProject(p);
    setSegments(segs);
    if (selectedId != null && !segs.some((s) => s.id === selectedId)) {
      setSelectedId(null);
    }
  }

  useEffect(() => {
    void reloadAll().catch((e) => setErr(String(e)));
  }, [projectId]);

  useEffect(() => {
    if (!project) return;
    setPjName(project.name);
    setPjClient(project.client_org ?? "");
    setPjCode(project.project_code ?? "");
    setPjRoad(project.road_name ?? "");
    setPjScope(project.scope_text ?? "");
    setPjContact(project.contact_name ?? "");
    setPjPhone(project.contact_phone ?? "");
  }, [project]);

  useEffect(() => {
    if (selectedId == null) {
      setDefects([]);
      setOcr(null);
      setDraftStart("");
      setDraftEnd("");
      return;
    }
    setErr(null);
    fetchDefects(selectedId)
      .then(setDefects)
      .catch((e) => setErr(String(e)));
    const s = segments.find((x) => x.id === selectedId);
    if (s) {
      setDraftStart(s.chain_start_label ?? "");
      setDraftEnd(s.chain_end_label ?? "");
    }
  }, [selectedId, segments]);

  async function onSaveProject() {
    setBusy(true);
    setErr(null);
    try {
      await patchProject(projectId, {
        name: pjName.trim() || undefined,
        client_org: pjClient.trim() || null,
        project_code: pjCode.trim() || null,
        road_name: pjRoad.trim() || null,
        scope_text: pjScope.trim() || null,
        contact_name: pjContact.trim() || null,
        contact_phone: pjPhone.trim() || null,
      });
      await reloadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onAddSegment() {
    setBusy(true);
    setErr(null);
    try {
      const seg = await createSegment(projectId, { display_name: `管段-${segments.length + 1}` });
      await reloadAll();
      setSelectedId(seg.id);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onUploadVideo(file: File | null) {
    if (!file || selectedId == null) return;
    setBusy(true);
    setErr(null);
    try {
      await uploadSegmentVideo(selectedId, file);
      await reloadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onExtract() {
    if (selectedId == null) return;
    setBusy(true);
    setErr(null);
    try {
      await extractPreview(selectedId, 1);
      await reloadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onOcr() {
    if (selectedId == null) return;
    setBusy(true);
    setErr(null);
    try {
      const o = await ocrSegmentPreview(selectedId);
      setOcr(o);
      setDraftStart(o.suggested_chain_start ?? draftStart);
      setDraftEnd(o.suggested_chain_end ?? draftEnd);
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onSaveLabels() {
    if (selectedId == null) return;
    setBusy(true);
    setErr(null);
    try {
      await patchSegment(selectedId, {
        chain_start_label: draftStart || null,
        chain_end_label: draftEnd || null,
      });
      await reloadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onAddDefect() {
    if (selectedId == null) return;
    setBusy(true);
    setErr(null);
    try {
      await createDefect(selectedId, {
        defect_code: defectCode.trim() || "PL",
        level: defectLevel,
        kind: defectKind,
      });
      const d = await fetchDefects(selectedId);
      setDefects(d);
      await reloadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onExportDocx() {
    setBusy(true);
    setExportMsg(null);
    setErr(null);
    try {
      const { media_url } = await exportProjectDocx(projectId);
      setExportMsg(`已生成：${media_url}`);
      window.open(media_url, "_blank", "noopener,noreferrer");
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  if (!project) {
    return (
      <div className="shell">
        <p className="muted" style={{ padding: 24 }}>加载工程…</p>
      </div>
    );
  }

  return (
    <div className="shell">
      <header className="topbar">
        <div className="topbar-inner">
          <button type="button" className="btn ghost" data-testid="workbench-back" onClick={onBack}>
            ← 返回列表
          </button>
          <h1 className="title" style={{ flex: 1 }}>{pjName || project.name}</h1>
          <span className="pill">工作台</span>
        </div>
      </header>
      <main className="main main-wide">
        {err ? <p className="error">{err}</p> : null}
        {exportMsg ? <p className="muted small-note">{exportMsg}</p> : null}

        <section className="card">
          <h2 className="card-title">工程信息</h2>
          <div className="project-form">
            <label className="field">
              <span>工程名称</span>
              <input value={pjName} onChange={(e) => setPjName(e.target.value)} data-testid="pj-name" required />
            </label>
            <label className="field">
              <span>委托单位</span>
              <input value={pjClient} onChange={(e) => setPjClient(e.target.value)} data-testid="pj-client" />
            </label>
            <label className="field">
              <span>工程编号</span>
              <input value={pjCode} onChange={(e) => setPjCode(e.target.value)} data-testid="pj-code" />
            </label>
            <label className="field">
              <span>路名 / 位置</span>
              <input value={pjRoad} onChange={(e) => setPjRoad(e.target.value)} data-testid="pj-road" />
            </label>
            <label className="field full-width">
              <span>检测范围说明</span>
              <input value={pjScope} onChange={(e) => setPjScope(e.target.value)} data-testid="pj-scope" />
            </label>
            <label className="field">
              <span>联系人</span>
              <input value={pjContact} onChange={(e) => setPjContact(e.target.value)} data-testid="pj-contact" />
            </label>
            <label className="field">
              <span>联系电话</span>
              <input value={pjPhone} onChange={(e) => setPjPhone(e.target.value)} data-testid="pj-phone" />
            </label>
          </div>
          <div className="toolbar" style={{ marginTop: 14 }}>
            <button type="button" className="btn secondary" data-testid="save-project" disabled={busy || !pjName.trim()} onClick={() => void onSaveProject()}>
              保存工程信息
            </button>
            <button type="button" className="btn secondary" data-testid="export-docx" disabled={busy} onClick={() => void onExportDocx()}>
              导出 Word 报告
            </button>
          </div>
        </section>

        <section className="card">
          <div className="card-head">
            <h2 className="card-title" style={{ margin: 0 }}>管段</h2>
            <button type="button" className="btn primary" data-testid="add-segment" disabled={busy} onClick={() => void onAddSegment()}>
              新建管段
            </button>
          </div>
          {segments.length === 0 ? (
            <p className="muted">暂无管段，点击「新建管段」开始。</p>
          ) : (
            <div className="seg-grid">
              {segments.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  className={`seg-tile ${selectedId === s.id ? "active" : ""}`}
                  data-testid={`segment-${s.id}`}
                  onClick={() => setSelectedId(s.id)}
                >
                  <div className="seg-tile-title">{s.display_name || `管段 #${s.id}`}</div>
                  <div className="seg-tile-meta">
                    {s.chain_start_label || "?"}～{s.chain_end_label || "?"} · RI {s.ri ?? "—"} · MI {s.mi ?? "—"}
                  </div>
                </button>
              ))}
            </div>
          )}
        </section>

        {selected ? (
          <section className="card" data-testid="segment-detail">
            <h2 className="card-title">当前管段 · {selected.display_name || `#${selected.id}`}</h2>

            <div className="panel">
              <h3 className="subhead">1. 视频</h3>
              <div className="row">
                <label className="field">
                  <span>上传文件</span>
                  <input
                    type="file"
                    accept="video/*"
                    data-testid="video-file"
                    disabled={busy}
                    onChange={(e) => void onUploadVideo(e.target.files?.[0] ?? null)}
                  />
                </label>
                <span className="muted small-note">{selected.video_relpath ?? "尚未上传"}</span>
              </div>
              <div className="toolbar">
                <button type="button" className="btn secondary" data-testid="extract-preview" disabled={busy} onClick={() => void onExtract()}>
                  抽取预览帧
                </button>
              </div>
              {selected.preview_frame_relpath ? (
                <figure className="preview-wrap">
                  <img
                    className="preview-img"
                    alt="预览帧"
                    src={mediaUrl(selected.preview_frame_relpath)}
                  />
                </figure>
              ) : null}
            </div>

            <div className="panel">
              <h3 className="subhead">2. OCR 与井号</h3>
              <div className="toolbar">
                <button type="button" className="btn secondary" data-testid="run-ocr" disabled={busy || !selected.preview_frame_relpath} onClick={() => void onOcr()}>
                  对预览图 OCR
                </button>
              </div>
              {ocr ? (
                <pre className="ocr-preview" data-testid="ocr-raw">{ocr.raw_text || "（无文本）"}</pre>
              ) : null}
              <div className="row">
                <label className="field">
                  <span>起点井号</span>
                  <input value={draftStart} onChange={(e) => setDraftStart(e.target.value)} data-testid="chain-start" />
                </label>
                <label className="field">
                  <span>终点井号</span>
                  <input value={draftEnd} onChange={(e) => setDraftEnd(e.target.value)} data-testid="chain-end" />
                </label>
                <button type="button" className="btn primary" data-testid="save-labels" disabled={busy} onClick={() => void onSaveLabels()}>
                  保存井号
                </button>
              </div>
            </div>

            <div className="panel">
              <h3 className="subhead">3. 缺陷与指数</h3>
              <div className="row">
                <label className="field">
                  <span>代码</span>
                  <input value={defectCode} onChange={(e) => setDefectCode(e.target.value)} placeholder="PL" data-testid="defect-code" />
                </label>
                <label className="field slim">
                  <span>等级</span>
                  <select value={defectLevel} data-testid="defect-level" onChange={(e) => setDefectLevel(Number(e.target.value))}>
                    {[1, 2, 3, 4].map((n) => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                </label>
                <label className="field slim">
                  <span>类型</span>
                  <select value={defectKind} data-testid="defect-kind" onChange={(e) => setDefectKind(e.target.value as "structural" | "functional")}>
                    <option value="structural">结构性</option>
                    <option value="functional">功能性</option>
                  </select>
                </label>
                <button type="button" className="btn primary" data-testid="add-defect" disabled={busy} onClick={() => void onAddDefect()}>
                  添加缺陷
                </button>
              </div>
              <p className="muted small-note">
                当前 RI = {selected.ri ?? "—"}（{selected.ri_grade ?? "—"}）· MI = {selected.mi ?? "—"}（{selected.mi_grade ?? "—"}）
              </p>
              <ul className="defect-list" data-testid="defect-list">
                {defects.map((d) => (
                  <li key={d.id}>{d.defect_code} · {d.kind} · L{d.level}</li>
                ))}
              </ul>
            </div>
          </section>
        ) : (
          <section className="card muted">请选择一个管段以编辑视频、OCR 与缺陷。</section>
        )}
      </main>
    </div>
  );
}
