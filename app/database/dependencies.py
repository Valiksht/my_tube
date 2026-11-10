"""Зависимости для работы с базой данных."""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Получить асинхронную сессию базы данных.

    Используется как зависимость FastAPI для эндпоинтов, которые работают с БД.
    
    Пример использования:
        @app.get("/items")
        async def read_items(db=Depends(get_db)):
            ...

    Автоматически обрабатывает commit и rollback при ошибках.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
