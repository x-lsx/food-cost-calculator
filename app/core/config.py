from pathlib import Path
import os
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # ====================== Основные ======================
    APP_NAME: str = Field("FastAPI Cost-Calculator", alias="APP_NAME")
    DEBUG: bool = Field(True, alias="DEBUG")
    ENV: str = Field("docker", alias="ENV")

    # ====================== PostgreSQL ======================
    POSTGRES_USER: str = Field("postgres", alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field("postgres_secret", alias="POSTGRES_PASSWORD")
    POSTGRES_DB: str = Field("foodcost_db", alias="POSTGRES_DB")
    DATABASE_URL: str = Field(..., alias="DATABASE_URL")   # обязательно

    # ====================== Redis ======================
    REDIS_HOST: str = Field("redis", alias="REDIS_HOST")
    REDIS_PORT: int = Field(6379, alias="REDIS_PORT")
    REDIS_DB: int = Field(0, alias="REDIS_DB")
    REDIS_PASSWORD: str | None = Field("redispass", alias="REDIS_PASSWORD")
    CACHE_EXPIRE_SECONDS: int = Field(300, alias="CACHE_EXPIRE_SECONDS")

    # ====================== FastAPI ======================
    FASTAPI_PORT: int = Field(8000, alias="FASTAPI_PORT")

    # ====================== Security ======================
    SECRET_KEY: str = Field(..., alias="SECRET_KEY")
    REFRESH_SECRET_KEY: str = Field(..., alias="REFRESH_SECRET_KEY")
    ALGORITHM: str = Field("HS256", alias="ALGORITHM")
    ACCESS_TOKEN_EXPIRE: int = Field(120, alias="ACCESS_TOKEN_EXPIRE")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # ====================== CORS ======================
    CORS_ORIGINS: str = Field("", alias="CORS_ORIGINS")

    # ====================== Paths ======================
    STATIC_DIR: str = Field("static", alias="STATIC_DIR")
    IMAGES_DIR: str = Field("static/images", alias="IMAGES_DIR")
    UPLOAD_DIR: str = Field("uploads", alias="UPLOAD_DIR")
    TIMEZONE: str = Field("Europe/Moscow", alias="TIMEZONE")

    # ====================== Logging ======================
    LOG_LEVEL: str = Field("20", alias="LOG_LEVEL")   # лучше как строка или int

    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / ".env.docker" if os.getenv("ENV") == "docker" else BASE_DIR / ".env.local"
        ),
        env_file_encoding="utf-8",
        extra="ignore",           # надёжнее
        case_sensitive=False,
    )


settings = Settings()