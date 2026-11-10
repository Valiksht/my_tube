"""Async session management."""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

_db_engine = None


def _get_db_url() -> str:
    """Получить URL подключения к базе данных."""
    return f"postgresql+asyncpg://postgres:{settings.DB_PASSWORD}@postgres:5432/mytube"


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
