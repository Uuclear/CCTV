# Harness 约定（本仓库）

与 [long-running-agent-harness](.cursor/rules/long-running-agent-harness.mdc) 对齐的最低集：

- **`init.ps1` / `init.sh`**：一键安装后端 venv + 前端 npm。
- **`feature_list.json`**：可执行步骤 + `passes`；禁止随意删改 `steps`。
- **`claude-progress.txt`**：轮班日志，合并前更新。
- **`AGENTS.md`**：本 TOC；不把百科全书塞进单文件。

呈现大量结构化报告数据时，优先 **Cursor Canvas**（见仓库规则）。
