package com.muse.walls.data

// OkHttp + 简易 JSON 解析的 API 客户端
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.HttpUrl.Companion.toHttpUrl
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class MuseApi(private val baseUrlProvider: () -> String) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    /** 将相对路径补全为绝对 URL */
    fun resolveUrl(path: String): String {
        if (path.isBlank()) return ""
        if (path.startsWith("http://") || path.startsWith("https://")) return path
        val base = baseUrlProvider().trimEnd('/')
        return if (path.startsWith("/")) "$base$path" else "$base/$path"
    }

    /** 拉取分类列表 */
    suspend fun categories(): List<Category> = withContext(Dispatchers.IO) {
        val arr = JSONArray(get("/api/categories"))
        (0 until arr.length()).map { i ->
            val o = arr.getJSONObject(i)
            Category(
                id = o.getInt("id"),
                name = o.getString("name"),
                slug = o.getString("slug"),
                description = o.optString("description"),
                cover_url = o.optString("cover_url"),
                wallpaper_count = o.optInt("wallpaper_count"),
            )
        }
    }

    /** 分页拉取壁纸 */
    suspend fun wallpapers(
        category: String? = null,
        q: String? = null,
        page: Int = 1,
        pageSize: Int = 30,
        sort: String = "newest",
    ): WallpaperList = withContext(Dispatchers.IO) {
        val url = (resolveUrl("/api/wallpapers")).toHttpUrl().newBuilder()
            .addQueryParameter("page", page.toString())
            .addQueryParameter("page_size", pageSize.toString())
            .addQueryParameter("sort", sort)
        if (!category.isNullOrBlank()) url.addQueryParameter("category", category)
        if (!q.isNullOrBlank()) url.addQueryParameter("q", q)
        val root = JSONObject(getAbsolute(url.build().toString()))
        val items = root.getJSONArray("items")
        WallpaperList(
            total = root.getInt("total"),
            items = (0 until items.length()).map { parseWallpaper(items.getJSONObject(it)) },
        )
    }

    /** 详情（会增加浏览量） */
    suspend fun wallpaper(id: Int): Wallpaper = withContext(Dispatchers.IO) {
        parseWallpaper(JSONObject(get("/api/wallpapers/$id")))
    }

    /** 点赞 */
    suspend fun like(id: Int): Wallpaper = withContext(Dispatchers.IO) {
        parseWallpaper(JSONObject(post("/api/wallpapers/$id/like")))
    }

    /** 记录下载 */
    suspend fun download(id: Int): Wallpaper = withContext(Dispatchers.IO) {
        parseWallpaper(JSONObject(post("/api/wallpapers/$id/download")))
    }

    /** 许愿列表 */
    suspend fun wishes(page: Int = 1, pageSize: Int = 30): WishList =
        withContext(Dispatchers.IO) {
            val url = (resolveUrl("/api/wishes")).toHttpUrl().newBuilder()
                .addQueryParameter("page", page.toString())
                .addQueryParameter("page_size", pageSize.toString())
                .build()
            val root = JSONObject(getAbsolute(url.toString()))
            val arr = root.getJSONArray("items")
            WishList(
                total = root.getInt("total"),
                items = (0 until arr.length()).map { parseWish(arr.getJSONObject(it)) },
            )
        }

    /** 提交许愿（文生图 / 图生图外链） */
    suspend fun createWish(
        prompt: String,
        author: String,
        mode: String,
        sourceImageUrl: String,
        width: Int,
        height: Int,
    ): Wish = withContext(Dispatchers.IO) {
        val body = JSONObject()
            .put("prompt", prompt)
            .put("author_name", author)
            .put("mode", mode)
            .put("source_image_url", sourceImageUrl)
            .put("width", width)
            .put("height", height)
            .toString()
        val reqBody = body.toRequestBody("application/json; charset=utf-8".toMediaType())
        val res = client.newCall(
            Request.Builder().url(resolveUrl("/api/wishes")).post(reqBody).build(),
        ).execute()
        if (!res.isSuccessful) error("许愿失败 ${res.code}: ${res.body?.string()}")
        parseWish(JSONObject(res.body?.string() ?: error("空响应")))
    }

    /** 重试许愿 */
    suspend fun retryWish(id: Int): Wish = withContext(Dispatchers.IO) {
        parseWish(JSONObject(post("/api/wishes/$id/retry")))
    }

    private fun parseWish(o: JSONObject): Wish = Wish(
        id = o.getInt("id"),
        prompt = o.getString("prompt"),
        author_name = o.optString("author_name", "匿名"),
        mode = o.optString("mode", "txt2img"),
        status = o.optString("status", "pending"),
        width = o.optInt("width", 1920),
        height = o.optInt("height", 1080),
        provider = o.optString("provider"),
        source_image_url = resolveUrl(o.optString("source_image_url")),
        image_url = resolveUrl(o.optString("image_url")),
        error_message = o.optString("error_message"),
        wallpaper_id = if (o.isNull("wallpaper_id")) null else o.optInt("wallpaper_id"),
    )

    private fun parseWallpaper(o: JSONObject): Wallpaper = Wallpaper(
        id = o.getInt("id"),
        title = o.getString("title"),
        slug = o.getString("slug"),
        description = o.optString("description"),
        image_url = resolveUrl(o.getString("image_url")),
        thumb_url = resolveUrl(o.optString("thumb_url", o.getString("image_url"))),
        width = o.optInt("width"),
        height = o.optInt("height"),
        tags = o.optString("tags"),
        downloads = o.optInt("downloads"),
        views = o.optInt("views"),
        likes = o.optInt("likes"),
        is_featured = o.optBoolean("is_featured"),
        category_name = o.optString("category_name").ifBlank { null },
        category_slug = o.optString("category_slug").ifBlank { null },
    )

    private fun get(path: String): String = getAbsolute(resolveUrl(path))

    private fun getAbsolute(url: String): String {
        val res = client.newCall(Request.Builder().url(url).get().build()).execute()
        if (!res.isSuccessful) error("请求失败 ${res.code}: ${res.body?.string()}")
        return res.body?.string() ?: error("空响应")
    }

    private fun post(path: String): String {
        val body = ByteArray(0).toRequestBody(null)
        val res = client.newCall(
            Request.Builder().url(resolveUrl(path)).post(body).build(),
        ).execute()
        if (!res.isSuccessful) error("请求失败 ${res.code}: ${res.body?.string()}")
        return res.body?.string() ?: error("空响应")
    }
}
