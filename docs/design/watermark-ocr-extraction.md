# 看板水印 / 文件名 — OCR 提取与起止井号解析规格

> 对应能力：**批量导入视频** 时从画面 OSD 与文件名得到 **起止井号、管径、管材、检测日期**。  
> 原则：**规则可单测、结果可解释**；所有自动结果进草稿表，**人工确认后入库**。

**重要**：现场 OSD **不保证行序**（管径、链号、管材可能任意上下排列，或分多块显示）。本规格 **禁止** 用「第 1/2/3 行」推断字段类型，一律采用 **按文本内容分类 + 分字段择优**。

样例画面（`视频/W9-W10.mp4`）：左上可能出现 `DN500`、`w9-w10`、`球墨铸铁` 等，**顺序不固定**。

---

## 1. 输入与输出

### 1.1 输入

| 来源 | 说明 |
|------|------|
| `frame_image` | ffmpeg 在 0/2/5/10 s 抽取的帧（取清晰度最高的一帧） |
| `filename_stem` | 无扩展名文件名 |
| `roi_template_id` | 水印区域模板，默认 `cctv_osd_v1` |

### 1.2 OCR 中间结构（不按行序依赖）

对每一 ROI 裁剪图做 OCR，得到 **文本块列表** `TextBlock[]`（PaddleOCR 检测框 + 识别文本）：

```json
{
  "text": "DN500",
  "confidence": 0.94,
  "bbox": [x0, y0, x1, y1],
  "roi_id": "top_left_meta"
}
```

- **不**假设 `bbox.top` 小者一定是管径。  
- 行聚类（按 y 坐标合并同一行）**仅用于** UI 展示或拼接 **同一逻辑串**（如 `DN` 与 `500` 被拆成两框时合并），**不**用于字段类型判定。

### 1.3 输出（`ParseResult`）

与先前相同：`chain_start_label`、`chain_end_label`、`diameter_mm`、`pipe_material`、`inspection_date` 及置信度、warnings。

---

## 2. 处理流水线（内容驱动）

```text
1. 裁 ROI（位置只限定「在哪找」，不限定「第几行是什么」）
2. OCR → TextBlock[]（每 ROI 内全部文本块）
3. 对每个 TextBlock 做 content_type 分类（可多标签，取得分最高者）
4. 分字段聚合候选 → 每字段选最优候选（§2.2）
5. 起止井号：汇总所有 chain 类块 + 文件名，走 §3 令牌解析
6. 交叉验证、warnings → ParseResult
```

### 2.1 文本块内容类型 `content_type`

对每个块 `text`（预处理后）计算各类 **匹配得分** `score ∈ [0,1]`，取得分最高且 ≥ 阈值的类型（默认阈值 0.55）。

| content_type | 判定依据（摘要） | 详见 |
|--------------|------------------|------|
| `diameter` | 命中 DN/φ/mm 管径正则 | §4 |
| `chain` | 含 `-` 且含井号令牌或描述性链号模式 | §3 |
| `material` | 管材词表命中 | §5 |
| `date` | 日期正则且非时间行 | §6 |
| `time` | UTC、上午/下午、时:分:秒 | §6 |
| `distance` | `\d+(\.\d+)?\s*m` | 可选 |
| `road` | 路名/通道词表，且无管径/链号主导 | §5 |
| `project_banner` | 长文本、含「工程」「项目」等 | 校验用 |
| `unknown` | 无类型超阈值 | 人工看 |

同一块 **不得** 同时强匹配 `diameter` 与 `material`：若得分接近，用 **互斥规则**（§2.3）。

### 2.2 每字段择优（与块在画面上的上下顺序无关）

| 目标字段 | 候选来源 | 选择规则 |
|----------|----------|----------|
| `diameter_mm` | 所有 `content_type=diameter` 的块 | 取得分最高；同分取 OCR `confidence` 高者 |
| `pipe_material` | 所有 `material` 块 | 词表命中长度最长；同分取 confidence |
| `inspection_date` | 所有 `date` 块（`top_left` + `bottom_left` + 全幅兜底扫描） | 得分最高；多帧取众数 |
| 起止井号 | 所有 `chain` 块 + **拼接后的 meta 全文** + 文件名 | §3 |

