package com.muse.walls.data

// 与后端 JSON 对齐的数据模型

data class Category(
    val id: Int,
    val name: String,
    val slug: String,
    val description: String = "",
    val cover_url: String = "",
    val wallpaper_count: Int = 0,
)

data class Wallpaper(
    val id: Int,
    val title: String,
    val slug: String,
    val description: String = "",
    val image_url: String,
    val thumb_url: String = "",
    val width: Int = 0,
    val height: Int = 0,
    val tags: String = "",
    val downloads: Int = 0,
    val views: Int = 0,
    val likes: Int = 0,
    val is_featured: Boolean = false,
    val category_name: String? = null,
    val category_slug: String? = null,
)

data class WallpaperList(
    val total: Int,
    val items: List<Wallpaper>,
)

data class Wish(
    val id: Int,
    val prompt: String,
    val author_name: String = "匿名",
    val status: String = "pending",
    val width: Int = 1920,
    val height: Int = 1080,
    val provider: String = "",
    val image_url: String = "",
    val error_message: String = "",
    val wallpaper_id: Int? = null,
)

data class WishList(
    val total: Int,
    val items: List<Wish>,
)
