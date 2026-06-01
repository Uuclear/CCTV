import { useEffect, useState } from "react";
import {
  createSegment,
  deleteSegment,
  downloadStatisticsXlsx,
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
  type SegmentSummary,
} from "./api";
import { BatchImportPanel } from "./BatchImportPanel";
import { DefectVideoPanel } from "./DefectVideoPanel";
import { ImageLightbox } from "./ImageLightbox";
import { ProjectInfoForm } from "./ProjectInfoForm";
import { SegmentPipelineTable, type SegmentPatch } from "./SegmentPipelineTable";
import { formatConditionGrade } from "./segmentDisplay";
import {
  formToProjectPayload,
  projectToForm,
  warnCodeFormats,
  type ProjectFormValues,
} from "./projectConstants";

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
  const [segments, setSegments] = useState<SegmentSummary[]>([]);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [defects, setDefects] = useState<Defect[]>([]);
  const [err, setErr] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [ocr, setOcr] = useState<OcrPreviewOut | null>(null);
  const [draftStart, setDraftStart] = useState("");
  const [draftEnd, setDraftEnd] = useState("");
  const [draftDiameter, setDraftDiameter] = useState("");
  const [draftMaterial, setDraftMaterial] = useState("");
  const [draftDate, setDraftDate] = useState("");
  const [exportMsg, setExportMsg] = useState<string | null>(null);
  const [lightboxSrc, setLightboxSrc] = useState<string | null>(null);
  const [pjForm, setPjForm] = useState<ProjectFormValues | null>(null);

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
    setPjForm(projectToForm(project));
  }, [project]);

  useEffect(() => {
    if (selectedId == null) {
      setDefects([]);
      setOcr(null);
      setDraftStart("");
      setDraftEnd("");
      setDraftDiameter("");
      setDraftMaterial("");
      setDraftDate("");
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
      setDraftDiameter(s.diameter_mm != null ? String(s.diameter_mm) : "");
      setDraftMaterial(s.pipe_material ?? "");
      setDraftDate(s.inspection_date ?? "");
    }
  }, [selectedId, segments]);

  async function onSaveProject() {
    if (!pjForm || !pjForm.name.trim()) {
      setErr("工程名称不能为空");
      return;
    }
    warnCodeFormats(pjForm.project_code, pjForm.report_no);
    setBusy(true);
    setErr(null);
    try {
      await patchProject(projectId, formToProjectPayload(pjForm));
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
      if (o.suggested_diameter_mm != null) setDraftDiameter(String(o.suggested_diameter_mm));
      if (o.suggested_pipe_material) setDraftMaterial(o.suggested_pipe_material);
      if (o.suggested_inspection_date) setDraftDate(o.suggested_inspection_date);
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
        diameter_mm: draftDiameter ? Number(draftDiameter) : null,
        pipe_material: draftMaterial || null,
        inspection_date: draftDate || null,
      });
      await reloadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onPatchSegmentRow(id: number, patch: SegmentPatch) {
    setErr(null);
    try {
      await patchSegment(id, patch);
      await reloadAll();
    } catch (e) {
      setErr(String(e));
    }
  }

  async function onDeleteSegment(id: number) {
    setBusy(true);
    setErr(null);
    try {
      await deleteSegment(id);
      if (selectedId === id) setSelectedId(null);
      await reloadAll();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  async function onExportStatistics() {
    setBusy(true);
    setErr(null);
    try {
      await downloadStatisticsXlsx(projectId, `${pjForm?.name || project?.name || "工程"}_管段统计表.xlsx`);
      setExportMsg("已导出管段统计表（.xlsx）。");
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
          <h1 className="title" style={{ flex: 1 }}>{pjForm?.name || project.name}</h1>
          <span className="pill">工作台</span>
        </div>
      </header>
      <main className="main main-wide">
        {err ? <p className="error">{err}</p> : null}
        {exportMsg ? <p className="muted small-note">{exportMsg}</p> : null}

        <section className="card">
          <h2 className="card-title">工程与委托信息</h2>
          {pjForm ? (
            <ProjectInfoForm
              form={pjForm}
              onChange={(patch) => setPjForm((f) => (f ? { ...f, ...patch } : f))}
            />
          ) : null}
          <div className="toolbar" style={{ marginTop: 14 }}>
            <button type="button" className="btn secondary" data-testid="save-project" disabled={busy || !pjForm?.name.trim()} onClick={() => void onSaveProject()}>
              保存工程信息
            </button>
            <button type="button" className="btn secondary" data-testid="export-docx" disabled={busy} onClick={() => void onExportDocx()}>
              导出 Word 报告
            </button>
          </div>
        </section>

        <BatchImportPanel projectId={projectId} onCommitted={() => void reloadAll()} />

        <section className="card">
          <div className="card-head">
            <h2 className="card-title" style={{ margin: 0 }}>管段</h2>
            <div className="toolbar">
              <button
                type="button"
                className="btn secondary"
                data-testid="export-statistics"
                disabled={busy || segments.length === 0}
                onClick={() => void onExportStatistics()}
              >
                导出统计表
              </button>
              <button type="button" className="btn primary" data-testid="add-segment" disabled={busy} onClick={() => void onAddSegment()}>
                新建管段
              </button>
            </div>
          </div>
          <SegmentPipelineTable
            segments={segments}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onPatch={(id, patch) => void onPatchSegmentRow(id, patch)}
          />
        </section>

        {selected ? (
          <section className="card" data-testid="segment-detail">
            <div className="card-head">
              <h2 className="card-title" style={{ margin: 0 }}>
                当前管段 · {selected.display_name || `#${selected.id}`}
              </h2>
              <button
                type="button"
                className="btn btn-danger"
                data-testid="delete-segment"
                disabled={busy}
                onClick={() => {
                  const label = `${selected.chain_start_label ?? "?"}～${selected.chain_end_label ?? "?"}`;
                  if (window.confirm(`确定删除管段 ${label}？`)) void onDeleteSegment(selected.id);
                }}
              >
                删除管段
              </button>
            </div>

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
                  抽取预览帧（随机时刻，写入本管段供报告使用）
                </button>
              </div>
              {selected.preview_frame_relpath ? (
                <figure className="preview-wrap">
                  <button
                    type="button"
                    className="thumb-btn"
                    onClick={() => setLightboxSrc(mediaUrl(selected.preview_frame_relpath!))}
                  >
                    <img
                      className="preview-img"
                      alt="预览帧"
                      src={mediaUrl(selected.preview_frame_relpath)}
                    />
                  </button>
                </figure>
              ) : null}
            </div>

            <div className="panel">
              <h3 className="subhead">2. 水印 OCR（起止井号 / 管径 / 管材 / 日期）</h3>
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
                <label className="field slim">
                  <span>管径 mm</span>
                  <input value={draftDiameter} onChange={(e) => setDraftDiameter(e.target.value)} />
                </label>
                <label className="field">
                  <span>管材</span>
                  <input value={draftMaterial} onChange={(e) => setDraftMaterial(e.target.value)} />
                </label>
                <label className="field">
                  <span>检测日期</span>
                  <input value={draftDate} onChange={(e) => setDraftDate(e.target.value)} placeholder="YYYY-MM-DD" />
                </label>
                <button type="button" className="btn primary" data-testid="save-labels" disabled={busy} onClick={() => void onSaveLabels()}>
                  保存看板字段
                </button>
              </div>
            </div>

            <div className="panel">
              <h3 className="subhead">3. 缺陷与指数（视频暂停标注）</h3>
              <DefectVideoPanel
                segmentId={selected.id}
                videoUrl={selected.video_relpath ? mediaUrl(selected.video_relpath) : null}
                onDefectAdded={() => {
                  void fetchDefects(selected.id).then(setDefects);
                  void reloadAll();
                }}
              />
              <p className="muted small-note">
                当前 RI = {selected.ri ?? "—"}（{formatConditionGrade(selected.ri_grade, selected.ri)}）· MI ={" "}
                {selected.mi ?? "—"}（{formatConditionGrade(selected.mi_grade, selected.mi)}）
              </p>
              <ul className="defect-list" data-testid="defect-list">
                {defects.length === 0 ? <li className="muted">无缺陷</li> : null}
                {defects.map((d) => (
                  <li key={d.id}>
                    {d.defect_code} · {d.kind} · L{d.level}
                    {d.note ? ` · ${d.note}` : ""}
                  </li>
                ))}
              </ul>
            </div>
          </section>
        ) : (
          <section className="card muted">请选择一个管段以编辑视频、OCR 与缺陷。</section>
        )}
        {lightboxSrc ? <ImageLightbox src={lightboxSrc} onClose={() => setLightboxSrc(null)} /> : null}
      </main>
    </div>
  );
}
