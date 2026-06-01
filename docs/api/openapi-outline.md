# REST API 概要（OpenAPI 提纲）

> 版本：`/api/v1`。正式 `openapi.yaml` 可在实施阶段由 FastAPI 自动生成并与此文同步。

**Base URL**：`http://127.0.0.1:8000`（开发）

**认证（首期 Web）**：`Authorization: Bearer <JWT>`；桌面单机模式可 `X-Local-Mode: true` 跳过（可配置）。

**通用错误**：`{ "detail": string | object }`；422 校验错误含字段路径。

---

## 1. 健康与元数据

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | `{ "status": "ok" }` |
| GET | `/api/v1/standards/active` | 当前 `rules_version`、缺陷码表摘要 |

---

## 2. 项目 Project

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/projects` | 列表；query: `status`, `q`, `page`, `page_size` |
| POST | `/api/v1/projects` | 创建 |
| GET | `/api/v1/projects/{id}` | 详情 |
| PATCH | `/api/v1/projects/{id}` | 更新 |
| DELETE | `/api/v1/projects/{id}` | 删除（级联管段） |
| GET | `/api/v1/projects/{id}/plan` | 检测方案 |
| PUT | `/api/v1/projects/{id}/plan` | 保存方案 |
| POST | `/api/v1/projects/{id}/status` | `{ "status": "fieldwork" }` 状态流转 |

### ProjectCreate / ProjectOut（摘要）

```json
{
  "name": "string",
  "project_code": "string",
  "client_org": "string",
  "site_address": "string",
  "scope_text": "string",
  "inspection_org": "string",
  "k_value_default": 3
}
```

---

## 3. 管段 Segment

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/projects/{pid}/segments` | 列表 |
| POST | `/api/v1/projects/{pid}/segments` | 创建；body 含 `video_path` 可选 |
| GET | `/api/v1/segments/{id}` | 详情含评估 |
| PATCH | `/api/v1/segments/{id}` | 看板字段、K/E/T、井号 |
| DELETE | `/api/v1/segments/{id}` | |
| POST | `/api/v1/segments/{id}/video` | multipart 上传或 `{ "local_path": "..." }` 桌面注册 |
| POST | `/api/v1/segments/{id}/media/extract-preview` | ffmpeg 抽帧 → `preview_frame_relpath` |
| POST | `/api/v1/segments/{id}/ocr-preview` | OCR 建议井号/管段名 |
| POST | `/api/v1/segments/{id}/evaluate` | 重算 RI/MI |
| GET | `/api/v1/segments/{id}/inspection-record` | 附录 D JSON |
| PUT | `/api/v1/segments/{id}/inspection-record` | 批量保存表体行 |

---

## 4. 缺陷 Defect

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/segments/{sid}/defects` | |
| POST | `/api/v1/segments/{sid}/defects` | 单条 |
| PATCH | `/api/v1/defects/{id}` | |
| DELETE | `/api/v1/defects/{id}` | |
| POST | `/api/v1/segments/{sid}/defects/bulk` | 表格粘贴导入 |

### DefectCreate

```json
{
  "defect_code": "PL",
  "kind": "structural",
  "level": 2,
  "distance_m": 12.5,
  "clock_position": "0309",
  "longitudinal_length_m": 1.0,
  "video_start_s": 120.0,
  "video_end_s": 125.0,
  "note": ""
}
```

---

## 5. 报告与导出

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/v1/projects/{id}/reports/docx` | 生成 Word；返回 `{ "path", "download_url" }` |
| POST | `/api/v1/projects/{id}/reports/pdf` | LibreOffice 转 PDF |
| GET | `/api/v1/projects/{id}/reports` | 历史报告列表 |
| GET | `/api/v1/projects/{id}/export/statistics.xlsx` | 对齐公共通道统计表 |
| GET | `/api/v1/projects/{id}/export/package.zip` | docx+pdf+xlsx+记录表 JSON |
| GET | `/api/v1/projects/{id}/summary/structural` | 附录 K 数据 |
| GET | `/api/v1/projects/{id}/summary/functional` | 附录 L 数据 |

---

## 6. 媒体

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/media/{path}` | 静态文件；path 为相对 `data/files` |

---

## 7. 审计（首期可选）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/projects/{id}/audit-logs` | 缺陷/评估变更 |

---

## 8. WebSocket（二期可选）

| 路径 | 说明 |
|------|------|
| `/ws/v1/jobs/{job_id}` | 抽帧/OCR/报告生成进度 |

首期：轮询 `GET /api/v1/jobs/{id}` 或同步小任务。

---

## 9. 与功能需求追溯

| FR | 主要端点 |
|----|----------|
| FR-01 | `/projects` |
| FR-02 | `/projects/{id}/plan` |
| FR-03–04 | `/segments`, `/media/extract-preview`, `/ocr-preview` |
| FR-05 | `/defects`, `/inspection-record` |
| FR-06 | `/segments/{id}/evaluate` |
| FR-07 | `/summary/structural`, `/export/statistics.xlsx` |
| FR-08–09 | `/reports/docx`, `/reports/pdf`, `/export/package.zip` |
| FR-10 | `/audit-logs` |

---

## 相关文档

- [../CCTV-PM-SDD.md](../CCTV-PM-SDD.md)  
- [../design/domain-model.md](../design/domain-model.md)
