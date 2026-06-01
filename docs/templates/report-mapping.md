# 业务模板字段映射

> 映射仓库内 **`公共通道雨水管CCTV委托单.doc`**、**`CC01-2  报告模板.docx`**、**`公共通道统计表.xlsx`** 与目标数据模型 / docxtpl 占位符。栏名以范本为准；若委托方表格有差异，在本表增行即可。

---

## 1. 委托单 → `Project` / `DetectionPlan`

来源：`公共通道雨水管CCTV委托单.doc`（二进制 .doc，栏位由范本提取）。

### 1.1 工程与委托信息

| 委托单栏名 | 实体.字段 | 类型 | 必填 | 说明 |
|------------|-----------|------|------|------|
| 项目名称 | `Project.name` | string | 是 | 例：世博文化公园地下空间 A4-1 地块文化商业设施 |
| 工程地点 / 工程地址 | `Project.site_address` | string | 是 | 例：济明路 988 弄 1 号、25 号 |
| 委托单位 | `Project.client_org` | string | 是 | |
| 建设单位 | `Project.build_org` | string | 否 | |
| 监理单位 | `Project.supervision_org` | string | 否 | |
| 设计单位 | `Project.design_org` | string | 否 | |
| 施工单位 | `Project.construction_org` | string | 否 | |
| 检测单位 | `Organization.name` / `Project.inspection_org` | string | 是 | |
| 现场负责人 | `Project.site_manager` | string | 否 | |
| 委托编号 | `Project.project_code` | string | 否 | 与报告编号可能不同 |
| 检测内容说明 | `Project.scope_text` | text | 是 | 例：新建雨水管道电视检测、现场抽检 |

### 1.2 检测工期（可并入方案或项目）

| 委托单栏名 | 字段 | 说明 |
|------------|------|------|
| 现场检测开始日期 | `Project.field_start_date` | |
| 现场检测结束日期 | `Project.field_end_date` | |
| 报告提交日期 | `Project.report_due_date` | 对应 11.1「完成后 5 个工作日」可计算提醒 |

### 1.3 管段清单（委托单附表）

委托单常含「设计管道信息表」「实际检测信息表」：

| 表栏名 | `Segment` 字段 |
|--------|----------------|
| 管道类型（雨水/污水/合流） | `pipe_system` |
| 材质 | `pipe_material` |
| 管段（起止井号） | `chain_start_label`, `chain_end_label` |
| 管径 mm | `diameter_mm` |
| 长度 m | `pipe_length_m` |

导入：首期支持 **Excel/CSV 批量创建管段**；委托单 .doc 手工录入或二期 OCR。

---

## 2. CC01-2 报告模板 → docxtpl

来源：`CC01-2  报告模板.docx`。

### 2.1 报告结构（目录）

| 章节 | 内容 | 数据来源 |
|------|------|----------|
| 1. 项目信息 | 项目表 | `Project` + 参建单位 |
| 2. 检测工程概况 | 依据、委托内容、工期 | `Project`, `DetectionPlan` |
| 3. 检测设备与作业流程 | 3.1 设备、3.2 流程示意图 | `Organization.equipment` |
| 4. 检测数据及评估结果 | 4.1 检测与建议、4.2 结构性、4.3 功能性 | 评估引擎 + 统计表 |
| 5. 管段缺陷及图片资料 | 逐管段 | `Segment`, `DefectRecord`, 媒体 |

### 2.2 封面与编号

| 范本文字 | 占位符建议 | 数据源 |
|----------|------------|--------|
| 报告编号 CC01-2 | `{{ report_no }}` | 规则生成或 `Project.report_no` |
| 工程编号 CC018-2 | `{{ project_code }}` | `Project.project_code` |
| 检测单位 | `{{ inspection_org }}` | |
| 报告日期 | `{{ report_date }}` | 导出日 `YYYY-MM-DD` |

### 2.3 项目信息表（第 1 章）

