# Tauri 桌面壳

- **开发**：在 [`frontend/`](../frontend/) 下执行 `npm run tauri:dev`（需 [Rust](https://rustup.rs/)）。会先由 [`scripts/tauri-dev-bootstrap.mjs`](../scripts/tauri-dev-bootstrap.mjs) 在必要时拉起 `uvicorn`，再阻塞运行 `vite`，供 WebView 加载 `http://127.0.0.1:5173`。
- **仍可用**：[`desktop/run-dev.ps1`](../desktop/run-dev.ps1) 作为仅双进程浏览器方案。
- **正式包**：当前未把 Python 打进安装包；发布需另做 **sidecar / 安装指引** 或内嵌后端。
- **图标**：若需重生成，在仓库根已装好后端 venv 的前提下可执行：`pip install pillow`（一次性），在 `frontend/` 放 `icon-1024.png`，再 `npx tauri icon icon-1024.png`。
