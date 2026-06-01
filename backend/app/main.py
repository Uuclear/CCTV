"""FastAPI application entry."""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db import engine
from app.db_migrate import migrate_sqlite_schema
from app.models import Base
from app.routers import exports, imports, projects, reports, segments, standards
from app.services import ocr_text


_BACK_ROOT = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    data_dir = _BACK_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    settings.files_dir.mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(migrate_sqlite_schema)

    async def _warmup_ocr() -> None:
        await asyncio.to_thread(ocr_text.warmup)

    # 不阻塞 HTTP 监听：启动阶段 OCR 模型加载可能需数十秒，否则前端会 Failed to fetch
    asyncio.create_task(_warmup_ocr())
    yield


app = FastAPI(title="CCTV Report API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(segments.router)
app.include_router(reports.router)
app.include_router(imports.router)
app.include_router(exports.router)
app.include_router(standards.router)

settings.files_dir.mkdir(parents=True, exist_ok=True)

app.mount(
    "/media",
    StaticFiles(directory=str(settings.files_dir.resolve())),
    name="media",
)


@app.get("/health")
async def health():
    return {"status": "ok"}
