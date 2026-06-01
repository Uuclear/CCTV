/** 结构/功能状况仅展示 一级|二级|三级 */
export function formatConditionGrade(
  grade: string | null | undefined,
  index?: number | null,
): string {
  if (grade) {
    const g = grade.trim();
    if (g === "一级" || g === "二级" || g === "三级") return g;
    if (g === "0" || g === "0级" || g === "0.0") return "一级";
    if (g === "1" || g === "1级") return "一级";
    if (g === "2" || g === "2级") return "二级";
    if (g === "3" || g === "3级") return "三级";
  }
  if (index == null || index === 0) return "一级";
  if (index < 4) return "一级";
  if (index < 7) return "二级";
  return "三级";
}
