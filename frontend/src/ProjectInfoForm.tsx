import {
  CODE_SUFFIX_DIGITS,
  PREFIX_PROJECT_CODE,
  PREFIX_REPORT_NO,
  type ProjectFormValues,
  validateCodeSuffix,
} from "./projectConstants";

type RowProps = {
  label: string;
  hint?: string;
  children: React.ReactNode;
  warn?: string | null;
};

function FormRow({ label, hint, children, warn }: RowProps) {
  return (
    <div className="info-row">
      <div className="info-label">
        <span>{label}</span>
        {hint ? <span className="info-hint">{hint}</span> : null}
      </div>
      <div className="info-value">
        {children}
        {warn ? <span className="field-warn">{warn}</span> : null}
      </div>
    </div>
  );
}

type Props = {
  form: ProjectFormValues;
  onChange: (patch: Partial<ProjectFormValues>) => void;
  nameRequired?: boolean;
  showScope?: boolean;
  testIdPrefix?: string;
};

export function ProjectInfoForm({
  form,
  onChange,
  nameRequired,
  showScope = true,
  testIdPrefix = "pj",
}: Props) {
  const codeWarn = validateCodeSuffix(form.project_code, PREFIX_PROJECT_CODE);
  const reportWarn = validateCodeSuffix(form.report_no, PREFIX_REPORT_NO);

  return (
    <div className="info-form">
      <FormRow label={nameRequired ? "工程名称 *" : "工程名称"}>
        <input
          value={form.name}
          onChange={(e) => onChange({ name: e.target.value })}
          data-testid={`${testIdPrefix}-name`}
          required={nameRequired}
        />
      </FormRow>

      <div className="info-row info-row-split">
        <div className="info-label">
          <span>委托编号 / 报告编号</span>
          <span className="info-hint">后缀 {CODE_SUFFIX_DIGITS} 位数字</span>
        </div>
        <div className="info-value info-codes">
          <div className="code-field">
            <div className="prefixed-input">
              <span className="prefix">{PREFIX_PROJECT_CODE}</span>
              <input
                value={form.project_code}
                onChange={(e) => onChange({ project_code: e.target.value })}
                placeholder="000001"
                data-testid={`${testIdPrefix}-code`}
              />
            </div>
            {codeWarn ? <span className="field-warn">{codeWarn}</span> : null}
          </div>
          <div className="code-field">
            <div className="prefixed-input">
              <span className="prefix">{PREFIX_REPORT_NO}</span>
              <input
                value={form.report_no}
                onChange={(e) => onChange({ report_no: e.target.value })}
                placeholder="000001"
              />
            </div>
            {reportWarn ? <span className="field-warn">{reportWarn}</span> : null}
          </div>
        </div>
      </div>

      <FormRow label="工程地点">
        <input value={form.site_address} onChange={(e) => onChange({ site_address: e.target.value })} />
      </FormRow>
      <FormRow label="委托单位">
        <input
          value={form.client_org}
          onChange={(e) => onChange({ client_org: e.target.value })}
          data-testid={`${testIdPrefix}-client`}
        />
      </FormRow>
      <FormRow label="建设单位">
        <input value={form.build_org} onChange={(e) => onChange({ build_org: e.target.value })} />
      </FormRow>
      <FormRow label="设计单位">
        <input value={form.design_org} onChange={(e) => onChange({ design_org: e.target.value })} />
      </FormRow>
      <FormRow label="监理单位">
        <input value={form.supervision_org} onChange={(e) => onChange({ supervision_org: e.target.value })} />
      </FormRow>
      <FormRow label="施工单位">
        <input value={form.construction_org} onChange={(e) => onChange({ construction_org: e.target.value })} />
      </FormRow>
      <FormRow label="检测单位">
        <input value={form.inspection_org} onChange={(e) => onChange({ inspection_org: e.target.value })} />
      </FormRow>
      <FormRow label="现场负责人">
        <input value={form.site_manager} onChange={(e) => onChange({ site_manager: e.target.value })} />
      </FormRow>
      <FormRow label="报告编写人">
        <input value={form.report_author} onChange={(e) => onChange({ report_author: e.target.value })} />
      </FormRow>
      <FormRow label="质检部负责人">
        <input value={form.qc_manager} onChange={(e) => onChange({ qc_manager: e.target.value })} />
      </FormRow>

      {showScope ? (
        <FormRow label="检测内容说明">
          <textarea
            rows={2}
            value={form.scope_text}
            onChange={(e) => onChange({ scope_text: e.target.value })}
            data-testid={`${testIdPrefix}-scope`}
          />
        </FormRow>
      ) : null}
    </div>
  );
}
