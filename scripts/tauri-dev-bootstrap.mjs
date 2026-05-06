/**
 * Tauri beforeDevCommand: ensure API is up, then run Vite (blocking, stdio inherited).
 * Run from repo root context with: node ../scripts/tauri-dev-bootstrap.mjs (cwd = frontend).
 */
import { spawn } from "node:child_process";
import { access } from "node:fs/promises";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.dirname(__dirname);
const backend = path.join(root, "backend");
const frontend = path.join(root, "frontend");
const venvPython =
  process.platform === "win32"
    ? path.join(backend, ".venv", "Scripts", "python.exe")
    : path.join(backend, ".venv", "bin", "python");

function checkHealth() {
  return new Promise((resolve) => {
    const req = http.get("http://127.0.0.1:8000/health", (res) => {
      resolve(res.statusCode === 200);
    });
    req.on("error", () => resolve(false));
    req.setTimeout(2000, () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitForHealthy(seconds) {
  for (let i = 0; i < seconds; i++) {
    if (await checkHealth()) return true;
    await new Promise((r) => setTimeout(r, 1000));
  }
  return checkHealth();
}

if (!(await checkHealth())) {
  try {
    await access(venvPython);
  } catch {
    console.error(`[tauri-dev-bootstrap] Missing venv: ${venvPython} — run init.ps1 / init.sh.`);
    process.exit(1);
  }
  console.log("[tauri-dev-bootstrap] Starting uvicorn on 127.0.0.1:8000...");
  const uvicorn = spawn(
    venvPython,
    ["-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
    { cwd: backend, stdio: "ignore", detached: true, windowsHide: true },
  );
  uvicorn.unref();
  if (!(await waitForHealthy(90))) {
    console.error("[tauri-dev-bootstrap] Backend did not become healthy at /health");
    process.exit(1);
  }
  console.log("[tauri-dev-bootstrap] Backend is up.");
} else {
  console.log("[tauri-dev-bootstrap] Backend already running.");
}

const vite = spawn(
  "npm",
  ["run", "dev", "--", "--host", "127.0.0.1", "--port", "5173", "--strictPort"],
  { cwd: frontend, stdio: "inherit", shell: true },
);

vite.on("exit", (code, signal) => {
  if (signal) process.kill(process.pid, signal);
  process.exit(code ?? 1);
});
