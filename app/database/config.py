"""Конфигурация подключения к базе данных PostgreSQL."""

import asyncio
import os
from functools import lru_cache

from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import get_settings


@lru_cache()
def check_connection() -> bool:
    """Проверить подключение к базе данных.
    
    Returns:
        True если подключение успешно, иначе False.
    """
    settings = get_settings()
    database_url = settings.database_url
    
    async def _test() -> bool:
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
        )
        
        try:
            async with engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    return bool(asyncio.run(_test()))


def get_async_engine():
    """Получить асинхронный движок PostgreSQL.
    
    Returns:
        AsyncEngine: Движок SQLAlchemy для работы с БД.
    """
    settings = get_settings()
    
    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        driver="asyncpg",
    )


__all__ = ["check_connection", "get_async_engine"]
