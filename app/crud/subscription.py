"""CRUD операции для подписок."""

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseRepository
from app.models.subscription import Subscription


class SubscriptionRepository(BaseRepository[Subscription]):
    """Репозиторий для подписок."""
    
    async def get_subscription(
        self,
        db: AsyncSession,
        subscribed_user_id: int,
        subscribed_channel_id: int,
    ) -> Subscription | None:
        """Получить подписку пользователя на канал."""
        return await self.get_by(
            db,
            subscribed_user_id=subscribed_user_id,
            subscribed_channel_id=subscribed_channel_id,
        )
    
    async def get_user_subscriptions(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """Получить подписки пользователя с жадной загрузкой каналов."""
        query = (
            select(self.model)
            .where(self.model.subscribed_user_id == user_id)
            .options(selectinload(self.model.subscribed_channel))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_channel_subscribers(
        self,
        db: AsyncSession,
        channel_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """Получить подписчиков канала."""
        return await self.get_all(
            db,
            skip=skip,
            limit=limit,
            subscribed_channel_id=channel_id,
        )
    
    async def create_subscription(
        self,
        db: AsyncSession,
        subscribed_user_id: int,
        subscribed_channel_id: int,
    ) -> Subscription:
        """Создать подписку."""
        return await self.create(db, {
            "subscribed_user_id": subscribed_user_id,
            "subscribed_channel_id": subscribed_channel_id,
        })
    
    async def remove_subscription(
        self,
        db: AsyncSession,
        subscription: Subscription,
    ) -> None:
        """Удалить подписку."""
        await self.remove(db, subscription)


subscription_repo = SubscriptionRepository(Subscription)
