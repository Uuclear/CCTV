package com.muse.walls.ui

// AI 许愿池：提交 Prompt 与查看生成进度
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import com.muse.walls.data.Wish

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun WishPoolScreen(
    prompt: String,
    author: String,
    wishes: List<Wish>,
    total: Int,
    submitting: Boolean,
    message: String?,
    onPromptChange: (String) -> Unit,
    onAuthorChange: (String) -> Unit,
    onSubmit: () -> Unit,
    onRetry: (Wish) -> Unit,
    onBack: () -> Unit,
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("AI 许愿池") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                    }
                },
            )
        },
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            item {
                Text(
                    "写下画面愿望，后端会异步生成壁纸。共 $total 条",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            item {
                OutlinedTextField(
                    value = prompt,
                    onValueChange = onPromptChange,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("Prompt") },
                    minLines = 3,
                )
            }
            item {
                OutlinedTextField(
                    value = author,
                    onValueChange = onAuthorChange,
                    modifier = Modifier.fillMaxWidth(),
                    label = { Text("署名（可选）") },
                    singleLine = true,
                )
            }
            item {
                Button(
                    onClick = onSubmit,
                    enabled = !submitting && prompt.trim().length >= 2,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(if (submitting) "许愿中…" else "投入许愿池")
                }
            }
            if (!message.isNullOrBlank()) {
                item {
                    Text(message, color = MaterialTheme.colorScheme.primary)
                }
            }
            items(wishes, key = { it.id }) { wish ->
                WishCard(wish, onRetry)
            }
        }
    }
}

@Composable
private fun WishCard(wish: Wish, onRetry: (Wish) -> Unit) {
    Column(
        Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp))
            .background(MaterialTheme.colorScheme.surface)
            .padding(12.dp),
    ) {
        Text(statusLabel(wish.status), style = MaterialTheme.typography.labelLarge)
        Spacer(modifier = Modifier.height(8.dp))
        if (wish.image_url.isNotBlank()) {
            AsyncImage(
                model = wish.image_url,
                contentDescription = wish.prompt,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(0.75f)
                    .clip(RoundedCornerShape(12.dp)),
            )
        } else {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1.4f)
                    .clip(RoundedCornerShape(12.dp))
                    .background(MaterialTheme.colorScheme.background),
                contentAlignment = Alignment.Center,
            ) {
                Text(
                    if (wish.status == "failed") "生成失败" else "画面酝酿中…",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
        Spacer(modifier = Modifier.height(8.dp))
        Text(wish.prompt)
        Text(
            "${wish.author_name} · ${wish.width}×${wish.height}",
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            style = MaterialTheme.typography.bodyMedium,
        )
        if (wish.error_message.isNotBlank()) {
            Text(wish.error_message, color = MaterialTheme.colorScheme.error)
        }
        if (wish.status == "failed" || wish.status == "pending") {
            Row {
                OutlinedButton(onClick = { onRetry(wish) }) { Text("重新生成") }
            }
        }
    }
}

/** 状态中文标签 */
private fun statusLabel(status: String): String = when (status) {
    "pending" -> "排队中"
    "generating" -> "生成中"
    "done" -> "已兑现"
    "failed" -> "失败"
    else -> status
}
