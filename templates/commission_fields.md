# 委托单字段 ↔ 数据模型 ↔ 报告 docx 占位符

> 范本来源：仓库根目录若存在 **`公共通道雨水管CCTV委托单.doc`**（或其它委托单），以**实际表格栏名为准**；下表为**典型** CCTV/检测委托栏与当前后端 `Project` 的映射。栏名不一致时在本表增行即可，必要时扩展 [`backend/app/models.py`](../backend/app/models.py) 与 [`backend/app/schemas.py`](../backend/app/schemas.py)。

## `Project`（工程 / 委托）

| 委托单常见栏名（示例） | `Project` 字段 | OpenAPI / JSON 键 | docxtpl 占位符（与 [`report_build.build_report_context`](../backend/app/services/report_build.py) 一致） |
|------------------------|----------------|-------------------|--------------------------------------------------------------------------------------------------------|
| 工程名称 / 项目名称 | `name` | `name` | `{{ project_name }}` |
| 委托单位 / 建设单位 | `client_org` | `client_org` | `{{ client_org }}` |
| 工程编号 / 委托编号 | `project_code` | `project_code` | `{{ project_code }}` |
| 路名 / 工区 / 工程位置 | `road_name` | `road_name` | `{{ road_name }}` |
| 检测范围、内容说明 | `scope_text` | `scope_text` | `{{ scope_text }}` |
| 联系人 | `contact_name` | `contact_name` | `{{ contact_name }}` |
| 联系电话 | `contact_phone` | `contact_phone` | `{{ contact_phone }}` |
| — | `created_at`（系统） | `created_at` | （报告模板可按需后续增加 `{{ created_at }}`） |

## 报告专用（非单列字段）

| 说明 | docxtpl |
|------|---------|
| 报告日期（导出当日） | `{{ report_date }}`（`YYYY-MM-DD`） |
| 管段与缺陷汇总正文（多行纯文本） | `{{ body }}` |

## 管段 / 缺陷（当前进 `body` 文本，未逐字段占位）

- **Segment**：`chain_start_label`、`chain_end_label`、`ri`、`mi`、`ri_grade`、`mi_grade` 等已写入 `{{ body }}` 段落。
- 若 CC01-2 需**表格逐行**渲染，请在模板中使用 [docxtpl 循环](https://docxtpl.readthedocs.io/)，并在后端扩展 `build_report_context` 传入 `segments` 列表（后续迭代）。

## CC01-2 范本合并步骤（摘要）

详见同目录 [`report/docxtpl-context.md`](report/docxtpl-context.md)。

1. 将 **`CC01-2  报告模板.docx`** 复制为 `templates/report/CC01-2-base.docx`。  
2. 在 Word 中把需自动填写的单元格改为与上表一致的 `{{ 变量名 }}`。  
3. 将 `settings.report_template_docx`（环境变量 `REPORT_TEMPLATE_DOCX` 或 `.env`）指向该文件，或在 [`backend/app/config.py`](../backend/app/config.py) 中临时改默认路径。  

当前默认模板：[`templates/report/jinja_minimal.docx`](report/jinja_minimal.docx)（含上述占位符，用于开发与 CI）。
