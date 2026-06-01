export const DEFAULT_INSPECTION_ORG = "上海建科检验检测认证有限公司";
export const DEFAULT_SITE_MANAGER = "胡跃进";
export const DEFAULT_REPORT_AUTHOR = "秦臻";
export const DEFAULT_QC_MANAGER = "张峙琪";
export const PREFIX_PROJECT_CODE = "CC01-";
export const PREFIX_REPORT_NO = "CC018-";
export const CODE_SUFFIX_DIGITS = 6;

export function withPrefix(value: string, prefix: string): string {
  const v = value.trim();
  if (!v) return "";
  if (v.toUpperCase().startsWith(prefix.toUpperCase())) return v;
  return `${prefix}${v}`;
}

export function stripPrefix(value: string, prefix: string): string {
  const v = value.trim();
  if (!v) return "";
  if (v.toUpperCase().startsWith(prefix.toUpperCase())) {
    return v.slice(prefix.length);
  }
  return v;
}

/** Soft validation: suffix after prefix must be exactly 6 digits. */
export function validateCodeSuffix(fullOrSuffix: string, prefix: string): string | null {
  const trimmed = fullOrSuffix.trim();
  if (!trimmed) return null;
  const full = withPrefix(trimmed, prefix);
  const suffix = stripPrefix(full, prefix);
  if (!/^\d{6}$/.test(suffix)) {
    return `「${prefix}」后应为 ${CODE_SUFFIX_DIGITS} 位数字，当前为「${suffix || "（空）"}」`;
  }
  return null;
}

export function warnCodeFormats(projectCode: string, reportNo: string): void {
  const msgs = [
    validateCodeSuffix(projectCode, PREFIX_PROJECT_CODE),
    validateCodeSuffix(reportNo, PREFIX_REPORT_NO),
  ].filter(Boolean) as string[];
  if (msgs.length > 0) {
    window.alert(`编号格式提醒（仍可保存）：\n\n${msgs.join("\n")}`);
  }
}

export type ProjectFormValues = {
  name: string;
  project_code: string;
  report_no: string;
  site_address: string;
  client_org: string;
  build_org: string;
  design_org: string;
  supervision_org: string;
  construction_org: string;
  inspection_org: string;
  site_manager: string;
  report_author: string;
  qc_manager: string;
  scope_text: string;
};

export const emptyProjectForm = (): ProjectFormValues => ({
  name: "",
  project_code: "",
  report_no: "",
  site_address: "",
  client_org: "",
  build_org: "",
  design_org: "",
  supervision_org: "",
  construction_org: "",
  inspection_org: DEFAULT_INSPECTION_ORG,
  site_manager: DEFAULT_SITE_MANAGER,
  report_author: DEFAULT_REPORT_AUTHOR,
  qc_manager: DEFAULT_QC_MANAGER,
  scope_text: "",
});

export function projectToForm(p: {
  name: string;
  project_code?: string | null;
  report_no?: string | null;
  site_address?: string | null;
  client_org?: string | null;
  build_org?: string | null;
  design_org?: string | null;
  supervision_org?: string | null;
  construction_org?: string | null;
  inspection_org?: string | null;
  site_manager?: string | null;
  report_author?: string | null;
  qc_manager?: string | null;
  scope_text?: string | null;
}): ProjectFormValues {
  return {
    name: p.name,
    project_code: stripPrefix(p.project_code ?? "", PREFIX_PROJECT_CODE),
    report_no: stripPrefix(p.report_no ?? "", PREFIX_REPORT_NO),
    site_address: p.site_address ?? "",
    client_org: p.client_org ?? "",
    build_org: p.build_org ?? "",
    design_org: p.design_org ?? "",
    supervision_org: p.supervision_org ?? "",
    construction_org: p.construction_org ?? "",
    inspection_org: p.inspection_org ?? DEFAULT_INSPECTION_ORG,
    site_manager: p.site_manager ?? DEFAULT_SITE_MANAGER,
    report_author: p.report_author ?? DEFAULT_REPORT_AUTHOR,
    qc_manager: p.qc_manager ?? DEFAULT_QC_MANAGER,
    scope_text: p.scope_text ?? "",
  };
}

export function formToProjectPayload(form: ProjectFormValues) {
  return {
    name: form.name.trim(),
    site_address: form.site_address.trim() || null,
    client_org: form.client_org.trim() || null,
    build_org: form.build_org.trim() || null,
    design_org: form.design_org.trim() || null,
    supervision_org: form.supervision_org.trim() || null,
    construction_org: form.construction_org.trim() || null,
    inspection_org: form.inspection_org.trim() || DEFAULT_INSPECTION_ORG,
    site_manager: form.site_manager.trim() || null,
    report_author: form.report_author.trim() || null,
    qc_manager: form.qc_manager.trim() || null,
    project_code: form.project_code.trim() ? withPrefix(form.project_code, PREFIX_PROJECT_CODE) : null,
    report_no: form.report_no.trim() ? withPrefix(form.report_no, PREFIX_REPORT_NO) : null,
    scope_text: form.scope_text.trim() || null,
  };
}
