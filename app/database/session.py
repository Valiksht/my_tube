"""Настройки подключения к базе данных."""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.config import settings


# Создание асинхронного движка базы данных
async_database_url = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/mytube_db"
)

engine = create_async_engine(
    async_database_url,
    echo=settings.DEBUG,  # Вывод SQL-запросов в режиме DEBUG
    future=True  # Для совместимости с разными версиями SQLAlchemy
)

# Создание фабричной функции сессий
AsyncSessionLocal = async_sessionmaker(
    AsyncSession,
    bind=engine,
    autoflush=False,  # Отключаем автоматический flush для контроля транзакций
    autocommit=False  # Не используем автокоммит - управляем вручную через зависимости
)

