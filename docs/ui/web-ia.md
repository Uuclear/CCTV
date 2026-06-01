# Web 信息架构与页面规格

> React + TypeScript + Vite SPA。设计 token：卡片式布局、圆角、柔和中性色、数据密集型表格（不绑定特定 UI 库）。

---

## 1. 站点地图

```text
/                          → 重定向 /projects
/projects                  → 项目列表
/projects/new              → 新建委托
/projects/:id              → 项目概览（Tab 容器）
/projects/:id/plan         → 检测方案
/projects/:id/workbench    → 检测工作台（核心）
/projects/:id/reports      → 报告与导出
/projects/:id/settings     → 工程参数、K 默认值、权限
/login                     → Web 登录（局域网）
```

---

## 2. 项目列表 `/projects`

| 元素 | 行为 |
|------|------|
| 表格列 | 名称、委托单位、编号、状态、管段数、交付日、操作 |
| 筛选 | 状态、日期、关键词 |
| 操作 | 进入工作台、导出、删除（管理员） |
| 主按钮 | 新建项目 |

---

## 3. 项目工作台 `/projects/:id/workbench`

三栏布局（宽屏）；窄屏折叠为 Tab：**管段 | 视频 | 缺陷**。

### 3.1 左栏 — 管段列表（25%）

- 可排序表格：井号区间、管径、长度、RI/MI 等级色标  
- 按钮：新增管段、批量导入 CSV、刷新评估  
- 选中行加载中栏与右栏  

### 3.2 中栏 — 视频与看板（45%）

| 组件 | 说明 |
|------|------|
| 看板信息条 | 编辑路名、井号、管径、方向、日期（附录 D 表头） |
| 视频播放器 | HTML5；时间轴刻度；标记缺陷点 |
| 工具条 | 上传视频、抽帧预览、OCR 建议、电缆距离标定（二期） |
| 预览图 | `GET /media/...` 显示 OCR 用帧 |

**交互**：播放中按 `M` 在当前时间插入缺陷行（预填 `video_start_s`）。

### 3.3 右栏 — 附录 D 缺陷表 + 评估（30%）

| 组件 | 说明 |
|------|------|
| 缺陷网格 | 列同 [forms-appendix-d.md](../design/forms-appendix-d.md)；内联编辑 |
| 缺陷录入表单 | 代码下拉（结构/功能分组）、等级、钟点、距离 |
| 评估卡片 | RI、MI、等级、建议；展开显示 S/F/Y/G（高级） |
| 完整性提示 | RS/ZZ 时黄色横幅 |

---

## 4. 检测方案 `/projects/:id/plan`

- 多段 textarea / 富文本（简易 Markdown）对应 DetectionPlan 各节  
- 保存版本号；与 5.3 节目录一致的分节标题  

---

## 5. 报告 `/projects/:id/reports`

| 区块 | 内容 |
|------|------|
| 模板选择 | CC01-2-base（默认） |
| 生成 | Word、PDF 按钮；进度条 |
| 附录 K/L 预览 | 表格只读 |
| 下载区 | 成果包 zip、统计 xlsx |
| 审核 | 提交审核 / 批准（reviewer 角色） |

---

## 6. 组件清单

| 组件 | 用途 |
|------|------|
| `SegmentTable` | 左栏 |
| `VideoPanel` | 中栏 |
| `DefectGrid` | 附录 D 表 |
| `ClockPicker` | 4 位钟点（圆盘，附录 G） |
| `GradeBadge` | 一/二/三级色 |
| `EvaluationDetail` | S/F/Y/G 展开 |
| `ConfirmDialog` | OCR 改名确认 |

---

## 7. 角色与可见性

| 页面/操作 | admin | inspector | reviewer | readonly |
|-----------|-------|-----------|----------|----------|
| 新建项目 | ✓ | ✓ | — | — |
| 缺陷编辑 | ✓ | ✓ | — | — |
| 报告批准 | ✓ | — | ✓ | — |
| 导出 | ✓ | ✓ | ✓ | ✓ |

---

## 8. 无障碍与国际化

- 首期中文界面；缺陷代码显示中文名 + 代码  
- 表格支持键盘 Tab 与 Enter 提交  

---

## 相关文档

- [desktop-gui.md](desktop-gui.md)  
- [../CCTV-PM-SDD.md](../CCTV-PM-SDD.md) §10
