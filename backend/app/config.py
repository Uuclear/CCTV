"""Application settings."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _BACKEND_ROOT.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = f"sqlite+aiosqlite:///{(_BACKEND_ROOT / 'data' / 'app.db').as_posix()}"
    files_dir: Path = _REPO_ROOT / "data" / "files"
    standards_dir: Path = _REPO_ROOT / "config" / "standards" / "db31t444-2022"
    cors_origins: str = "http://127.0.0.1:5173,http://localhost:5173"


settings = Settings()
