package com.muse.walls

// 主 Activity：导航首页 / 详情 / 设置
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.muse.walls.ui.AppViewModel
import com.muse.walls.ui.DetailScreen
import com.muse.walls.ui.HomeScreen
import com.muse.walls.ui.SettingsScreen
import com.muse.walls.ui.WishPoolScreen
import com.muse.walls.ui.theme.MuseTheme
import com.muse.walls.wallpaper.WallpaperTarget

class MainActivity : ComponentActivity() {
    private val vm: AppViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MuseTheme {
                MuseNav(vm)
            }
        }
    }
}

@Composable
private fun MuseNav(vm: AppViewModel) {
    val nav = rememberNavController()
    NavHost(navController = nav, startDestination = "home") {
        composable("home") {
            HomeScreen(
                categories = vm.categories,
                items = vm.items,
                total = vm.total,
                selectedCategory = vm.selectedCategory,
                query = vm.query,
                loading = vm.loading,
                loadingMore = vm.loadingMore,
                error = vm.error,
                onQueryChange = vm::onQueryChange,
                onCategory = vm::selectCategory,
                onOpen = {
                    vm.openDetail(it)
                    nav.navigate("detail")
                },
                onLoadMore = vm::loadMore,
                onWishPool = {
                    vm.openWishPool()
                    nav.navigate("wish")
                },
                onSettings = {
                    vm.loadSettings()
                    nav.navigate("settings")
                },
            )
        }
        composable("wish") {
            WishPoolScreen(
                prompt = vm.wishPrompt,
                author = vm.wishAuthor,
                mode = vm.wishMode,
                sourceUrl = vm.wishSourceUrl,
                wishes = vm.wishes,
                total = vm.wishTotal,
                submitting = vm.wishSubmitting,
                message = vm.wishMessage,
                onPromptChange = vm::onWishPromptChange,
                onAuthorChange = vm::onWishAuthorChange,
                onModeChange = vm::onWishModeChange,
                onSourceUrlChange = vm::onWishSourceUrlChange,
                onSubmit = vm::submitWish,
                onRetry = vm::retryWish,
                onBack = {
                    vm.stopWishPolling()
                    nav.popBackStack()
                },
            )
        }
        composable("detail") {
            DetailScreen(
                wallpaper = vm.detail,
                busy = vm.busy,
                message = vm.message,
                onBack = {
                    vm.clearDetail()
                    nav.popBackStack()
                },
                onSetHome = { vm.setWallpaper(WallpaperTarget.HOME) },
                onSetLock = { vm.setWallpaper(WallpaperTarget.LOCK) },
                onSetBoth = { vm.setWallpaper(WallpaperTarget.BOTH) },
                onLike = vm::like,
            )
        }
        composable("settings") {
            SettingsScreen(
                currentUrl = vm.settingsUrl,
                saving = vm.settingsSaving,
                message = vm.settingsMsg,
                onBack = { nav.popBackStack() },
                onSave = vm::saveBaseUrl,
                onTest = vm::testHealth,
            )
        }
    }
}
