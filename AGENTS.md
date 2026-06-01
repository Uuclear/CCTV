# AGENTS.md — 导航入口

本仓库：**CCTV 检测项目管理系统** 产品与开发文档（DB31/T 444-2022，首期管道电视检测）。**实施代码前请先读文档，勿仅凭 MinerU 摘要写评估逻辑。**

## 合规（必读）

- 规程参考：[MinerU_markdown_DB31-T_444-2022排水管道电视和声呐检测评估技术规程_2055030793924440064.md](MinerU_markdown_DB31-T_444-2022排水管道电视和声呐检测评估技术规程_2055030793924440064.md)  
- **验收依据**：标准正式 PDF；`rules_version` 须与算例单测一并更新。

## 文档地图

| 路径 | 说明 |
|------|------|
| [docs/PRODUCT.md](docs/PRODUCT.md) | 产品愿景、角色、首期/二期边界 |
| [docs/CCTV-PM-SDD.md](docs/CCTV-PM-SDD.md) | **主开发文档（SDD）** |
| [docs/design/evaluation-engine.md](docs/design/evaluation-engine.md) | RI/MI、S/F/Y/G、权重表、算例 |
| [docs/design/forms-appendix-d.md](docs/design/forms-appendix-d.md) | 电视检测记录表 → UI/Schema |
| [docs/design/watermark-ocr-extraction.md](docs/design/watermark-ocr-extraction.md) | 批量视频水印 OCR：起止井号/管径/管材/日期解析规则 |
| [docs/design/domain-model.md](docs/design/domain-model.md) | 实体、状态机 |
| [docs/api/openapi-outline.md](docs/api/openapi-outline.md) | REST 提纲 |
| [docs/ui/web-ia.md](docs/ui/web-ia.md) | Web 页面与组件 |
| [docs/ui/desktop-gui.md](docs/ui/desktop-gui.md) | Tauri 桌面壳 |
| [docs/templates/report-mapping.md](docs/templates/report-mapping.md) | 委托单 / CC01-2 / xlsx 字段映射 |

## 业务模板（仓库根目录）

| 文件 | 用途 |
|------|------|
| `公共通道雨水管CCTV委托单.doc` | 委托字段 |
| `CC01-2  报告模板.docx` | 报告母版 |
| `公共通道统计表.xlsx` | 管段统计导出对齐 |
| `视频/` | 样例视频 |

## 建议实施顺序

1. `config/standards/db31t444-2022/` 规则包 + TC-EVAL 单测  
2. FastAPI 领域模型与 API（见 openapi-outline）  
3. Web 工作台 → 媒体/OCR → 报告 → Tauri  

## 首期不做

声呐、检查井、GIS 上报、QV/无人机/数字化电视 — 见 SDD §14。
