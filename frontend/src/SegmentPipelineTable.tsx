import type { SegmentSummary } from "./api";
import { formatConditionGrade } from "./segmentDisplay";

export type SegmentPatch = {
  pipe_system?: string | null;
  pipe_material?: string | null;
  chain_start_label?: string | null;
  chain_end_label?: string | null;
  diameter_mm?: number | null;
  pipe_length_m?: number | null;
  remark?: string | null;
};

type Props = {
  segments: SegmentSummary[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  onPatch: (id: number, patch: SegmentPatch) => void;
};

export function SegmentPipelineTable({ segments, selectedId, onSelect, onPatch }: Props) {
  if (segments.length === 0) {
    return <p className="muted">暂无管段。批量导入视频解析入库后，将在此以表格展示。</p>;
  }

  function stop(e: React.SyntheticEvent) {
    e.stopPropagation();
  }

  return (
    <div className="table-wrap">
      <table className="data-table pipeline-table pipeline-table-editable">
        <thead>
          <tr>
            <th>序号</th>
            <th>管道类型</th>
            <th>管材</th>
            <th>起点</th>
            <th>终点</th>
            <th>管径</th>
            <th>长度</th>
            <th>缺陷</th>
            <th>修复指数</th>
            <th>结构状况</th>
            <th>养护指数</th>
            <th>功能状况</th>
            <th>备注</th>
          </tr>
        </thead>
        <tbody>
          {segments.map((s, i) => (
            <tr
              key={s.id}
              className={selectedId === s.id ? "row-selected" : ""}
              data-testid={`segment-row-${s.id}`}
              onClick={() => onSelect(s.id)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") onSelect(s.id);
              }}
            >
              <td>{i + 1}</td>
              <td onClick={stop}>
                <input
                  className="cell-input"
                  defaultValue={s.pipe_system ?? ""}
                  onBlur={(e) => onPatch(s.id, { pipe_system: e.target.value || null })}
                />
              </td>
              <td onClick={stop}>
                <input
                  className="cell-input"
                  defaultValue={s.pipe_material ?? ""}
                  onBlur={(e) => onPatch(s.id, { pipe_material: e.target.value || null })}
                />
              </td>
              <td onClick={stop}>
                <input
                  className="cell-input"
                  defaultValue={s.chain_start_label ?? ""}
                  onBlur={(e) => onPatch(s.id, { chain_start_label: e.target.value || null })}
                />
              </td>
              <td onClick={stop}>
                <input
                  className="cell-input"
                  defaultValue={s.chain_end_label ?? ""}
                  onBlur={(e) => onPatch(s.id, { chain_end_label: e.target.value || null })}
                />
              </td>
              <td onClick={stop}>
                <input
                  className="cell-input cell-input-num"
                  defaultValue={s.diameter_mm != null ? String(s.diameter_mm) : ""}
                  onBlur={(e) =>
                    onPatch(s.id, {
                      diameter_mm: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                />
              </td>
              <td onClick={stop}>
                <input
                  className="cell-input cell-input-num"
                  defaultValue={s.pipe_length_m != null ? String(s.pipe_length_m) : ""}
                  onBlur={(e) =>
                    onPatch(s.id, {
                      pipe_length_m: e.target.value ? Number(e.target.value) : null,
                    })
                  }
                />
              </td>
              <td className="mono">{s.defect_summary ?? "无"}</td>
              <td>{s.ri != null ? s.ri : "—"}</td>
              <td>{formatConditionGrade(s.ri_grade, s.ri)}</td>
              <td>{s.mi != null ? s.mi : "—"}</td>
              <td>{formatConditionGrade(s.mi_grade, s.mi)}</td>
              <td onClick={stop}>
                <input
                  className="cell-input"
                  defaultValue={s.remark ?? ""}
                  onBlur={(e) => onPatch(s.id, { remark: e.target.value || null })}
                />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="muted small-note">
        表格内可编辑基础字段（失焦保存）；结构/功能状况由修复指数、养护指数自动评定。删除管段请在选中后于下方操作。
      </p>
    </div>
  );
}
