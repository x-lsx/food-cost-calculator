from pathlib import Path
import os
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):

    APP_NAME: str = Field("FastAPI APP", alias = "APP_NAME")
    DEBUG: bool = Field(False, alias = "DEBUG")
    DB_URL: str = Field("", validation_alias=AliasChoices("DB_URL", "db_url"))
    SECRET_KEY: str = Field("secret_key", alias = "SECRET_KEY")
    REFRESH_SECRET_KEY: str = Field("secret_key", alias = "REFRESH_SECRET_KEY")
    ALGORITHM: str = Field("HS256", alias = "ALGORITHM")
    ACCESS_TOKEN_EXPIRE: int = Field(120, alias = "ACCESS_TOKEN_EXPIRE")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, alias ="REFRESH_TOKEN_EXPIRE_DAYS")
    CORS_ORIGINS: str = Field("", alias = "CORS_ORIGINS")

    STATIC_DIR: str = Field("static", alias = "STATIC_DIR")
    IMAGES_DIR: str = Field("static/images", alias = "IMAGES_DIR")
    UPLOAD_DIR: str = Field("uploads", alias = "UPLOAD_DIR")
    TIMEZONE: str = Field("Europe/Moscow", alias="TIMEZONE")
    
    REDIS_HOST: str = Field("localhost", alias="REDIS_HOST")
    REDIS_PORT: int = Field(6379, alias="REDIS_PORT")
    REDIS_DB: int = Field(0, alias="REDIS_DB")
    REDIS_PASSWORD: str | None = Field(None, alias="REDIS_PASSWORD")
    CACHE_EXPIRE_SECONDS: int = Field(300, alias="CACHE_EXPIRE_SECONDS") 
    
    LOG_LEVEL: str = Field("INFO", alias="LOG_LEVEL")
    
    model_config = SettingsConfigDict(
        env_file=(
            BASE_DIR / "env.docker" if os.getenv("ENV") == "docker" else BASE_DIR / "env.local"
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
