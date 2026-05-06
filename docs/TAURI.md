# Tauri 桌面壳（规划）

当前用 **[`desktop/run-dev.ps1`](../desktop/run-dev.ps1)** 在 Windows 上同时启动后端与 Vite，并用 Playwright 做 UI 冒烟。

若需 **原生 Tauri 窗口**，建议在 `frontend/` 下初始化 `src-tauri`（需安装 [Rust](https://rustup.rs/)），`beforeDevCommand` 指向 `npm run dev`，正式包内再考虑嵌入或 sidecar 启动 Python 后端。
