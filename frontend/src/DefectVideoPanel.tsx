import { useEffect, useRef, useState } from "react";

import { DEFECT_CATALOG_FALLBACK } from "./defectCatalog";
import { createDefect, fetchDefectCatalog, type DefectCatalogItem } from "./api";

type Props = {
  segmentId: number;
  videoUrl: string | null;
  onDefectAdded: () => void;
};

export function DefectVideoPanel({ segmentId, videoUrl, onDefectAdded }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [catalog, setCatalog] = useState<DefectCatalogItem[]>([]);
  const [defectCode, setDefectCode] = useState("PL");
  const [defectLevel, setDefectLevel] = useState(1);
  const [pausedAt, setPausedAt] = useState<number | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  useEffect(() => {
    fetchDefectCatalog()
      .then((items) => {
        setCatalog(items);
        if (items.length) setDefectCode(items[0].code);
      })
      .catch(() => setCatalog(DEFECT_CATALOG_FALLBACK));
  }, []);

  const selected = catalog.find((c) => c.code === defectCode);
  const kind = selected?.kind ?? "structural";
  const maxLevel = selected?.max_level ?? 4;

  function capturePauseTime() {
    const v = videoRef.current;
    if (!v) return;
    v.pause();
    setPausedAt(v.currentTime);
  }

  async function onAddAtPause() {
    if (pausedAt == null) {
      setErr("请先暂停视频并点击「记录当前画面」");
      return;
    }
    setBusy(true);
    setErr(null);
    try {
      const item = catalog.find((c) => c.code === defectCode);
      await createDefect(segmentId, {
        defect_code: defectCode,
        level: defectLevel,
        kind: (item?.kind ?? "structural") as "structural" | "functional",
        note: `视频暂停 @ ${pausedAt.toFixed(2)}s`,
        distance_m: pausedAt,
      });
      setPausedAt(null);
      onDefectAdded();
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  if (!videoUrl) {
    return <p className="muted small-note">请先上传或批量导入带视频文件的管段。</p>;
  }

  return (
    <div className="defect-video-panel">
      <video
        ref={videoRef}
        className="defect-video"
        src={videoUrl}
        controls
        preload="metadata"
        data-testid="defect-video"
      />
      <div className="toolbar" style={{ marginTop: 8 }}>
        <button type="button" className="btn secondary" onClick={capturePauseTime}>
          记录当前画面（暂停）
        </button>
        {pausedAt != null ? (
          <span className="muted small-note">已记录 {pausedAt.toFixed(2)}s</span>
        ) : null}
      </div>
      <div className="row" style={{ marginTop: 10 }}>
        <label className="field grow">
          <span>缺陷（标准）</span>
          <select
            value={defectCode}
            data-testid="defect-code-select"
            onChange={(e) => {
              setDefectCode(e.target.value);
              const c = catalog.find((x) => x.code === e.target.value);
              if (c) setDefectLevel(Math.min(defectLevel, c.max_level));
            }}
          >
            {(catalog.length ? catalog : DEFECT_CATALOG_FALLBACK).map((c) => (
              <option key={`${c.kind}-${c.code}`} value={c.code}>
                {c.name} ({c.code}) · {c.kind === "structural" ? "结构" : "功能"}
              </option>
            ))}
          </select>
        </label>
        <label className="field slim">
          <span>等级</span>
          <select
            value={defectLevel}
            data-testid="defect-level"
            onChange={(e) => setDefectLevel(Number(e.target.value))}
          >
            {Array.from({ length: maxLevel }, (_, i) => i + 1).map((n) => (
              <option key={n} value={n}>
                {n} 级
              </option>
            ))}
          </select>
        </label>
        <button
          type="button"
          className="btn primary"
          data-testid="add-defect"
          disabled={busy || pausedAt == null}
          onClick={() => void onAddAtPause()}
        >
          在暂停处添加缺陷
        </button>
      </div>
      <p className="muted small-note">
        类型：{kind === "structural" ? "结构性" : "功能性"}。播放视频 → 暂停 →「记录当前画面」→ 选择缺陷与等级 → 添加。
      </p>
      {err ? <p className="error">{err}</p> : null}
    </div>
  );
}
