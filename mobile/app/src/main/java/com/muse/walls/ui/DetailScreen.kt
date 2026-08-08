package com.muse.walls.ui

// 详情页：预览与一键设桌面/锁屏壁纸
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.muse.walls.data.Wallpaper

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DetailScreen(
    wallpaper: Wallpaper?,
    busy: Boolean,
    message: String?,
    onBack: () -> Unit,
    onSetHome: () -> Unit,
    onSetLock: () -> Unit,
    onSetBoth: () -> Unit,
    onLike: () -> Unit,
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(wallpaper?.title ?: "壁纸详情") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                    }
                },
            )
        },
    ) { padding ->
        if (wallpaper == null) {
            Column(
                Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(24.dp),
            ) { CircularProgressIndicator() }
            return@Scaffold
        }
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            AsyncImage(
                model = wallpaper.image_url,
                contentDescription = wallpaper.title,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(0.7f)
                    .clip(RoundedCornerShape(20.dp)),
            )
            Text(wallpaper.title, style = MaterialTheme.typography.headlineMedium)
            Text(
                listOfNotNull(
                    wallpaper.category_name,
                    "${wallpaper.width}×${wallpaper.height}",
                    "喜欢 ${wallpaper.likes}",
                    "浏览 ${wallpaper.views}",
                ).joinToString(" · "),
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            if (wallpaper.description.isNotBlank()) {
                Text(wallpaper.description, style = MaterialTheme.typography.bodyMedium)
            }
            if (!message.isNullOrBlank()) {
                Text(message, color = MaterialTheme.colorScheme.primary)
            }
            if (busy) {
                CircularProgressIndicator(modifier = Modifier.padding(8.dp))
            }
            Button(
                onClick = onSetHome,
                enabled = !busy,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("设为桌面壁纸") }
            Button(
                onClick = onSetLock,
                enabled = !busy,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("设为锁屏壁纸") }
            OutlinedButton(
                onClick = onSetBoth,
                enabled = !busy,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("桌面 + 锁屏一起设置") }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedButton(onClick = onLike, enabled = !busy) { Text("喜欢") }
            }
            Spacer(modifier = Modifier.height(24.dp))
        }
    }
}
