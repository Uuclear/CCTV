package com.muse.walls.ui.theme

// 幕色移动端主题：墨色底 + 玉色强调
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.Typography
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

private val Ink = Color(0xFF0E1418)
private val Ink2 = Color(0xFF172029)
private val Jade = Color(0xFF3F8F7A)
private val JadeBright = Color(0xFF62B79D)
private val Pearl = Color(0xFFE7EEF3)
private val Muted = Color(0xFF9AABBA)

private val colors = darkColorScheme(
    primary = JadeBright,
    onPrimary = Color(0xFF062019),
    secondary = Jade,
    background = Ink,
    surface = Ink2,
    onBackground = Pearl,
    onSurface = Pearl,
    onSurfaceVariant = Muted,
    outline = Color(0x33E7EEF3),
)

private val typography = Typography(
    headlineLarge = TextStyle(fontWeight = FontWeight.Bold, fontSize = 30.sp, color = Pearl),
    headlineMedium = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 22.sp),
    titleMedium = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 16.sp),
    bodyMedium = TextStyle(fontSize = 14.sp, lineHeight = 20.sp),
    labelLarge = TextStyle(fontWeight = FontWeight.Medium, fontSize = 14.sp),
)

@Composable
fun MuseTheme(content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = colors, typography = typography, content = content)
}
