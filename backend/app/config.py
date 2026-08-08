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


settings = Settings()
settings.upload_dir.mkdir(parents=True, exist_ok=True)
