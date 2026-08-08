# 幕色 Android（APK）

手机端壁纸客户端：连接幕色服务端 API，浏览分类，一键设置**桌面壁纸**或**锁屏壁纸**。

## 功能

- 配置服务端 Base URL（Cloudflare 隧道 / 自建域名均可）
- 分类筛选、搜索、双列瀑布网格、加载更多
- 详情预览；一键「桌面 / 锁屏 / 两者」
- 点赞与下载计数回写服务端

## 构建 APK

```bash
export ANDROID_HOME=$HOME/android-sdk   # 或你的 SDK 路径
cd mobile
./gradlew :app:assembleDebug
```

产物：

`app/build/outputs/apk/debug/app-debug.apk`

安装：

```bash
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## 连接服务端

1. 确保手机能访问后端（公网域名或同一局域网 IP）
2. 打开 App → 右上角设置 → 填写 Base URL  
   例如：`https://xxx.trycloudflare.com` 或 `http://192.168.1.8:8000`
3. 点「测试连接」或「保存并连接」

默认已写入构建时的隧道地址，可随时修改。

## 权限

- `INTERNET`
- `SET_WALLPAPER`（Android 7+ 支持分别设置桌面 / 锁屏）

## 说明

- 部分定制 ROM 可能限制锁屏壁纸 API，失败时会提示错误信息
- 相对路径上传图（`/uploads/...`）会自动拼接 Base URL

## AI 许愿池

首页右上角星星图标进入。填写 Prompt 提交后，后端异步生成；生成中会自动轮询。

说明：Cursor 内置生图不能被 APK/后端直接调用，运行时使用服务端配置的 Pollinations 文生图。

