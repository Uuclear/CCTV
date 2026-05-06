# docxtpl 上下文清单（与代码同步）

后端 [`build_report_context`](../backend/app/services/report_build.py) 注入以下键，**CC01-2-base.docx** 中占位符须同名（区分大小写）。

| 键 | 类型 | 说明 |
|----|------|------|
| `project_name` | str | 工程名称 |
| `client_org` | str | 委托单位 |
| `project_code` | str | 工程编号 |
| `road_name` | str | 道路/工区 |
| `scope_text` | str | 检测范围概述 |
| `contact_name` | str | 联系人 |
| `contact_phone` | str | 电话 |
| `report_date` | str | 导出日 `YYYY-MM-DD` |
| `body` | str | 管段与缺陷多行文本 |

## 开发用最小模板

- 文件：`jinja_minimal.docx`  
- 用途：`pytest`、本地联调；真实交付可换 `CC01-2-base.docx`。

## 扩展循环数据（预留）

若模板使用 `{% for s in segments %}`，需在 `build_report_context` 内增加 `segments` 列表（字典或 Jinja-friendly 对象），并在本文件补充字段说明。
