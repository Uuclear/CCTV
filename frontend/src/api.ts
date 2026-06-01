import { readApiError } from "./apiErrors";

export type OcrStatus = {
  available: boolean;
  engine: string;
  error: string | null;
  ffmpeg_on_path?: boolean;
  ffprobe_on_path?: boolean;
};

export type Project = {
  id: number;
  name: string;
  client_org: string | null;
  build_org: string | null;
  supervision_org: string | null;
  design_org: string | null;
  construction_org: string | null;
  project_code: string | null;
  report_no: string | null;
  road_name: string | null;
  scope_text: string | null;
  contact_name: string | null;
  contact_phone: string | null;
  site_address: string | null;
  inspection_org: string | null;
  site_manager: string | null;
  report_author: string | null;
  qc_manager: string | null;
  k_value_default: number | null;
  created_at: string;
};

export type Segment = {
  id: number;
  project_id: number;
  original_filename: string | null;
  display_name: string | null;
  video_relpath: string | null;
  preview_frame_relpath: string | null;
  chain_start_label: string | null;
  chain_end_label: string | null;
  pipe_system: string | null;
  diameter_mm: number | null;
  pipe_length_m: number | null;
  pipe_material: string | null;
  repair_index: number | null;
  remark: string | null;
  inspection_date: string | null;
  ri: number | null;
  mi: number | null;
  ri_grade: string | null;
  mi_grade: string | null;
  created_at: string;
};

export type SegmentSummary = Segment & {
  defect_count: number;
  defect_summary: string | null;
};

export type SegmentWithSample = Segment & { sample_time_sec?: number | null };

export type Defect = {
  id: number;
  segment_id: number;
  defect_code: string;
  level: number;
  kind: string;
  clock_position: string | null;
  distance_m: number | null;
  note: string | null;
  created_at: string;
};

export type OcrPreviewOut = {
  raw_text: string;
  suggested_chain_start: string | null;
  suggested_chain_end: string | null;
  suggested_diameter_mm?: number | null;
  suggested_pipe_material?: string | null;
  suggested_inspection_date?: string | null;
  parse?: Record<string, unknown> | null;
  engine: string;
};

export type DefectCatalogItem = {
  code: string;
  name: string;
  kind: "structural" | "functional";
  max_level: number;
  mi_exclude?: boolean;
};

export type ImportDraft = {
  draft_id: string;
  source_path: string;
  original_filename: string;
  preview_frame_relpath: string | null;
  parse: {
    chain_start_label?: string | null;
    chain_end_label?: string | null;
    diameter_mm?: number | null;
    pipe_material?: string | null;
    pipe_system?: string | null;
    inspection_date?: string | null;
    chain_confidence?: number;
    chain_warnings?: string[];
    scan?: {
      ffmpeg_ok?: boolean;
      ocr_available?: boolean;
      ocr_engine?: string;
      ocr_error?: string | null;
      ffmpeg_error?: string | null;
      ocr_raw_text?: string;
      ocr_blocks?: string[];
      sample_frame_relpaths?: string[];
      sample_times_sec?: number[];
    };
  };
};

