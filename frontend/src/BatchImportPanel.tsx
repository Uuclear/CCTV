import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

import {
  checkImportDuplicates,
  commitImports,
  fetchOcrStatus,
  ocrImportOne,
  scanImportFolderStage,
  uploadStageOneVideo,
  type ImportDraft,
  type ImportDuplicateHit,
  type OcrStatus,
} from "./api";
import { formatFetchError } from "./apiErrors";
import { ImageLightbox } from "./ImageLightbox";

function mediaUrl(relpath: string): string {
  return `/media/${relpath}`;
}

type OcrRowState = "pending" | "running" | "done" | "error";

type Props = {
  projectId: number;
  onCommitted: () => void;
};

type DraftRow = {
  draft_id: string;
  source_path: string;
  original_filename: string;
  preview_frame_relpath: string | null;
  chain_start_label: string;
  chain_end_label: string;
  diameter_mm: string;
  pipe_material: string;
  pipe_system: string;
  inspection_date: string;
  ocrState: OcrRowState;
  ocrError: string | null;
  sample_frame_relpaths: string[];
  preview_sample_time_sec: number | null;
};

function emptyRow(d: ImportDraft): DraftRow {
  return {
    draft_id: d.draft_id,
    source_path: d.source_path,
    original_filename: d.original_filename,
    preview_frame_relpath: d.preview_frame_relpath,
    chain_start_label: "",
    chain_end_label: "",
    diameter_mm: "",
    pipe_material: "",
    pipe_system: "雨水",
    inspection_date: "",
    ocrState: "pending",
    ocrError: null,
    sample_frame_relpaths: [],
    preview_sample_time_sec: null,
  };
}

function applyOcrToRow(row: DraftRow, d: ImportDraft): DraftRow {
  const scan = d.parse.scan;
  const notes: string[] = [];
  if (scan?.ffmpeg_error) notes.push(`ffmpeg: ${scan.ffmpeg_error}`);
  if (scan?.ocr_error) notes.push(`OCR: ${scan.ocr_error}`);
  if (d.parse.chain_warnings?.length) notes.push(d.parse.chain_warnings.join(", "));
  return {
    ...row,
    chain_start_label: d.parse.chain_start_label ?? "",
    chain_end_label: d.parse.chain_end_label ?? "",
    diameter_mm: d.parse.diameter_mm != null ? String(d.parse.diameter_mm) : "",
    pipe_material: d.parse.pipe_material ?? "",
    pipe_system: d.parse.pipe_system ?? row.pipe_system,
    inspection_date: d.parse.inspection_date ?? "",
    preview_frame_relpath: d.preview_frame_relpath,
    preview_sample_time_sec: scan?.sample_times_sec?.[0] ?? null,
    sample_frame_relpaths: scan?.sample_frame_relpaths?.length
      ? scan.sample_frame_relpaths
      : d.preview_frame_relpath
        ? [d.preview_frame_relpath]
        : [],
    ocrState: notes.some((n) => n.includes("失败") || n.includes("error")) ? "error" : "done",
    ocrError: notes.length ? notes.join(" · ") : null,
  };
}

