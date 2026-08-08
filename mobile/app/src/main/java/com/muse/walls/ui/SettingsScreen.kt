package com.muse.walls.ui

// 服务端连接设置页
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(
    currentUrl: String,
    saving: Boolean,
    message: String?,
    onBack: () -> Unit,
    onSave: (String) -> Unit,
    onTest: (String) -> Unit,
) {
    var url by remember(currentUrl) { mutableStateOf(currentUrl) }
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("连接服务端") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "返回")
                    }
                },
            )
        },
    ) { padding ->
        Column(modifier = Modifier.padding(padding).padding(16.dp)) {
            Text(
                "填写幕色后端地址（可填 Cloudflare 隧道或你的公网域名）。手机需能访问该地址。",
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(modifier = Modifier.height(12.dp))
            OutlinedTextField(
                value = url,
                onValueChange = { url = it },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("Base URL") },
                placeholder = { Text("https://your-host.example") },
                singleLine = true,
            )
            Spacer(modifier = Modifier.height(12.dp))
            Button(
                onClick = { onSave(url) },
                enabled = !saving && url.isNotBlank(),
                modifier = Modifier.fillMaxWidth(),
            ) { Text(if (saving) "保存中…" else "保存并连接") }
            Spacer(modifier = Modifier.height(8.dp))
            Button(
                onClick = { onTest(url) },
                enabled = !saving && url.isNotBlank(),
                modifier = Modifier.fillMaxWidth(),
            ) { Text("测试连接 /api/health") }
            if (!message.isNullOrBlank()) {
                Spacer(modifier = Modifier.height(12.dp))
                Text(message, color = MaterialTheme.colorScheme.primary)
            }
        }
    }
}
