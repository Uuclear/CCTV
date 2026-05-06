# Tauri 桌面壳

## Linux / WSL 系统依赖（避免 OpenSSL / WebView 编译失败）

若在 **`npm run tauri:dev`** 或 **`cargo build`** 时出现 **`could not find openssl development headers`**（或 `openssl-sys` / `pkg-config` 相关报错），请先安装 **OpenSSL 开发包** 与 **pkg-config**，并补齐 Tauri 官方列出的 GTK / WebKit 依赖。以 **Debian / Ubuntu / WSL2** 为例：

```bash
sudo apt update
sudo apt install -y build-essential curl wget file pkg-config libssl-dev \
  libwebkit2gtk-4.1-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
```

装好后在 `frontend/` 重试 `npm run tauri:dev`。其他发行版名称不同（如 Fedora 的 `openssl-devel`、`pkgconf-pkg-config`），可按 [Tauri 前置要求](https://v2.tauri.app/start/prerequisites/) 对照安装。

- **开发**：在 [`frontend/`](../frontend/) 下执行 `npm run tauri:dev`（需 [Rust](https://rustup.rs/)）。会先由 [`scripts/tauri-dev-bootstrap.mjs`](../scripts/tauri-dev-bootstrap.mjs) 在必要时拉起 `uvicorn`，再阻塞运行 `vite`，供 WebView 加载 `http://127.0.0.1:5173`。
- **仍可用**：[`desktop/run-dev.ps1`](../desktop/run-dev.ps1) 作为仅双进程浏览器方案。
- **正式包**：当前未把 Python 打进安装包；发布需另做 **sidecar / 安装指引** 或内嵌后端。
- **图标**：若需重生成，在仓库根已装好后端 venv 的前提下可执行：`pip install pillow`（一次性），在 `frontend/` 放 `icon-1024.png`，再 `npx tauri icon icon-1024.png`。