export async function fetchProjects(): Promise<Project[]> {
  const r = await fetch("/api/projects");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchProject(id: number): Promise<Project> {
  const r = await fetch(`/api/projects/${id}`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function patchProject(
  id: number,
  body: {
    name?: string;
    client_org?: string | null;
    build_org?: string | null;
    supervision_org?: string | null;
    design_org?: string | null;
    construction_org?: string | null;
    project_code?: string | null;
    report_no?: string | null;
    road_name?: string | null;
    scope_text?: string | null;
    contact_name?: string | null;
    contact_phone?: string | null;
    site_address?: string | null;
    inspection_org?: string | null;
    site_manager?: string | null;
    report_author?: string | null;
    qc_manager?: string | null;
    k_value_default?: number | null;
  },
): Promise<Project> {
  const r = await fetch(`/api/projects/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function createProject(body: {
  name: string;
  client_org?: string | null;
  build_org?: string | null;
  supervision_org?: string | null;
  design_org?: string | null;
  construction_org?: string | null;
  project_code?: string | null;
  report_no?: string | null;
  road_name?: string | null;
  scope_text?: string | null;
  contact_name?: string | null;
  contact_phone?: string | null;
  site_address?: string | null;
  inspection_org?: string | null;
  site_manager?: string | null;
  report_author?: string | null;
  qc_manager?: string | null;
  k_value_default?: number | null;
}): Promise<Project> {
  const r = await fetch("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchSegments(projectId: number): Promise<SegmentSummary[]> {
  const r = await fetch(`/api/projects/${projectId}/segments`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function createSegment(
  projectId: number,
  body: {
    display_name?: string | null;
    chain_start_label?: string | null;
    chain_end_label?: string | null;
  } = {},
): Promise<Segment> {
  const r = await fetch(`/api/projects/${projectId}/segments`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function patchSegment(
  segmentId: number,
  body: {
    display_name?: string | null;
    chain_start_label?: string | null;
    chain_end_label?: string | null;
    diameter_mm?: number | null;
    pipe_material?: string | null;
    pipe_system?: string | null;
    pipe_length_m?: number | null;
    remark?: string | null;
    inspection_date?: string | null;
    preview_frame_relpath?: string | null;
    video_relpath?: string | null;
  },
): Promise<Segment> {
  const r = await fetch(`/api/segments/${segmentId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function uploadSegmentVideo(segmentId: number, file: File): Promise<Segment> {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`/api/segments/${segmentId}/video`, {
    method: "POST",
    body: fd,
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function extractPreview(segmentId: number, margin_sec = 1): Promise<SegmentWithSample> {
  const r = await fetch(`/api/segments/${segmentId}/extract-preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ margin_sec }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function ocrSegmentPreview(segmentId: number): Promise<OcrPreviewOut> {
  const r = await fetch(`/api/segments/${segmentId}/ocr-preview`, { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchDefects(segmentId: number): Promise<Defect[]> {
  const r = await fetch(`/api/segments/${segmentId}/defects`);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function deleteSegment(segmentId: number): Promise<void> {
  let r = await fetch(`/api/segments/${segmentId}/remove`, { method: "POST" });
  if (!r.ok && r.status === 404) {
    r = await fetch(`/api/segments/${segmentId}`, { method: "DELETE" });
  }
  if (!r.ok) throw new Error(await readApiError(r));
}

export async function fetchDefectCatalog(): Promise<DefectCatalogItem[]> {
  const { DEFECT_CATALOG_FALLBACK } = await import("./defectCatalog");
  try {
    const r = await fetch("/api/standards/defects");
    if (r.ok) {
      const items = (await r.json()) as DefectCatalogItem[];
      if (items.length > 0) return items;
    }
  } catch {
    /* use fallback */
  }
  return DEFECT_CATALOG_FALLBACK;
}

export async function createDefect(
  segmentId: number,
  body: {
    defect_code: string;
    level: number;
    kind: "structural" | "functional";
    note?: string | null;
    distance_m?: number | null;
  },
): Promise<Defect> {
  const r = await fetch(`/api/segments/${segmentId}/defects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchOcrStatus(): Promise<OcrStatus> {
  const r = await fetch("/api/imports/ocr-status");
  if (!r.ok) throw new Error(await readApiError(r));
  return r.json();
}

export type ImportDuplicateHit = {
  source_path: string;
  segment_ids: number[];
  chain_start_label?: string | null;
  chain_end_label?: string | null;
};

/** Upload only — no OCR until user runs batch OCR. */
export async function uploadStageOneVideo(projectId: number, file: File): Promise<ImportDraft> {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`/api/projects/${projectId}/imports/upload-stage-one`, {
    method: "POST",
    body: fd,
  });
  if (!r.ok) throw new Error(await readApiError(r));
  return r.json();
}

export async function ocrImportOne(projectId: number, sourcePath: string): Promise<ImportDraft> {
  const r = await fetch(`/api/projects/${projectId}/imports/ocr-one`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_path: sourcePath }),
  });
  if (!r.ok) throw new Error(await readApiError(r));
  return r.json();
}

export async function checkImportDuplicates(
  projectId: number,
  items: { source_path: string; chain_start_label?: string | null; chain_end_label?: string | null }[],
): Promise<ImportDuplicateHit[]> {
  const r = await fetch(`/api/projects/${projectId}/imports/check-duplicates`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });
  if (!r.ok) throw new Error(await readApiError(r));
  return r.json();
}

export async function scanImportFolderStage(projectId: number, folder: string): Promise<ImportDraft[]> {
  const r = await fetch(`/api/projects/${projectId}/imports/scan-folder-stage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ folder }),
  });
  if (!r.ok) throw new Error(await readApiError(r));
  return r.json();
}

/** One file per request — legacy: upload + OCR immediately. */
export async function uploadScanOneVideo(projectId: number, file: File): Promise<ImportDraft> {
  const fd = new FormData();
  fd.append("file", file);
  const r = await fetch(`/api/projects/${projectId}/imports/upload-scan-one`, {
    method: "POST",
    body: fd,
  });
  if (!r.ok) throw new Error(await readApiError(r));
  return r.json();
}

export async function uploadScanVideos(projectId: number, files: File[]): Promise<ImportDraft[]> {
  const out: ImportDraft[] = [];
  for (const f of files) {
    out.push(await uploadScanOneVideo(projectId, f));
  }
  return out;
}

export async function scanImportFolder(projectId: number, folder: string): Promise<ImportDraft[]> {
  const r = await fetch(`/api/projects/${projectId}/imports/scan-folder`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ folder }),
  });
  if (!r.ok) throw new Error(await readApiError(r));
  return r.json();
}

export async function commitImports(
  projectId: number,
  items: {
    source_path: string;
    chain_start_label?: string | null;
    chain_end_label?: string | null;
    diameter_mm?: number | null;
    pipe_material?: string | null;
    inspection_date?: string | null;
    pipe_system?: string | null;
    pipe_length_m?: number | null;
    display_name?: string | null;
    preview_frame_relpath?: string | null;
    preview_sample_time_sec?: number | null;
    remark?: string | null;
    duplicate_policy?: "skip" | "overwrite";
  }[],
): Promise<Segment[]> {
  const r = await fetch(`/api/projects/${projectId}/imports/commit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items }),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function exportProjectDocx(projectId: number): Promise<{ docx_relpath: string; media_url: string }> {
  const r = await fetch(`/api/projects/${projectId}/reports/docx`, { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function downloadStatisticsXlsx(projectId: number, filename?: string): Promise<void> {
  const r = await fetch(`/api/projects/${projectId}/export/statistics.xlsx`);
  if (!r.ok) throw new Error(await readApiError(r));
  const blob = await r.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename ?? `管段统计表_${projectId}.xlsx`;
  a.click();
  URL.revokeObjectURL(url);
}
