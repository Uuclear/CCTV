# FastAPI 应用入口：挂载路由、静态资源与种子数据
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.routers import auth, categories, stats, wallpapers
from app.seed import ensure_seed


@asynccontextmanager
async def lifespan(_: FastAPI):
    """启动时建表并写入种子数据。"""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_seed(db)
    finally:
        db.close()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(categories.router)
app.include_router(wallpapers.router)
app.include_router(stats.router)
app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")


@app.get("/api/health")
def health() -> dict:
    """健康检查。"""
    return {"ok": True, "app": settings.app_name}
