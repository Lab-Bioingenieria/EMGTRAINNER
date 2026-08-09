from enum import Enum

from pydantic import PostgresDsn, RedisDsn, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TEST = "test"


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)


class Config(BaseConfig):
    DEBUG: int = 0
    DEFAULT_LOCALE: str = "en_US"
    ENVIRONMENT: str = EnvironmentType.DEVELOPMENT
    POSTGRES_URL: str = "sqlite+aiosqlite:///./fastapi.db"
    REDIS_URL: str = "redis://localhost:6379/7"
    RELEASE_VERSION: str = "0.1"
    SHOW_SQL_ALCHEMY_QUERIES: int = 0
    SECRET_KEY: str = "super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24
    CORS_ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]
    CELERY_BROKER_URL: str = "amqp://rabbit:password@localhost:5672"
    CELERY_BACKEND_URL: str = "redis://localhost:6379/0"

    @model_validator(mode="after")
    def validate_auth_secrets(self):
        if (
            self.ENVIRONMENT not in {EnvironmentType.DEVELOPMENT, EnvironmentType.TEST}
            and self.SECRET_KEY == "super-secret-key"
        ):
            raise ValueError(
                "SECRET_KEY must be configured outside development/test environments"
            )
        return self


config: Config = Config()
