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

export async function fetchProjects(): Promise<Project[]> {
  const r = await fetch("/api/projects");
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

export async function createProject(body: {
  name: string;
  client_org?: string;
  project_code?: string;
}): Promise<Project> {
  const r = await fetch("/api/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}
