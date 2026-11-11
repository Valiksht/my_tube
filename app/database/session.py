"""Менеджер асинхронных сессий PostgreSQL."""

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.config import get_settings


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
    settings = get_settings()
    
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
    )
    
    async with engine() as session:
        yield session
