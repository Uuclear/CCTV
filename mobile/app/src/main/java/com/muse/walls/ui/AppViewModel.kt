package com.muse.walls.ui

// 全局 ViewModel：列表、详情、设壁纸与服务端配置
import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.muse.walls.MuseApp
import com.muse.walls.data.Category
import com.muse.walls.data.MuseApi
import com.muse.walls.data.Wallpaper
import com.muse.walls.wallpaper.WallpaperSetter
import com.muse.walls.wallpaper.WallpaperTarget
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request

class AppViewModel(app: Application) : AndroidViewModel(app) {
    private val prefs = (app as MuseApp).prefs
    private var baseUrl: String = ""
    private val api = MuseApi { baseUrl }
    private val wallpaperSetter = WallpaperSetter(app)

    var categories by mutableStateOf<List<Category>>(emptyList())
        private set
    var items by mutableStateOf<List<Wallpaper>>(emptyList())
        private set
    var total by mutableStateOf(0)
        private set
    var page by mutableStateOf(1)
        private set
    var selectedCategory by mutableStateOf("")
        private set
    var query by mutableStateOf("")
        private set
    var loading by mutableStateOf(true)
        private set
    var loadingMore by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set
    var detail by mutableStateOf<Wallpaper?>(null)
        private set
    var busy by mutableStateOf(false)
        private set
    var message by mutableStateOf<String?>(null)
        private set
    var settingsUrl by mutableStateOf("")
        private set
    var settingsMsg by mutableStateOf<String?>(null)
        private set
    var settingsSaving by mutableStateOf(false)
        private set

    private var searchJob: Job? = null

    init {
        viewModelScope.launch {
            baseUrl = prefs.baseUrlFlow.first()
            settingsUrl = baseUrl
            refresh()
        }
    }

    /** 刷新分类与第一页壁纸 */
    fun refresh() {
        viewModelScope.launch {
            loading = true
            error = null
            page = 1
            try {
                categories = api.categories()
                val list = api.wallpapers(category = selectedCategory.ifBlank { null }, q = query.ifBlank { null })
                items = list.items
                total = list.total
            } catch (e: Exception) {
                error = e.message ?: "加载失败"
            } finally {
                loading = false
            }
        }
    }

    /** 切换分类 */
    fun selectCategory(slug: String) {
        selectedCategory = slug
        refresh()
    }

    /** 搜索输入（防抖） */
    fun onQueryChange(value: String) {
        query = value
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(350)
            refresh()
        }
    }

    /** 加载更多 */
    fun loadMore() {
        if (loadingMore || items.size >= total) return
        viewModelScope.launch {
            loadingMore = true
            try {
                val next = page + 1
                val list = api.wallpapers(
                    category = selectedCategory.ifBlank { null },
                    q = query.ifBlank { null },
                    page = next,
                )
                items = items + list.items
                total = list.total
                page = next
            } catch (e: Exception) {
                error = e.message
            } finally {
                loadingMore = false
            }
        }
    }

    /** 打开详情并上报浏览 */
    fun openDetail(item: Wallpaper) {
        detail = item
        message = null
        viewModelScope.launch {
            try {
                detail = api.wallpaper(item.id)
            } catch (_: Exception) {
                // 保留列表中的条目
            }
        }
    }

    fun clearDetail() {
        detail = null
        message = null
    }

    /** 一键设置壁纸 */
    fun setWallpaper(target: WallpaperTarget) {
        val current = detail ?: return
        viewModelScope.launch {
            busy = true
            message = null
            try {
                api.download(current.id)
                message = wallpaperSetter.setFromUrl(current.image_url, target)
            } catch (e: Exception) {
                message = e.message ?: "设置失败"
            } finally {
                busy = false
            }
        }
    }

    fun like() {
        val current = detail ?: return
        viewModelScope.launch {
            try {
                detail = api.like(current.id)
                message = "已喜欢"
            } catch (e: Exception) {
                message = e.message
            }
        }
    }

    fun loadSettings() {
        viewModelScope.launch {
            settingsUrl = prefs.baseUrlFlow.first()
            settingsMsg = null
        }
    }

    /** 保存服务端地址并重新拉取 */
    fun saveBaseUrl(url: String) {
        viewModelScope.launch {
            settingsSaving = true
            settingsMsg = null
            try {
                prefs.setBaseUrl(url)
                baseUrl = url.trim().trimEnd('/')
                settingsUrl = baseUrl
                settingsMsg = "已保存，正在重新连接…"
                refresh()
                settingsMsg = "连接成功，共 $total 张壁纸"
            } catch (e: Exception) {
                settingsMsg = e.message ?: "保存失败"
            } finally {
                settingsSaving = false
            }
        }
    }

    /** 仅测试 health 接口 */
    fun testHealth(url: String) {
        viewModelScope.launch {
            settingsSaving = true
            settingsMsg = null
            try {
                val base = url.trim().trimEnd('/')
                val res = with(OkHttpClient()) {
                    newCall(Request.Builder().url("$base/api/health").get().build()).execute()
                }
                settingsMsg = if (res.isSuccessful) {
                    "健康检查通过：${res.body?.string()}"
                } else {
                    "失败 HTTP ${res.code}"
                }
            } catch (e: Exception) {
                settingsMsg = e.message
            } finally {
                settingsSaving = false
            }
        }
    }
}
