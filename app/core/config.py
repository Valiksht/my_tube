"""Конфигурация приложения YouTube Clone.

Загружает настройки из переменных окружения (.env) с валидацией через Pydantic v2.
"""

from typing import Any, Literal

from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения.

    Все значения загружаются из переменных окружения.
    Для локальной разработки используется файл .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Приложение
    app_name: str = "YouTube Clone"
    debug: bool = False

    # База данных
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "mytube_db"
    postgres_port: int = 5432
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/mytube_db"
    )

    # Секреты
    secret_key: str = "change-this-secret-key-in-production-12345"
    algorithm: str = "HS256"

    # CORS
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:8000,http://localhost:8000,http://localhost:80"

    # Сессии
    session_cookie: str = "session"
    session_max_age: int = 86400  # 24 часа
    session_token_expire_days: int = 7

    # CSRF
    csrf_secret_key: str = "change-this-csrf-secret-key-in-production"

    # Storage
    storage_type: str = "filesystem"
    storage_dir: str = "./storage"
    storage_base_url: str = "http://localhost:8000/storage"

    @property
    def cors_origins_list(self) -> list[str]:
        """Разобрать строку CORS origins в список."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Предупреждение о слабом секрете в dev-режиме."""
        if v == "change-this-secret-key-in-production-12345":
            import warnings
            warnings.warn(
                "Используется секретный ключ по умолчанию! "
                "Установите переменную SECRET_KEY для production."
            )
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """Проверка что URL базы данных использует asyncpg."""
        if "asyncpg" not in v:
            raise ValueError("DATABASE_URL должен использовать драйвер asyncpg")
        return v


# Глобальный экземпляр настроек (кэшируется через lru_cache)
_settings_cache: dict[str, Settings] = {}


def get_settings() -> Settings:
    """Получить экземпляр настроек с кэшированием.
    
    Returns:
        Settings: Экземпляр конфигурации приложения.
    """
    if "main" not in _settings_cache:
        _settings_cache["main"] = Settings()
    return _settings_cache["main"]