**meta 区全文拼接（仅用于链号）**：将 `top_left_meta` 内所有块按阅读顺序用空格连接为 `meta_blob`，再跑一遍 §3 解析，避免链号被拆成多框时漏检。

### 2.3 类型互斥与排除

| 若文本… | 则不要标为… |
|---------|-------------|
| 匹配 `DN\d+` / `φ\d+` | `material`、`chain` |
| 仅一个 `WELL_TOKEN`、无 `-`、无中文后缀 | 不单作 `chain`（可能是误框）；除非整块仅数字字母且长≤8 |
| 命中管材词表 | 非 `diameter` |
| 含「通道」「路」「弄」「号」且无「管」「DN」 | 优先 `road`，非 `material` |
| 形如 `NH2W5` 且为独立块 | `chain` 候选，**非** `material` |
| 含 `UTC` / `\d{1,2}:\d{2}` | `date` → 改为 `time` |

---

## 3. 起止井号解析（与块顺序无关）

### 3.1 井号令牌 `WELL_TOKEN`

```regex
(?i)\b([A-Z]{1,6}\d+(?:-[A-Za-z0-9]+)*)\b
```

| 示例串 | tokens |
|--------|--------|
| `W9-W10` | W9, W10 |
| `W9-W9-1` | W9, W9-1 |
| `W9-1-W9-2` | W9-1, W9-2 |
| `W11-2-NH2W5` | W11-2, NH2W5 |
| `w9-污水监测井` | W9（+ 描述后缀） |

### 3.2 OCR 侧：从「链号候选」提取（非固定行）

**链号候选集合** = 满足任一：

1. `content_type == chain` 的 TextBlock 的 `text`  
2. `meta_blob`（左上 ROI 全部块拼接）  
3. 对 `meta_blob` 中 **未分类** 的块，若含 `-` 且含字母数字，追加为弱候选（score×0.8）

对集合中 **每一条** 文本独立执行 `parse_chain_from_text`（§3.4），得到多个 `ChainParse` 结果，再：

- 优先采用 `well_pair` 且 tokens 数=2 的结果；  
- 若多条一致 → 提高置信度；  
- 若冲突 → 取 OCR confidence 加权最高的一条，并 warning `CHAIN_MULTI_CANDIDATE_CONFLICT`。

**与行序无关示例**（同一帧三块 OCR，顺序任意）：

| 块 A | 块 B | 块 C | 提取结果 |
|------|------|------|----------|
| `球墨铸铁` | `DN500` | `w9-w10` | 管材←A，管径←B，起止←C |
| `w9-w10` | `球墨铸铁` | `DN500` | **相同** |
| `DN500` | `w9-w10` | `公共通道2` | 管径、链号、路名各归其类 |

### 3.3 文件名解析

对 `filename_stem` 执行与 §3.4 相同逻辑（与 OCR 块顺序无关）。

| 文件名 | 起 → 止 | mode |
|--------|---------|------|
| `W9-W10` | W9 → W10 | well_pair |
| `W9-W9-1` | W9 → W9-1 | well_pair |
| `W9-1-W9-2` | W9-1 → W9-2 | well_pair |
| `W11-污水监测井` | W11 → 污水监测井 | descriptive_end |

### 3.4 `parse_chain_from_text(text)`（单条文本）

1. 预处理：去空格、全角→半角、OCR `1o`→`10` 等（仅链号数字段）。  
2. `WELL_TOKEN` 全局扫描 → `tokens[]`。  
3. `len(tokens) >= 2` → 起=`tokens[0]`，止=`tokens[-1]`，`well_pair`。  
4. `len(tokens) == 1` → 起=`tokens[0]`，止=描述后缀（最后一个 `-` 后中文等），`descriptive_end`。  
5. 否则 → `unparsed`。

