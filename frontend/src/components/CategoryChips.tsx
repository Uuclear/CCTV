/** 分类筛选芯片 */
import type { Category } from "../api/types";

interface Props {
  categories: Category[];
  value: string;
  onChange: (slug: string) => void;
}

/** 渲染全部分类 + 可选项芯片 */
export default function CategoryChips({ categories, value, onChange }: Props) {
  return (
    <div className="chip-row" role="tablist" aria-label="按分类筛选">
      <button
        type="button"
        className={`chip ${value === "" ? "active" : ""}`}
        onClick={() => onChange("")}
      >
        全部
      </button>
      {categories.map((c) => (
        <button
          key={c.id}
          type="button"
          className={`chip ${value === c.slug ? "active" : ""}`}
          onClick={() => onChange(c.slug)}
        >
          {c.name}
          <span style={{ opacity: 0.7 }}> · {c.wallpaper_count}</span>
        </button>
      ))}
    </div>
  );
}
