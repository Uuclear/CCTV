export type Project = {
  id: number;
  name: string;
  client_org: string | null;
  project_code: string | null;
  road_name: string | null;
  scope_text: string | null;
  contact_name: string | null;
  contact_phone: string | null;
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
  ri: number | null;
  mi: number | null;
  ri_grade: string | null;
  mi_grade: string | null;
  created_at: string;
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
  engine: string;
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
    project_code?: string | null;
    road_name?: string | null;
    scope_text?: string | null;
    contact_name?: string | null;
    contact_phone?: string | null;
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
  project_code?: string | null;
  road_name?: string | null;
  scope_text?: string | null;
  contact_name?: string | null;
  contact_phone?: string | null;
}): Promise<Project> {
  const r = await fetch("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function fetchSegments(projectId: number): Promise<Segment[]> {
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

export async function createDefect(
  segmentId: number,
  body: {
    defect_code: string;
    level: number;
    kind: "structural" | "functional";
    note?: string | null;
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

export async function exportProjectDocx(projectId: number): Promise<{ docx_relpath: string; media_url: string }> {
  const r = await fetch(`/api/projects/${projectId}/reports/docx`, { method: "POST" });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