### 3.5 合并优先级（OCR vs 文件名）

1. OCR 链号候选（§3.2）置信度 ≥ 阈值  
2. 文件名 `well_pair`  
3. 二者互补（仅一端有值）  
4. 冲突：默认 **OCR 优先**，UI 展示文件名备选 `chain_alt_*`

### 3.6 mode / warnings

（同前：`well_pair`、`descriptive_end`、`single_well`、`unparsed`；`END_LABEL_DESCRIPTIVE`、`OCR_FILENAME_MISMATCH` 等。）

tokens>2：**首 token 为起点，末 token 为终点**，warning `EXTRA_TOKENS_IGNORED`。

---

## 4. 管径提取（内容匹配，非第 N 行）

**候选**：所有 `content_type=diameter` 的块，或对 **每个** `top_left_meta` 块尝试下列正则（命中则该块标为 diameter）：

| 优先级 | 正则 | 示例 | `diameter_mm` |
|--------|------|------|---------------|
| 1 | `(?i)DN\s*(\d{2,4})` | DN500 | 500 |
| 2 | `(?i)[φΦ]\s*(\d{2,4})` | φ1200 | 1200 |
| 3 | `(?i)(\d{3,4})\s*mm` | 500mm | 500 |
| 4 | `(?i)D\s*(\d{2,4})(?!-)` | D500 | 500 |

**择优**：`score_diameter` 最高者；`DN5OO` 等仅在 diameter 类块内做 O→0。

**多块冲突**（如误识别两块都有 DN）：取 confidence 高者，warning `DIAMETER_MULTIPLE_CANDIDATES`。

校验：150–3000 mm，超出 warning `DIAMETER_OUT_OF_RANGE`。

---

## 5. 管材提取（词表，非第 N 行）

**候选**：`content_type=material` 的块；或对 meta 内块：若 **未** 标为 diameter/chain/date/time/distance，且命中管材词表 → 标为 material。

词表（最长优先子串匹配）：

| 关键词 | 规范值 |
|--------|--------|
| 球墨铸铁、球墨铸铁管 | 球墨铸铁 |
| HDPE、高密度聚乙烯、PE管 | HDPE |
| 混凝土、钢筋混凝土、砼 | 钢筋混凝土 |
| PVC、UPVC、塑料管 | PVC |
| 玻璃钢、FRP | 玻璃钢 |
| 钢管 | 钢管 |
| 铸铁 | 铸铁 |

**路名排除**：含「通道」「路」「弄」且不含「管」「DN」「铸铁」等 → `road`，不作为管材。

**多块命中**：取得分最高；仍无命中但块为纯中文 2–8 字且无数字 → `MATERIAL_GUESS_RAW`（低置信度），**不用行号兜底**。

**与链号混淆**：块若匹配 `WELL_TOKEN` 且整体像井号，标 `chain` 而非 `material`。

---

## 6. 检测日期（全区域扫描，非固定左下）

**候选来源**（任一 ROI 内所有块均可出现日期，不假定只在左下）：

1. `bottom_left_date` ROI 内全部块  
2. `top_left_meta` 内被标为 `date` 的块（有的设备把日期打在左上）  
3. **全帧弱扫描**：对未归入其他类型的块再跑日期正则（防止 ROI 模板偏移）

**日期正则**：

| 模式 | 示例 | 规范化 |
|------|------|--------|
| `(\d{4})[/\-年](\d{1,2})[/\-月](\d{1,2})` | 2026/4/21 | 2026-04-21 |
| `(\d{4})(\d{2})(\d{2})` | 20260421 | 2026-04-21 |

**排除时间**：块内含 `UTC`、`上午`、`下午`、或 `\d{1,2}:\d{2}:\d{2}` → 标 `time`，不写 `inspection_date`。

