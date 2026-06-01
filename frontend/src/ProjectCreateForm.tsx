import { useState } from "react";
import { createProject } from "./api";
import { ProjectInfoForm } from "./ProjectInfoForm";
import {
  emptyProjectForm,
  formToProjectPayload,
  warnCodeFormats,
} from "./projectConstants";

type Props = {
  onCreated: (projectId: number) => void;
};

export function ProjectCreateForm({ onCreated }: Props) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [form, setForm] = useState(emptyProjectForm);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.name.trim()) {
      setErr("请填写工程名称");
      return;
    }
    warnCodeFormats(form.project_code, form.report_no);
    setBusy(true);
    setErr(null);
    try {
      const p = await createProject(formToProjectPayload(form));
      onCreated(p.id);
      setForm(emptyProjectForm());
    } catch (e) {
      setErr(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card">
      <h2 className="card-title">新建工程</h2>
      <p className="muted">仅工程名称为必填；编号后缀建议 6 位数字（格式不符仅提醒，不阻止保存）。</p>
      <form onSubmit={(e) => void onSubmit(e)}>
        <ProjectInfoForm
          form={form}
          onChange={(patch) => setForm((f) => ({ ...f, ...patch }))}
          nameRequired
        />
        <div style={{ marginTop: 16 }}>
          <button className="btn primary" type="submit" disabled={busy}>
            {busy ? "创建中…" : "创建并进入工作台"}
          </button>
        </div>
      </form>
      {err ? <p className="error">{err}</p> : null}
    </section>
  );
}
