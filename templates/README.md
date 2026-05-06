# 模板目录

| 路径 | 说明 |
|------|------|
| [`commission_fields.md`](commission_fields.md) | 委托单栏 ↔ `Project` ↔ docxtpl 占位符 |
| [`report/jinja_minimal.docx`](report/jinja_minimal.docx) | 默认报告母版（docxtpl） |
| [`report/docxtpl-context.md`](report/docxtpl-context.md) | 与 `build_report_context` 同步的变量清单 |

将根目录 **`CC01-2  报告模板.docx`** 复制为 `report/CC01-2-base.docx` 后，在 Word 中按 `commission_fields.md` 插入 `{{ }}` 占位符；切换模板见该文档「CC01-2 范本合并步骤」。
