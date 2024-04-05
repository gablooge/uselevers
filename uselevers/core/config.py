import logging
import secrets
from pathlib import Path
from typing import Literal

from pydantic import FilePath, HttpUrl, PostgresDsn, computed_field
from pydantic_settings import BaseSettings

project_root = Path(__file__).parent.parent.parent.absolute()


class Settings(BaseSettings):
    # Project configuration
    PROJECT_NAME: str = "Uselevers Backend"
    PROJECT_VERSION: str = "1.0.0-dev"

    # API configuration
    API_V1_PATH: str = "/api/v1"

    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # Database configuration
    SQLALCHEMY_DATABASE_URI: PostgresDsn

    # CORS: Origins
    CORS_ORIGIN_FRONTEND: str

    # Logging configuration
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING"] = "INFO"
    SENTRY_DSN: HttpUrl | None = None

    # Development flags. Set them in .env.docker
    DEV_FASTAPI_DEBUG: bool = False
    DEV_MIGRATIONS: bool = False
    DEV_MIGRATIONS_ALEMBIC_INI: FilePath = project_root / "alembic.ini"
    DEV_FEATURES: bool = False

    @computed_field()  # type: ignore[misc]
    @property
    def http_client_user_agent(self) -> str:
        return f"uselevers/{self.PROJECT_VERSION}"


#
# Settings transformations
#


def log_level_from(settings: Settings) -> int:
    match settings.LOG_LEVEL:
        case "DEBUG":
            return logging.DEBUG
        case "INFO":
            return logging.INFO
        case "WARNING":
            return logging.WARNING
    raise Exception("Invalid log level")


settings = Settings()  # type: ignore[call-arg]
