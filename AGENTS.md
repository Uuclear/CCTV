# AGENTS.md — 导航入口

本仓库：排水管道 CCTV 检测报告系统（DB31/T 444-2022 规则需以正式标准数字化）。新进 Agent **先读本文件**，再按需下钻。

## 冷启动顺序（每个新会话）

1. 读 [`claude-progress.txt`](claude-progress.txt) — 上轮交接与风险。
2. 读 [`feature_list.json`](feature_list.json) — **只改 `passes`，勿改 `steps` 语义**。
3. 运行 [`init.ps1`](init.ps1)（Windows）或 [`init.sh`](init.sh)（Unix）装依赖。
4. 按 `feature_list.json` 选 **一条** `passes: false` 的最高优先级项实现；测完再置 `true`。

## 目录

| 路径 | 说明 |
|------|------|
| [`backend/`](backend/) | FastAPI、SQLite/PostgreSQL、视频/OCR/报告逻辑 |
| [`frontend/`](frontend/) | React + Vite + TypeScript，视觉参考 animal-island-ui（自有 token，不默认装该 npm 包） |
| [`config/standards/db31t444-2022/`](config/standards/db31t444-2022/) | 标准规则包（版本化）；**占位规则非验收依据** |
| [`templates/`](templates/) | 委托单字段说明、报告 docx 母版（从根目录范本复制） |
| [`docs/harness.md`](docs/harness.md) | 与 Anthropic/OpenAI 文章对齐的 harness 约定摘要 |

## 运行（开发）

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

```powershell
cd frontend
npm run dev
```

API 文档：<http://127.0.0.1:8000/docs>

## 依赖

- **ffmpeg / ffprobe**：须安装并在 `PATH` 中，用于 `POST /api/segments/{id}/extract-preview` 真机抽帧（单元测试已 mock，可不装也能跑 `pytest`）。
- 静态访问预览图：`GET /media/<相对于 data/files 的路径>`（与 `preview_frame_relpath` 拼接，例如 `/media/previews/1/2/xxx.png`）。

## 合规提醒

- `config/standards/` 中 **placeholder** 仅打通流水线；正式验收前必须对照 **DB31/T 444-2022 正文与附录** 重写。
