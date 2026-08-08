/** 展示风格切换器 */
import type { ViewMode } from "../api/types";

const MODES: { id: ViewMode; label: string }[] = [
  { id: "masonry", label: "瀑布" },
  { id: "grid", label: "网格" },
  { id: "cinema", label: "影院" },
  { id: "river", label: "溪流" },
];

interface Props {
  value: ViewMode;
  onChange: (mode: ViewMode) => void;
}

/** 切换四种子风格布局 */
export default function ViewSwitch({ value, onChange }: Props) {
  return (
    <div className="view-switch" role="group" aria-label="展示风格">
      {MODES.map((m) => (
        <button
          key={m.id}
          type="button"
          className={value === m.id ? "active" : ""}
          onClick={() => onChange(m.id)}
        >
          {m.label}
        </button>
      ))}
    </div>
  );
}
