# 应用配置：路径、密钥与管理员默认账号
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """运行时配置，可通过环境变量覆盖。"""

    app_name: str = "幕色 Muse"
    secret_key: str = "muse-wallpaper-dev-secret-change-me"
    access_token_expire_minutes: int = 60 * 24
    admin_username: str = "admin"
    admin_password: str = "admin123"
    database_url: str = "sqlite:///./muse.db"
    upload_dir: Path = Path(__file__).resolve().parent.parent / "uploads"
    max_upload_mb: int = 15
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
    ]
    # AI 许愿池：运行时文生图/图生图（Cursor 生图为 Agent 工具，后端无法直连）
    ai_image_provider: str = "pollinations"
    ai_image_model: str = "flux"
    # 图生图模型；kontext 需 enter.pollinations.ai，免费档可用 flux+image
    ai_img2img_model: str = "flux"
    ai_default_width: int = 1920
    ai_default_height: int = 1080
    ai_wish_auto_publish: bool = True
    # 图生图时供外网拉取 /uploads 参考图的公网根地址
    public_base_url: str = "https://already-tried-issue-mem.trycloudflare.com"


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
