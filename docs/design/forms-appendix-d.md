# 附录 D — 电视检测记录表（数字化规格）

> 依据 DB31/T 444-2022 **附录 D（规范性）** 及第 7 章电视检测要求。对应软件模块：**管段看板信息** + **缺陷记录行（DefectRecord）** + **导出/打印版式**。

---

## 1. 表头信息（管段级 Segment）

每条管段一份记录表头，字段与规程 7.2.3、7.2.5、附录 D 对齐。

| 字段 ID | 中文名 | 类型 | 必填 | 规程依据 |
|---------|--------|------|------|----------|
| `road_segment` | 路名（路段） | string | 是 | 附录 D |
| `address` | 地址 | string | 否 | 表 D.1 |
| `segment_code` | 管段编号 | string | 是 | 附录 D |
| `start_manhole` | 起点编号 | string | 是 | 附录 D |
| `end_manhole` | 终点编号 | string | 是 | 附录 D |
| `pipe_material` | 管道材质 | enum/string | 是 | 附录 D |
| `diameter_mm` | 管径 | number | 是 | 附录 D |
| `pipe_length_m` | 管道长度 | number | 是 | 附录 D |
| `inspected_length_m` | 检测长度 | number | 是 | 附录 D |
| `invert_elevation` | 管底标高 | string/number | 否 | 附录 D |
| `joint_type` | 接口型式 | string | 否 | 附录 D |
| `plugging_status` | 封堵情况 | string | 否 | 附录 D |
| `inspection_direction` | 检测方向 | enum | 是 | 上游→下游 / 下游→上游 |
| `weather` | 天气 | string | 否 | 附录 D |
| `instrument_model` | 仪器型号 | string | 否 | 附录 D |
| `video_disc_no` | 视频/光盘编号 | string | 否 | 10.2.2 |
| `gps_location` | 定位信息 | string/GeoJSON | 否 | 4.1、6.1.1、7.2.3 |
| `inspection_company` | 检测单位 | string | 是 | 看板 附录 B |
| `inspected_at` | 检测日期 | date | 是 | 附录 D |
| `inspector_name` | 检测者 | string | 是 | 表尾 |
| `reviewer_name` | 校核者 | string | 否 | 表尾 |
| `page_no` | 第 页/共 页 | string | 导出时生成 | 附录 D |

**看板（7.2.3）**：检测开始前须录入或拍摄看板；软件提供「看板信息」表单，并可导出为视频片头配置 JSON。

---

## 2. 明细行（DefectRecord / 附录 D 表体）

每行对应一处观测点（缺陷、特殊结构或操作状态）。

### 2.1 通用列

| 字段 ID | 中文名 | 类型 | 说明 |
|---------|--------|------|------|
| `video_index` | 视频计数 | string/int | 视频内序号 |
| `photo_id` | 照片编号 | string | 与缺陷分布图照片编号一致 |
| `distance_m` | 距离 m | number(1) | 自起始井起算，电缆计数或数字化距离 |
| `clock_position` | 时钟表示 | string | 顺时针钟点起止，如 `0309`；见附录 G |
| `remark` | 备注 | text | 含支管资料、百分比等 |

### 2.2 结构性缺陷等级列（空或 1–4）

| 列代码 | 名称 |
|--------|------|
| `PL` | 破裂 |
| `BX` | 变形 |
| `CW` | 错位 |
| `TJ` | 脱节 |
| `SL` | 渗漏 |
| `FS` | 腐蚀 |
| `JQ` | 胶圈脱落 |
| `AJ` | 支管暗接 |
| `QR` | 异物侵入 |

每行 **至多一个** 结构性代码填等级（或纵向缺陷用 KS/JS 配对多行表达）。

### 2.3 功能性缺陷等级列（空或 1–3）

| 列代码 | 名称 |
|--------|------|
| `CJ` | 沉积 |
| `JG` | 结垢 |
| `ZW` | 障碍物 |
| `SG` | 树根 |
| `WS` | 洼水（可记百分比） |
| `BT` | 坝头 |
| `FZ` | 浮渣（不参与 MI） |

### 2.4 其他代码列

| 字段 ID | 说明 | 来源 |
|---------|------|------|
| `other_defect` | 其他缺陷() | 自定义代码 |
| `special_structure` | 特殊结构 | 表 9：XF, BJ, Y, W, H, MJ, JM, YK, DH, PH |
| `operation_status` | 操作状态 | 表 11：KS××, JS××, RS, ZZ |

**纵向缺陷 > 1 m**：使用 `KS01`/`JS01` 成对行标记起止距离，引擎用起止差作为 \(L_i\)。

---

## 3. JSON Schema（逻辑模型摘要）

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "CctvInspectionRecordD",
  "type": "object",
  "required": ["header", "rows"],
  "properties": {
    "header": {
      "type": "object",
      "required": ["segment_code", "start_manhole", "end_manhole", "pipe_length_m", "inspection_direction"]
    },
    "rows": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["distance_m"],
        "properties": {
          "distance_m": { "type": "number", "minimum": 0 },
          "structural": { "type": "object", "additionalProperties": { "type": "integer", "minimum": 1, "maximum": 4 } },
          "functional": { "type": "object", "additionalProperties": { "type": ["integer", "string"] } },
          "clock_position": { "type": "string", "pattern": "^[0-9]{4}$" },
          "media_clip": { "type": "object", "properties": { "video_start_s": { "type": "number" }, "video_end_s": { "type": "number" } } }
        }
      }
    }
  }
}
```

完整 JSON Schema 文件建议落地：`config/schemas/appendix-d-record.schema.json`（实施阶段）。

---

## 4. UI 映射

| UI 区域 | 行为 |
|---------|------|
| 管段属性面板 | 编辑 §1 表头 |
| 缺陷数据网格 | 可编辑表格式录入 §2 列；支持从视频时间戳插入行 |
| 视频时间轴 | 选中时刻 → 预填 `distance_m`（若已标定电缆计数曲线） |
| 钟点选择器 | 图形化圆盘，输出 4 位时钟串（附录 G） |
| 校验 | BX 仅柔性管；FZ 行提示「不计入 MI」；ZZ/RS 提示评估完整性 |

---

## 5. 导出

| 格式 | 用途 |
|------|------|
| `.xlsx` | 版式贴近附录 D，便于打印签字 |
| `.json` | 系统交换、备份 |
| PDF | 随成果包（由 xlsx 或 docx 模板生成） |

---

## 6. 与第 7 章检测流程的对应

| 规程要求 | 软件 |
|----------|------|
| 7.1.5 检测后按附录 C 判读并填附录 D | 判读向导链至附录 C 词条（二期图库） |
| 7.2.4 电缆计数归零 | 管段属性 `counter_zero_at` |
| 7.2.8 缺陷处静止 ≥5 s | `media_clip` 最短 5 s 校验（警告） |
| 7.1.4 中止 RS/ZZ | `operation_status` 行 + 管段 `assessment_complete=false` |

---

## 相关文档

- [evaluation-engine.md](evaluation-engine.md)  
- [../templates/report-mapping.md](../templates/report-mapping.md)
