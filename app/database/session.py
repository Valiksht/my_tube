"""Async session management."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

AsyncSessionDep = AsyncSession

try:
    from app.core.config import settings
except ImportError:
    settings = None  # type: ignore

_db_engine = None


def _get_db_url() -> str:
    """Получить URL подключения к базе данных."""
    if settings is None:
        return "postgresql+asyncpg://postgres:mytubesecurepassword123!@localhost:5432/mytube"
    # Используем DB_PASSWORD из config, если он указан; иначе fallback
    password = getattr(settings, 'DB_PASSWORD', 'mytubesecurepassword123!')
    return f"postgresql+asyncpg://postgres:{password}@{settings.DB_HOST or 'localhost'}:{settings.DB_PORT or 5432}/{settings.DB_NAME or 'mytube'}"


def get_async_engine():
    """Получить или создать единый AsyncEngine для всего приложения."""
    global _db_engine
    if _db_engine is None:
        _db_engine = create_async_engine(
            _get_db_url(),
            echo=False,
            pool_pre_ping=True,
        )
    return _db_engine


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения async session.

    Открывает и закрывает сессию. Не выполняет commit/rollback автоматически —
    это делает внешний код (или SQLAlchemy в зависимости от use_transaction).
    """
    engine = get_async_engine()
    async with async_sessionmaker(engine) as session:
        try:
            yield session
        finally:
            await session.close()
