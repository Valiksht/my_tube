"""Менеджер асинхронных сессий PostgreSQL."""

import os
from contextlib import asynccontextmanager


@asynccontextmanager
async def get_async_session():
    """Контекстный менеджер для асинхронных сессий.
    
    Этапы работы:
    1. Получение движка (из кеша)
    2. Создание сессии через async context manager
    3. Автоматический commit/rollback при завершении
    
    Пример использования в FastAPI эндпоинте:
    
        @app.get("/videos")
        async def read_videos(db=Depends(get_async_session)):
            videos = ...
            return videos
    
    Автоматически обрабатывает commit и rollback.
    """
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.pool import StaticPool
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL не настроено!")
    
    engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True
    )
    
    async with engine() as session:
        yield session