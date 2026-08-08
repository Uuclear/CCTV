/** 壁纸与分类的共享类型定义 */

export interface Category {
  id: number;
  name: string;
  slug: string;
  description: string;
  cover_url: string;
  sort_order: number;
  is_active: boolean;
  wallpaper_count: number;
  created_at: string;
}

export interface Wallpaper {
  id: number;
  title: string;
  slug: string;
  description: string;
  image_url: string;
  thumb_url: string;
  width: number;
  height: number;
  tags: string;
  palette: string;
  style_hint: string;
  downloads: number;
  views: number;
  likes: number;
  is_featured: boolean;
  is_published: boolean;
  category_id: number | null;
  category_name: string | null;
  category_slug: string | null;
  created_at: string;
  updated_at: string;
}

export interface WallpaperList {
  total: number;
  items: Wallpaper[];
}

export interface Stats {
  wallpaper_count: number;
  published_count: number;
  featured_count: number;
  category_count: number;
  total_views: number;
  total_downloads: number;
  total_likes: number;
  wish_count?: number;
  wish_done_count?: number;
}

export interface Wish {
  id: number;
  prompt: string;
  author_name: string;
  mode: "txt2img" | "img2img" | string;
  status: "pending" | "generating" | "done" | "failed" | string;
  width: number;
  height: number;
  provider: string;
  source_image_url: string;
  image_url: string;
  error_message: string;
  wallpaper_id: number | null;
  created_at: string;
  updated_at: string;
}

export interface WishList {
  total: number;
  items: Wish[];
}

export type ViewMode = "masonry" | "grid" | "cinema" | "river";
export type SortKey = "newest" | "popular" | "likes" | "downloads";
