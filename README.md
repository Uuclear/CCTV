# 幕色 Muse — 壁纸网站

优雅的壁纸浏览与管理站点：前台多风格展示 + 完整后台管理。

## 功能

- **前台**：品牌首页、壁纸馆、分类页
- **四种展示风格**：瀑布 / 网格 / 影院 / 溪流（本地记忆）
- **分类与筛选**：山海、都市、极简、暗调、植物、抽象；支持搜索与排序
- **沉浸灯箱**：键盘左右切换、点赞、下载计数
- **后台**：JWT 登录、统计概览、分类 CRUD、壁纸外链/上传、精选与草稿

## 技术栈

- 后端：FastAPI + SQLAlchemy + SQLite + JWT
- 前端：React + Vite + TypeScript + React Router

## 快速启动

```bash
# 后端
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端（另开终端）
cd frontend
npm install
npm run dev
```

- 前台：http://127.0.0.1:5173
- API 文档：http://127.0.0.1:8000/docs
- 管理后台：http://127.0.0.1:5173/admin  
  默认账号：`admin` / `admin123`

## 目录

```
backend/     FastAPI 服务、种子数据、上传目录
frontend/    React 前台与管理界面
```

首次启动会自动写入示例分类与少量壁纸（Unsplash 外链）。

### 批量灌入约 2000 张壁纸

```bash
cd backend && source .venv/bin/activate
PYTHONPATH=. python scripts/bulk_seed_wallpapers.py --count 2000
```

图片使用 `picsum.photos` 确定性外链（按 seed 生成），会均匀分配到各分类。可重复执行以继续追加。

## AI 壁纸许愿池

网页 `/wish` 与 APK 内「许愿池」可提交 Prompt，后端异步生成壁纸。

**关于 Cursor 生图：** Cursor 的 `GenerateImage` 只在 Cloud Agent 对话侧可用，**网站/APK 后端无法直接调用**。  
运行时使用 [Pollinations](https://pollinations.ai) 文生图接口兑现愿望，成功后自动进入「AI许愿」分类。

```bash
# 提交许愿
curl -X POST http://127.0.0.1:8000/api/wishes \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"neon rain city night wallpaper","width":1920,"height":1080}'
```

## Android APK

手机端工程在 `mobile/`，可连接同一服务端并一键设置桌面/锁屏壁纸。

```bash
export ANDROID_HOME=$HOME/android-sdk
cd mobile && ./gradlew :app:assembleDebug
# 产物: mobile/app/build/outputs/apk/debug/app-debug.apk
# 或: mobile/dist/muse-walls-debug.apk
```

安装后在 App 内填写服务端 Base URL（如 Cloudflare 隧道地址）。详见 [mobile/README.md](mobile/README.md)。

