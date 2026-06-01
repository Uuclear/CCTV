import type { DefectCatalogItem } from "./api";

/** DB31/T 444-2022 表7、表8 — docs/design/evaluation-engine.md §2 */
export const DEFECT_CATALOG_FALLBACK: DefectCatalogItem[] = [
  { code: "PL", name: "破裂", kind: "structural", max_level: 4 },
  { code: "BX", name: "变形", kind: "structural", max_level: 3 },
  { code: "CW", name: "错位", kind: "structural", max_level: 4 },
  { code: "TJ", name: "脱节", kind: "structural", max_level: 4 },
  { code: "SL", name: "渗漏", kind: "structural", max_level: 4 },
  { code: "FS", name: "腐蚀", kind: "structural", max_level: 3 },
  { code: "JQ", name: "胶圈脱落", kind: "structural", max_level: 3 },
  { code: "AJ", name: "支管暗接", kind: "structural", max_level: 4 },
  { code: "QR", name: "异物侵入", kind: "structural", max_level: 3 },
  { code: "CJ", name: "沉积", kind: "functional", max_level: 3 },
  { code: "JG", name: "结垢", kind: "functional", max_level: 3 },
  { code: "ZW", name: "障碍物", kind: "functional", max_level: 3 },
  { code: "SG", name: "树根", kind: "functional", max_level: 3 },
  { code: "WS", name: "洼水", kind: "functional", max_level: 3 },
  { code: "BT", name: "坝头", kind: "functional", max_level: 3 },
  { code: "FZ", name: "浮渣", kind: "functional", max_level: 3, mi_exclude: true },
];