| 范本栏名 | docxtpl | 模型字段 |
|----------|---------|----------|
| 项目名称 | `{{ project_name }}` | `Project.name` |
| 工程地点 | `{{ site_address }}` | `Project.site_address` |
| 委托单位 | `{{ client_org }}` | `Project.client_org` |
| 建设单位 | `{{ build_org }}` | `Project.build_org` |
| 监理单位 | `{{ supervision_org }}` | |
| 设计单位 | `{{ design_org }}` | |
| 施工单位 | `{{ construction_org }}` | |
| 检测单位 | `{{ inspection_org }}` | |
| 现场负责人 | `{{ site_manager }}` | |

### 2.4 循环区（需 docxtpl 表格循环）

| 内容 | 循环变量 | 字段 |
|------|----------|------|
| 管段一览 | `{% for s in segments %}` | `chain_*`, `diameter_mm`, `pipe_length_m`, `ri`, `mi`, `ri_grade`, `mi_grade` |
| 缺陷表 | `{% for d in s.defects %}` | 附录 D 列 |
| 附录 K 统计 | `structural_stats` | 一级/二级/三级计数 |
| 附录 L 统计 | `functional_stats` | MI 分级计数 |

**策略**：固定版式区（封面、签字页）保留 Word 原样；仅 **表格循环区** 使用 docxtpl，避免页眉页脚错位。

### 2.5 模板落地步骤

1. 复制 `CC01-2  报告模板.docx` → `templates/report/CC01-2-base.docx`  
2. 在需自动填充处插入 `{{ variable }}` / `{% tr for %}`  
3. 配置 `REPORT_TEMPLATE_DOCX` 环境变量指向该文件  
4. 对照 [`../design/forms-appendix-d.md`](../design/forms-appendix-d.md) 核对缺陷列名  

---

## 3. 公共通道统计表.xlsx → 导出与对账

工作表 **CCTV**（管段汇总）：

| Excel 列 | 含义 | `Segment` / 评估 |
|----------|------|----------------|
| 序号 | 行号 | — |
| 管道 | 管道类型 | `pipe_system` |
| 管材 | 材质 | `pipe_material` |
| 管段 | 起止井号 | `chain_start_label`–`chain_end_label` |
| 管径（mm） | | `diameter_mm` |
| 长度（m） | | `pipe_length_m` |
| 缺陷 | 有/无 | 派生 |
| 修复指数 RI | | `Segment.ri` |
| 结构状况 | 一级/二级/三级 | `Segment.ri_grade` |
| 养护指数 MI | | `Segment.mi` |
| 功能状况 | 一级/二级/三级 | `Segment.mi_grade` |
| 备注 | | `Segment.note` |

工作表 **Sheet2**（缺陷明细卡片，按管段）：

| 列 | 含义 |
|----|------|
| 管道编号 | 管段标识 |
| 图号 | 附图序号 |
| 缺陷名称 / 缺陷等级 / 距离 / 时钟表示 / 备注 | 与附录 D 行一致 |

**软件导出**：`GET /api/v1/projects/{id}/export/statistics.xlsx` 列顺序与上表一致，便于与业主 Excel 对账。

---

## 4. 视频样例目录 `视频/`

| 用途 | 说明 |
|------|------|
| E2E 测试 | 命名惯例、看板叠加、时长 |
| OCR 训练 | 井号 `Y1A-Y1B` 等模式 |
| 性能 | 大文件本地路径挂接（桌面端） |

建议管段文件命名：`{工程编号}_{起点井}-{终点井}_{短哈希}.mp4`。

---

## 5. 占位符总表（首期最小集）

| docxtpl | 来源 |
|---------|------|
| `project_name`, `site_address`, `client_org`, `project_code`, `report_no`, `report_date` | Project |
| `inspection_org`, `site_manager` | Project / Organization |
| `field_start_date`, `field_end_date` | Project |
| `body` | 纯文本汇总（无循环时的降级） |
| `segments` | 列表（推荐循环） |
| `structural_stats`, `functional_stats` | 附录 K/L |

---

## 相关文档

- [../design/forms-appendix-d.md](../design/forms-appendix-d.md)  
- [../CCTV-PM-SDD.md](../CCTV-PM-SDD.md) §11 报告与导出