**择优**：多候选取 `score_date` 最高；多帧取众数。校验 2000-01-01～今天+1 天。

---

## 7. ROI 模板（只限定空间，不限定行义）

| ROI id | 相对区域 | 用途 |
|--------|----------|------|
| `top_left_meta` | 左上 ~38%×28% | 收集 **全部** 文本块后做类型分类 |
| `bottom_left_date` | 左下 ~22%×18% | 日期/时间候选 **之一** |
| `bottom_right_distance` | 右下 | 距离（可选） |
| `bottom_banner` | 底部通栏 | 工程名校验 |

**禁止**：在 `top_left_meta` 内按 y 排序后规定「第 1 行=管径」。  
**允许**：同一行内左右相距很近的两框合并为一个字符串后再分类（避免 `DN` | `500` 拆开）。

合并规则：两框垂直重叠 >50% 且水平间距 <0.5×行高 → 拼成 `DN500` 再分类。

---

## 8. 文件名 vs OCR

| 字段 | 不一致时 |
|------|----------|
| 起止井号 | OCR 链号候选优先；文件名作备选 |
| 管径/管材/日期 | 各字段独立择优，**不受** 链号块顺序影响 |

---

## 9. 伪代码（内容分类核心）

```python
def classify_block(text: str) -> tuple[str, float]:
    scores = {
        "diameter": score_diameter_patterns(text),
        "chain": score_chain_pattern(text),
        "material": score_material_lexicon(text),
        "date": score_date_pattern(text),
        "time": score_time_pattern(text),
        "road": score_road_lexicon(text),
    }
    scores = apply_mutual_exclusion(text, scores)
    best = max(scores, key=scores.get)
    return best, scores[best]

def extract_fields(blocks: list[TextBlock], filename: str) -> ParseResult:
    classified = [(b, *classify_block(b.text)) for b in blocks]
    diameter = pick_best([b for b, t, s in classified if t == "diameter"], key=score_diameter)
    material = pick_best([b for b, t, s in classified if t == "material"], key=score_material)
    date = pick_best([b for b, t, s in classified if t == "date"], key=score_date)

    chain_texts = [b.text for b, t, _ in classified if t == "chain"]
    meta_blob = " ".join(b.text for b in blocks if b.roi_id == "top_left_meta")
    chain = resolve_chain_candidates(chain_texts + [meta_blob], parse_chain_from_text)

    if not chain.confident:
        chain = merge_chain(chain, parse_chain_from_text(filename))
    return build_result(chain, diameter, material, date)
```

---

## 10. 单测用例

| id | 输入 | 起 | 止 | 管径 | 管材 | 日期 |
|----|------|----|----|------|------|------|
| T1 | 单块 `w9-w10` | W9 | W10 | — | — | — |
| T2 | 文件名 `W9-W9-1` | W9 | W9-1 | — | — | — |
| T3 | 文件名 `W9-1-W9-2` | W9-1 | W9-2 | — | — | — |
| T4 | 文件名 `W11-污水监测井` | W11 | 污水监测井 | — | — | — |
| T5 | 单块 `DN500` | — | — | 500 | — | — |
| T6 | 单块 `球墨铸铁` | — | — | — | 球墨铸铁 | — |
| T7 | 单块 `2026/4/21` | — | — | — | — | 2026-04-21 |
| T8 | 三块乱序：`球墨铸铁`,`DN500`,`w9-w10` | W9 | W10 | 500 | 球墨铸铁 | — |
| T9 | 三块乱序：`DN500`,`w9-w10`,`球墨铸铁` | W9 | W10 | 500 | 球墨铸铁 | — |
| T10 | 日期在左上块 `2026/4/21`，链号在右下误 ROI 时 | — | — | — | — | 2026-04-21（全幅 date 扫描兜底） |

---

## 11. 相关文档

- [forms-appendix-d.md](forms-appendix-d.md)  
- [domain-model.md](domain-model.md)  
- [../api/openapi-outline.md](../api/openapi-outline.md)
