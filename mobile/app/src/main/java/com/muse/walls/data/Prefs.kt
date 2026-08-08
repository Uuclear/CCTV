package com.muse.walls.data

// DataStore 偏好：服务端 Base URL
import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.muse.walls.BuildConfig
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore("muse_prefs")

class Prefs(private val context: Context) {
    private val keyBaseUrl = stringPreferencesKey("base_url")

    /** 观察当前服务端地址 */
    val baseUrlFlow: Flow<String> = context.dataStore.data.map { prefs ->
        prefs[keyBaseUrl]?.trim()?.trimEnd('/')
            ?: BuildConfig.DEFAULT_BASE_URL.trimEnd('/')
    }

    /** 保存服务端地址 */
    suspend fun setBaseUrl(url: String) {
        val cleaned = url.trim().trimEnd('/')
        context.dataStore.edit { it[keyBaseUrl] = cleaned }
    }
}
