export async function readApiError(response: Response): Promise<string> {
  const text = await response.text();
  if (!text) {
    return response.statusText || `HTTP ${response.status}`;
  }
  try {
    const data = JSON.parse(text) as { detail?: unknown };
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) {
      return data.detail.map((d) => (typeof d === "object" && d && "msg" in d ? String((d as { msg: string }).msg) : String(d))).join("; ");
    }
    return text;
  } catch {
    return text;
  }
}

export function formatFetchError(e: unknown): string {
  if (e instanceof TypeError && /fetch/i.test(e.message)) {
    return (
      "无法连接后端（Failed to fetch）。常见原因：\n" +
      "1) 后端未启动 — 在 backend 目录执行：.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000\n" +
      "2) 后端代码已更新但未重载 — 请停止旧 uvicorn 后重新启动（见 desktop\\run-dev.ps1）\n" +
      "3) 视频 OCR 处理中连接中断 — 单文件约 30～60 秒，请勿重复点击\n" +
      "4) 请用浏览器打开 http://127.0.0.1:5173（经 Vite 代理 /api），不要直接打开 dist/index.html\n" +
      "自检：http://127.0.0.1:8000/api/imports/ocr-status 应返回 JSON；http://127.0.0.1:5173/api/imports/ocr-status 同理。"
    );
  }
  const msg = String(e);
  if (/404|not found|upload-scan/i.test(msg)) {
    return `${msg}\n\n若路径含 upload-scan-one / ocr-status 却 404，说明后端仍是旧进程，请重启 uvicorn。`;
  }
  return msg;
}
