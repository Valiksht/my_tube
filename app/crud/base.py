"""Базовый класс репозитория для CRUD операций.

Предоставляет общие методы для работы с любой таблицей БД.
"""

from typing import Any, Generic, Sequence, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Базовый репозиторий для CRUD операций.
    
    Args:
        model: SQLAlchemy модель для работы.
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model
    
    async def get_by_id(
        self, 
        id: int, 
        db: AsyncSession,
        **kwargs: Any,
    ) -> ModelType | None:
        """Получить запись по ID.
        
        Args:
            id: Первичный ключ.
            db: AsyncSession.
            **kwargs: Дополнительные условия фильтрации.
            
        Returns:
            Запись или None.
        """
        query = select(self.model).where(
            self.model.id == id,
            **kwargs,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        **kwargs: Any,
    ) -> Sequence[ModelType]:
        """Получить список записей.
        
        Args:
            db: AsyncSession.
            skip: Сколько записей пропустить.
            limit: Максимум записей.
            **kwargs: Условия фильтрации.
            
        Returns:
            Список записей.
        """
        query = select(self.model).where(**kwargs).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()
    
    async def create(
        self,
        db: AsyncSession,
        obj_data: dict[str, Any],
    ) -> ModelType:
        """Создать новую запись.
        
        Args:
            db: AsyncSession.
            obj_data: Данные для создания.
            
        Returns:
            Созданная запись.
        """
        obj = self.model(**obj_data)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj
    
    async def update(
        self,
        db: AsyncSession,
        obj: ModelType,
        obj_data: dict[str, Any],
    ) -> ModelType:
        """Обновить запись.
        
        Args:
            db: AsyncSession.
            obj: Объект для обновления.
            obj_data: Новые данные.
            
        Returns:
            Обновлённый объект.
        """
        for key, value in obj_data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        await db.flush()
        await db.refresh(obj)
        return obj
    
    async def remove(
        self,
        db: AsyncSession,
        obj: ModelType,
    ) -> None:
        """Удалить запись.
        
        Args:
            db: AsyncSession.
            obj: Объект для удаления.
        """
        await db.delete(obj)
        await db.flush()
    
    async def get_by(self, db: AsyncSession, **kwargs: Any) -> ModelType | None:
        """Получить первую запись по условиям.
        
        Args:
            db: AsyncSession.
            **kwargs: Условия фильтрации.
            
        Returns:
            Первая найденная запись или None.
        """
        query = select(self.model).where(**kwargs)
        result = await db.execute(query)
        return result.scalar_one_or_none()
