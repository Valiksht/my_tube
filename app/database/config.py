"""Конфигурация подключения к базе данных PostgreSQL."""

import asyncio
import asyncpg  # Импорт перед SQLAlchemy чтобы использовать asyncpg
import os
from functools import lru_cache


@lru_cache()
def check_connection():
    """Проверить подключение к базе данных.
    
    Возвращает True если подключение успешно, иначе False.
    """
    from sqlalchemy.ext.asyncio import create_async_engine
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL не настроено!")
    
    async def _test():
        engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True
        )
        
        try:
            conn = await engine.connect()
            await conn.execute("SELECT 1")
            await conn.close()  # Возвращаем соединение в пул
            return True
        except Exception:
            return False
    
    loop = asyncio.get_event_loop()
    return bool(loop.run_until_complete(_test()))


def get_async_engine():
    """Получить асинхронный движок PostgreSQL."""
    from sqlalchemy.ext.asyncio import create_async_engine
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL не настроено!")
    
    return create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        driver="asyncpg"
    )


__all__ = ["check_connection", "get_async_engine"]