export function BatchImportPanel({ projectId, onCommitted }: Props) {
  const [folder, setFolder] = useState("视频");
  const [rows, setRows] = useState<DraftRow[]>([]);
  const [busy, setBusy] = useState(false);
  const [ocrRunning, setOcrRunning] = useState(false);
  const [ocrPaused, setOcrPaused] = useState(false);
  const [progress, setProgress] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [msg, setMsg] = useState<string | null>(null);
  const [ocrStatus, setOcrStatus] = useState<OcrStatus | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [lightboxSrc, setLightboxSrc] = useState<string | null>(null);
  const [dupDialog, setDupDialog] = useState<{
    hits: ImportDuplicateHit[];
    policy: "skip" | "overwrite";
  } | null>(null);

  const fileRef = useRef<HTMLInputElement>(null);
  const rowsRef = useRef(rows);
  const ocrAbortRef = useRef(false);
  const ocrPausedRef = useRef(false);

  useEffect(() => {
    rowsRef.current = rows;
  }, [rows]);

  useEffect(() => {
    fetchOcrStatus()
      .then((st) => {
        setOcrStatus(st);
        setBackendOk(true);
      })
      .catch(() => {
        setOcrStatus(null);
        setBackendOk(false);
      });
  }, []);

  const addStageDrafts = useCallback((drafts: ImportDraft[]) => {
    setRows((prev) => [...prev, ...drafts.map(emptyRow)]);
  }, []);

  async function stageFiles(files: FileList | File[]) {
    const mp4 = Array.from(files).filter((f) => f.name.toLowerCase().endsWith(".mp4"));
    if (mp4.length === 0) {
      setErr("请选择 .mp4 视频文件");
      return;
    }
    setBusy(true);
    setErr(null);
    setMsg(null);
    try {
      for (let i = 0; i < mp4.length; i++) {
        setProgress(`上传视频 ${i + 1}/${mp4.length}：${mp4[i].name}`);
        const draft = await uploadStageOneVideo(projectId, mp4[i]);
        addStageDrafts([draft]);
      }
      setMsg(`已添加 ${mp4.length} 个视频到列表，请点击「批量 OCR」识别水印。`);
    } catch (e) {
      setErr(formatFetchError(e));
    } finally {
      setBusy(false);
      setProgress(null);
    }
  }

  async function onScanFolder() {
    setBusy(true);
    setErr(null);
    try {
      const drafts = await scanImportFolderStage(projectId, folder.trim());
      setRows(drafts.map(emptyRow));
      setMsg(`已添加 ${drafts.length} 个视频，请点击「批量 OCR」。`);
    } catch (e) {
      setErr(formatFetchError(e));
    } finally {
      setBusy(false);
    }
  }

  async function runBatchOcr(startIndex = 0) {
    if (rowsRef.current.length === 0) return;
    ocrAbortRef.current = false;
    ocrPausedRef.current = false;
    setOcrPaused(false);
    setOcrRunning(true);
    setErr(null);
    try {
      for (let i = startIndex; i < rowsRef.current.length; i++) {
        while (ocrPausedRef.current && !ocrAbortRef.current) {
          await new Promise((r) => setTimeout(r, 200));
        }
        if (ocrAbortRef.current) {
          setMsg("OCR 已终止。");
          break;
        }
        const row = rowsRef.current[i];
        if (row.ocrState === "done") continue;

        setProgress(`OCR ${i + 1}/${rowsRef.current.length}：${row.original_filename}`);
        setRows((prev) =>
          prev.map((r, j) => (j === i ? { ...r, ocrState: "running", ocrError: null } : r)),
        );

        try {
          const draft = await ocrImportOne(projectId, row.source_path);
          setRows((prev) =>
            prev.map((r, j) => (j === i ? applyOcrToRow(r, draft) : r)),
          );
        } catch (e) {
          setRows((prev) =>
            prev.map((r, j) =>
              j === i ? { ...r, ocrState: "error", ocrError: formatFetchError(e) } : r,
            ),
          );
        }
      }
      if (!ocrAbortRef.current) setMsg("批量 OCR 完成，请核对后入库。");
    } finally {
      setOcrRunning(false);
      setProgress(null);
    }
  }

  function pauseOcr() {
    ocrPausedRef.current = true;
    setOcrPaused(true);
  }

  function resumeOcr() {
    ocrPausedRef.current = false;
    setOcrPaused(false);
    if (!ocrRunning) {
      const idx = rowsRef.current.findIndex((r) => r.ocrState === "pending" || r.ocrState === "error");
      if (idx >= 0) void runBatchOcr(idx);
    }
  }

  function stopOcr() {
    ocrAbortRef.current = true;
    ocrPausedRef.current = false;
    setOcrPaused(false);
    setOcrRunning(false);
    setProgress(null);
  }

  async function doCommit(policy: "skip" | "overwrite") {
    setBusy(true);
    setErr(null);
    setDupDialog(null);
    try {
      await commitImports(
        projectId,
        rows.map((r) => ({
          source_path: r.source_path,
          chain_start_label: r.chain_start_label.trim() || null,
          chain_end_label: r.chain_end_label.trim() || null,
          pipe_system: r.pipe_system.trim() || "雨水",
          diameter_mm: r.diameter_mm ? Number(r.diameter_mm) : null,
          pipe_material: r.pipe_material.trim() || null,
          inspection_date: r.inspection_date.trim() || null,
          display_name: `${r.chain_start_label || "?"}～${r.chain_end_label || "?"}`,
          preview_frame_relpath: r.preview_frame_relpath,
          preview_sample_time_sec: r.preview_sample_time_sec,
          duplicate_policy: policy,
        })),
      );
      setRows([]);
      setMsg("已入库，管段列表已更新；原视频已按起止井号重命名（如有权限）。");
      onCommitted();
    } catch (e) {
      setErr(formatFetchError(e));
    } finally {
      setBusy(false);
    }
  }

  async function onCommit() {
    setErr(null);
    try {
      const hits = await checkImportDuplicates(
        projectId,
        rows.map((r) => ({
          source_path: r.source_path,
          chain_start_label: r.chain_start_label.trim() || null,
          chain_end_label: r.chain_end_label.trim() || null,
        })),
      );
      if (hits.length > 0) {
        setDupDialog({ hits, policy: "skip" });
        return;
      }
      await doCommit("skip");
    } catch (e) {
      setErr(formatFetchError(e));
    }
  }

  function updateRow(i: number, patch: Partial<DraftRow>) {
    setRows((prev) => prev.map((r, j) => (j === i ? { ...r, ...patch } : r)));
  }

  function framePaths(r: DraftRow): string[] {
    if (r.sample_frame_relpaths.length) return r.sample_frame_relpaths;
    return r.preview_frame_relpath ? [r.preview_frame_relpath] : [];
  }

  const ocrBadge = ocrStatus
    ? ocrStatus.available
      ? `OCR: ${ocrStatus.engine} ✓`
      : `OCR 不可用: ${ocrStatus.error ?? "未知"}`
    : "OCR 状态检测中…";

  return (
    <section className="card">
      <h2 className="card-title">批量导入视频（水印 OCR）</h2>

      {backendOk === false ? (
        <p className="error">
          后端未就绪。请运行 <code>desktop\run-dev.ps1</code> 后刷新。
        </p>
      ) : null}

      <p className="muted small-note">
        <span className={ocrStatus?.available ? "ok" : "field-warn"}>{ocrBadge}</span>
        {" · "}先添加视频生成列表，再批量 OCR；可暂停 / 继续 / 终止。
      </p>

      <div
        className={`drop-zone ${dragOver ? "drop-zone-active" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          if (e.dataTransfer.files.length) void stageFiles(e.dataTransfer.files);
        }}
      >
        <p>将 mp4 拖放到此处（仅上传，不立即 OCR）</p>
        <input
          ref={fileRef}
          type="file"
          accept="video/mp4,.mp4"
          multiple
          hidden
          disabled={busy || ocrRunning}
          onChange={(e) => {
            if (e.target.files?.length) void stageFiles(e.target.files);
            e.target.value = "";
          }}
        />
        <button
          type="button"
          className="btn secondary"
          disabled={busy || ocrRunning}
          onClick={() => fileRef.current?.click()}
        >
          选择视频文件
        </button>
      </div>

      {progress ? <p className="muted">{progress}</p> : null}

      <details className="folder-scan">
        <summary>或扫描仓库内文件夹（仅建表，不 OCR）</summary>
        <div className="row" style={{ marginTop: 8 }}>
          <label className="field grow">
            <span>相对仓库路径</span>
            <input value={folder} onChange={(e) => setFolder(e.target.value)} disabled={busy} />
          </label>
          <button type="button" className="btn secondary" disabled={busy} onClick={() => void onScanFolder()}>
            扫描文件夹
          </button>
        </div>
      </details>

      {rows.length > 0 ? (
        <div className="table-wrap">
          <table className="data-table">
            <thead>
              <tr>
                <th>预览</th>
                <th>状态</th>
                <th>起点井</th>
                <th>终点井</th>
                <th>管径</th>
                <th>管材</th>
                <th>检测日期</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r, i) => (
                <tr key={r.draft_id}>
                  <td className="thumb-cell">
                    {framePaths(r).length ? (
                      <div className="thumb-row">
                        {framePaths(r).map((rel, fi) => (
                          <button
                            key={`${r.draft_id}-${fi}`}
                            type="button"
                            className="thumb-btn"
                            title="点击放大"
                            onClick={() => setLightboxSrc(mediaUrl(rel))}
                          >
                            <img className="thumb" src={mediaUrl(rel)} alt="" width={72} />
                          </button>
                        ))}
                      </div>
                    ) : (
                      "—"
                    )}
                  </td>
                  <td className="small-cell">
                    {r.ocrState === "pending" && "待 OCR"}
                    {r.ocrState === "running" && "识别中…"}
                    {r.ocrState === "done" && "已完成"}
                    {r.ocrState === "error" && (r.ocrError ?? "失败")}
                  </td>
                  <td>
                    <input
                      className="cell-input"
                      value={r.chain_start_label}
                      onChange={(e) => updateRow(i, { chain_start_label: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      className="cell-input"
                      value={r.chain_end_label}
                      onChange={(e) => updateRow(i, { chain_end_label: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      className="cell-input"
                      value={r.diameter_mm}
                      onChange={(e) => updateRow(i, { diameter_mm: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      className="cell-input"
                      value={r.pipe_material}
                      onChange={(e) => updateRow(i, { pipe_material: e.target.value })}
                    />
                  </td>
                  <td>
                    <input
                      className="cell-input"
                      value={r.inspection_date}
                      onChange={(e) => updateRow(i, { inspection_date: e.target.value })}
                    />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="toolbar" style={{ marginTop: 12, flexWrap: "wrap", gap: 8 }}>
            <button
              type="button"
              className="btn secondary"
              disabled={busy || ocrRunning}
              onClick={() => void runBatchOcr(0)}
            >
              批量 OCR
            </button>
            {ocrRunning ? (
              <>
                <button type="button" className="btn secondary" disabled={ocrPaused} onClick={pauseOcr}>
                  暂停
                </button>
                <button type="button" className="btn secondary" onClick={resumeOcr}>
                  继续
                </button>
                <button type="button" className="btn ghost" onClick={stopOcr}>
                  终止
                </button>
              </>
            ) : null}
            <button type="button" className="btn primary" disabled={busy || ocrRunning} onClick={() => void onCommit()}>
              确认入库 ({rows.length})
            </button>
            <button
              type="button"
              className="btn ghost"
              disabled={busy || ocrRunning}
              onClick={() => {
                setRows([]);
                setMsg(null);
              }}
            >
              清空列表
            </button>
          </div>
        </div>
      ) : null}

      {dupDialog
        ? createPortal(
            <div className="modal-backdrop" onClick={() => setDupDialog(null)}>
              <div className="modal-card" onClick={(e) => e.stopPropagation()}>
                <h3 className="subhead">发现重复管段</h3>
                <p className="muted small-note">
                  起点与终点相同或完全相反视为重复。共 {dupDialog.hits.length} 条与库内管段冲突。
                </p>
                <ul className="dup-list">
                  {dupDialog.hits.map((h) => (
                    <li key={h.source_path}>
                      {h.chain_start_label}～{h.chain_end_label}（已有 #{h.segment_ids.join(", #")}）
                    </li>
                  ))}
                </ul>
                <div className="toolbar">
                  <button
                    type="button"
                    className="btn secondary"
                    onClick={() => void doCommit("skip")}
                  >
                    忽略重复项
                  </button>
                  <button
                    type="button"
                    className="btn primary"
                    onClick={() => void doCommit("overwrite")}
                  >
                    覆盖已有管段
                  </button>
                  <button type="button" className="btn ghost" onClick={() => setDupDialog(null)}>
                    取消
                  </button>
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}

      {msg ? <p className="ok">{msg}</p> : null}
      {err ? <p className="error">{err}</p> : null}
      {lightboxSrc ? <ImageLightbox src={lightboxSrc} onClose={() => setLightboxSrc(null)} /> : null}
    </section>
  );
}
