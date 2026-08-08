/** 前端 API 客户端：封装鉴权与请求 */

import type { Category, Stats, Wallpaper, WallpaperList, Wish, WishList } from "./types";

const TOKEN_KEY = "muse_admin_token";

/** 读取本地管理员令牌 */
export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

/** 写入或清除管理员令牌 */
export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

/** 统一发起 JSON/表单请求 */
async function request<T>(path: string, init: RequestInit = {}, auth = false): Promise<T> {
  const headers = new Headers(init.headers || {});
  if (!(init.body instanceof FormData) && !headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }
  if (auth) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  const res = await fetch(path, { ...init, headers });
  if (!res.ok) {
    const detail = await res.json().catch(() => ({}));
    throw new Error(detail.detail || `请求失败 (${res.status})`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  /** 健康检查 */
  health: () => request<{ ok: boolean }>("/api/health"),

  /** 分类列表 */
  categories: (activeOnly = true) =>
    request<Category[]>(`/api/categories?active_only=${activeOnly}`, {}, !activeOnly),

  /** 壁纸列表 */
  wallpapers: (params: Record<string, string | number | boolean | undefined>, auth = false) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") qs.set(k, String(v));
    });
    return request<WallpaperList>(`/api/wallpapers?${qs}`, {}, auth);
  },

  /** 壁纸详情（增加浏览） */
  wallpaper: (id: number) => request<Wallpaper>(`/api/wallpapers/${id}`),

  /** 点赞 */
  like: (id: number) => request<Wallpaper>(`/api/wallpapers/${id}/like`, { method: "POST" }),

  /** 记录下载 */
  download: (id: number) =>
    request<Wallpaper>(`/api/wallpapers/${id}/download`, { method: "POST" }),

  /** 管理员登录 */
  login: (username: string, password: string) =>
    request<{ access_token: string }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),

  /** 当前管理员 */
  me: () => request<{ id: number; username: string }>("/api/auth/me", {}, true),

  /** 后台统计 */
  stats: () => request<Stats>("/api/stats", {}, true),

  /** 新建分类 */
  createCategory: (body: Partial<Category>) =>
    request<Category>("/api/categories", { method: "POST", body: JSON.stringify(body) }, true),

  /** 更新分类 */
  updateCategory: (id: number, body: Partial<Category>) =>
    request<Category>(`/api/categories/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }, true),

  /** 删除分类 */
  deleteCategory: (id: number) =>
    request<{ ok: boolean }>(`/api/categories/${id}`, { method: "DELETE" }, true),

  /** 新建壁纸（外链） */
  createWallpaper: (body: Record<string, unknown>) =>
    request<Wallpaper>("/api/wallpapers", { method: "POST", body: JSON.stringify(body) }, true),

  /** 更新壁纸 */
  updateWallpaper: (id: number, body: Record<string, unknown>) =>
    request<Wallpaper>(`/api/wallpapers/${id}`, {
      method: "PUT",
      body: JSON.stringify(body),
    }, true),

  /** 删除壁纸 */
  deleteWallpaper: (id: number) =>
    request<{ ok: boolean }>(`/api/wallpapers/${id}`, { method: "DELETE" }, true),

  /** 上传壁纸文件 */
  uploadWallpaper: (form: FormData) =>
    request<Wallpaper>("/api/wallpapers/upload", { method: "POST", body: form }, true),

  /** 许愿列表 */
  wishes: (params: Record<string, string | number | undefined> = {}) => {
    const qs = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== "") qs.set(k, String(v));
    });
    return request<WishList>(`/api/wishes?${qs}`);
  },

  /** 单条许愿 */
  wish: (id: number) => request<Wish>(`/api/wishes/${id}`),

  /** 提交许愿 Prompt */
  createWish: (body: {
    prompt: string;
    author_name?: string;
    width?: number;
    height?: number;
  }) =>
    request<Wish>("/api/wishes", { method: "POST", body: JSON.stringify(body) }),

  /** 重试生成 */
  retryWish: (id: number) =>
    request<Wish>(`/api/wishes/${id}/retry`, { method: "POST" }),

  /** 生图提供方说明 */
  wishProvider: () =>
    request<{ provider: string; model: string; cursor_native: boolean; note: string }>(
      "/api/wishes/meta/provider",
    ),
};
