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

首次启动会自动写入示例分类与壁纸（Unsplash 外链）。
