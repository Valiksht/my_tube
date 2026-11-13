"""Сервисы для работы с подписками.

Бизнес-логика: подписка/отписка, проверка подписки, список подписчиков.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.subscription import subscription_repo
from app.models.subscription import Subscription


class SubscriptionService:
    """Сервис для работы с подписками."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def toggle_subscription(
        self,
        subscribed_user_id: int,
        subscribed_channel_id: int,
    ) -> bool:
        """Переключить подписку на канал.

        True — пользователь подписан.
        False — пользователь отписан.
        """

        existing = await subscription_repo.get_subscription(
            self.db,
            subscribed_user_id=subscribed_user_id,
            subscribed_channel_id=subscribed_channel_id,
        )

        if existing:
            await subscription_repo.remove_subscription(
                self.db,
                existing,
            )
            return False

        await subscription_repo.create_subscription(
            self.db,
            subscribed_user_id=subscribed_user_id,
            subscribed_channel_id=subscribed_channel_id,
        )

        return True
    
    async def is_subscribed(
        self,
        subscribed_user_id: int,
        subscribed_channel_id: int,
    ) -> bool:
        """Проверить подписку пользователя на канал.
        
        Args:
            subscribed_user_id: ID пользователя.
            subscribed_channel_id: ID канала.
            
        Returns:
            True если пользователь подписан.
        """
        subscription = await subscription_repo.get_subscription(
            self.db,
            subscribed_user_id=subscribed_user_id,
            subscribed_channel_id=subscribed_channel_id,
        )
        return subscription is not None
    
    async def get_user_subscriptions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """Получить подписки пользователя."""
        return await subscription_repo.get_user_subscriptions(
            self.db,
            user_id=user_id,
            skip=skip,
            limit=limit,
        )
    
    async def get_channel_subscribers(
        self,
        channel_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Subscription]:
        """Получить подписчиков канала."""
        return await subscription_repo.get_channel_subscribers(
            self.db,
            channel_id=channel_id,
            skip=skip,
            limit=limit,
        )
    
    async def get_channel_subscriber_count(
        self,
        channel_id: int,
    ) -> int:
        """Получить количество подписчиков канала."""
        from sqlalchemy import func, select
        
        query = (
            select(func.count())
            .select_from(Subscription)
            .where(Subscription.subscribed_channel_id == channel_id)
        )
        result = await self.db.execute(query)
        return result.scalar() or 0

