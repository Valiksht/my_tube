"""Менеджер асинхронных сессий PostgreSQL."""

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)

from app.core.config import get_settings

# Глобальный кэш движка
_engine_cache: dict[str, object] = {}


def _get_engine():
    """Получить или создать движок с кэшированием."""
    settings = get_settings()
    key = settings.database_url
    
    if key not in _engine_cache:
        _engine_cache[key] = create_async_engine(
            settings.database_url,
            echo=settings.debug,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
        )
    
    return _engine_cache[key]


# Создаём maker для сессий
_session_maker = async_sessionmaker(
    bind=None,  # Будет установлено в get_async_session
    class_=AsyncSession,
    expire_on_commit=False,
)


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
    engine = _get_engine()
    session = _session_maker(bind=engine)
    
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
