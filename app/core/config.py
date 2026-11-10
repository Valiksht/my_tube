"""Конфигурация приложения через Pydantic Settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения из .env файла."""

    # Приложения FastAPI
    APP_TITLE: str = "YouTube Clone API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Educational YouTube Clone project with FastAPI"


settings = Settings()
