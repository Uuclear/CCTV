package com.muse.walls

// 应用入口：提供全局偏好存储
import android.app.Application
import com.muse.walls.data.Prefs

class MuseApp : Application() {
    /** 服务端地址等本地偏好 */
    lateinit var prefs: Prefs
        private set

    override fun onCreate() {
        super.onCreate()
        prefs = Prefs(this)
    }
}
