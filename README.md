# CCTV 排水管道检测项目管理系统

面向排水管道 **电视检测（CCTV）** 的工程级工作台：工程立项 → 批量视频导入与水印 OCR → 管段台账 → 视频缺陷标注 → **DB31/T 444-2022** RI/MI 自动评定 → Word 报告与 Excel 统计表导出。

依据上海地方标准 [**DB31/T 444-2022**《排水管道电视和声纳检测评估技术规程》](docs/CCTV-PM-SDD.md)。

在线仓库：[github.com/Uuclear/CCTV](https://github.com/Uuclear/CCTV)

---

## 功能概览

| 模块 | 说明 |
|------|------|
| 工程工作台 | 委托信息、管段管线表、内联编辑 |
| 批量导入 | 先建表再批量 OCR；可暂停 / 继续 / 终止；重复管段覆盖或忽略 |
| 水印解析 | 起止井号、管径、管材、检测日期（RapidOCR + 规则引擎） |
| 缺陷标注 | 视频暂停打点，标准缺陷目录（结构 / 功能） |
| 评定 | RI/MI、结构 / 功能状况等级（一级 / 二级 / 三级） |
| 导出 | Word 报告（docxtpl）、管段统计表 xlsx（对齐 `公共通道统计表.xlsx`） |
| 桌面壳 | Tauri 2（可选，开发时加载 Vite） |

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Python 3.11+、FastAPI、SQLAlchemy 2、SQLite（开发） |
| 前端 | React 18、TypeScript、Vite |
| OCR | rapidocr-onnxruntime |
| 视频 | ffmpeg / ffprobe |
| 报告 | python-docx、docxtpl、openpyxl |

---

## 目录结构

```
backend/           FastAPI 服务、规则包、单测
frontend/          React 工作台 UI
config/standards/  DB31/T444-2022 规则 YAML
desktop/           run-dev.ps1 一键启动脚本
docs/              产品说明、SDD、设计文档
scripts/           依赖安装、E2E
templates/         报告 Jinja 母版等
data/              运行时 SQLite、上传文件（git 忽略）
```

开发导航见 [AGENTS.md](AGENTS.md)。

---

## 环境要求

- **Windows 10/11**（当前脚本以 PowerShell 为主；Linux/macOS 可参考命令手动执行）
- **Python 3.11+**
- **Node.js 18+**、npm
- **ffmpeg**、**ffprobe**（PATH 可用；或运行 `scripts/install-system-deps.ps1`）

---

## 快速开始（Windows）

### 1. 初始化依赖

在仓库根目录：

```powershell
.\init.ps1
```

将创建 `backend\.venv`、安装 Python/npm 依赖，并尝试安装 OCR 与 ffmpeg 相关组件。

### 2. 启动前后端

```powershell
.\desktop\run-dev.ps1
```

- 后端：<http://127.0.0.1:8000>  
- 前端：<http://127.0.0.1:5173>（Vite 代理 `/api`、`/media` 到 8000）

脚本会轮询 `/health`，并自检 `缺陷目录 >= 16` 项。

### 3. 手动启动（可选）

**后端：**

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**前端：**

```powershell
cd frontend
npm run dev
```

### 4. 自检

浏览器打开应返回 JSON：

- <http://127.0.0.1:8000/api/imports/ocr-status>
- <http://127.0.0.1:5173/api/imports/ocr-status>

---

## 业务模板（本地放置，默认不入库）

| 文件 | 用途 |
|------|------|
| `公共通道统计表.xlsx` | 统计表导出模板（放仓库根或 `templates/`） |
| `CC01-2  报告模板.docx` | 报告母版 |
| `视频/` | 样例 mp4（已在 `.gitignore` 中排除） |

---

## 测试

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest -q
```

前端 E2E（需 Playwright 浏览器）见 `scripts/e2e.ps1`。

---

## 常见问题

| 现象 | 处理 |
|------|------|
| 前端 `Failed to fetch` | 确认后端 8000 已启动；页面必须用 **5173**，不要直接打开 `dist/index.html` |
| `upload-stage-one` / `export/statistics.xlsx` 404 | 停止旧 uvicorn，重新 `run-dev.ps1` |
| OCR 很慢 | 单文件约 30～60s，批量 OCR 勿重复点击 |
| 状况列显示 `0` | 重启后端并刷新；等级应为「一级 / 二级 / 三级」 |

---

## 文档

- [docs/PRODUCT.md](docs/PRODUCT.md) — 产品范围  
- [docs/CCTV-PM-SDD.md](docs/CCTV-PM-SDD.md) — 软件开发主文档  
- [docs/design/evaluation-engine.md](docs/design/evaluation-engine.md) — RI/MI 算法  
- [docs/api/openapi-outline.md](docs/api/openapi-outline.md) — API 提纲  

---

## 许可证

未指定许可证时默认保留所有权利；如需开源请补充 `LICENSE` 文件。

---

## 与历史仓库说明

本仓库由本地 **CCTV-report** 工程推送至 [Uuclear/CCTV](https://github.com/Uuclear/CCTV)，实现栈为 FastAPI + React（非原仓库 README 中的 Vue/PostgreSQL 脚手架）。以本 README 与 `docs/` 为准。
