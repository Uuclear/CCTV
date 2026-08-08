package com.muse.walls.wallpaper

// 系统壁纸 / 锁屏壁纸设置
import android.app.WallpaperManager
import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.os.Build
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.util.concurrent.TimeUnit

enum class WallpaperTarget {
    HOME,
    LOCK,
    BOTH,
}

class WallpaperSetter(private val context: Context) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    /** 下载图片并设置为桌面 / 锁屏 / 两者 */
    suspend fun setFromUrl(imageUrl: String, target: WallpaperTarget): String =
        withContext(Dispatchers.IO) {
            val bitmap = downloadBitmap(imageUrl)
            val wm = WallpaperManager.getInstance(context)
            when (target) {
                WallpaperTarget.HOME -> setFlags(wm, bitmap, WallpaperManager.FLAG_SYSTEM)
                WallpaperTarget.LOCK -> setFlags(wm, bitmap, WallpaperManager.FLAG_LOCK)
                WallpaperTarget.BOTH -> {
                    setFlags(wm, bitmap, WallpaperManager.FLAG_SYSTEM)
                    setFlags(wm, bitmap, WallpaperManager.FLAG_LOCK)
                }
            }
            when (target) {
                WallpaperTarget.HOME -> "已设为桌面壁纸"
                WallpaperTarget.LOCK -> "已设为锁屏壁纸"
                WallpaperTarget.BOTH -> "已同时设置桌面与锁屏"
            }
        }

    /** 按目标 Flag 写入壁纸 */
    private fun setFlags(wm: WallpaperManager, bitmap: Bitmap, flag: Int) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            wm.setBitmap(bitmap, null, true, flag)
        } else {
            wm.setBitmap(bitmap)
        }
    }

    /** 从网络下载为 Bitmap */
    private fun downloadBitmap(url: String): Bitmap {
        val res = client.newCall(Request.Builder().url(url).get().build()).execute()
        if (!res.isSuccessful) error("图片下载失败 ${res.code}")
        val bytes = res.body?.bytes() ?: error("图片为空")
        return BitmapFactory.decodeByteArray(bytes, 0, bytes.size)
            ?: error("无法解码图片")
    }
}
