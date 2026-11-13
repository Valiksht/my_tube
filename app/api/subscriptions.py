"""API роутеры для подписок."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.dependencies import get_current_user
from app.schemas.subscription import SubscriptionResponse
from app.services.subscription import SubscriptionService
from app.models.users import User

router = APIRouter(
    prefix="/channels/{channel_id}/subscriptions",
    tags=["subscriptions"],
)


@router.post("")
async def toggle_subscription(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Переключить подписку на канал."""

    service = SubscriptionService(db)

    is_subscribed = await service.toggle_subscription(
        subscribed_user_id=current_user.id,
        subscribed_channel_id=channel_id,
    )

    count = await service.get_channel_subscriber_count(
        channel_id=channel_id,
    )

    return {
        "channel_id": channel_id,
        "is_subscribed": is_subscribed,
        "subscriber_count": count,
    }


@router.get("/status")
async def get_subscription_status(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Проверить подписку пользователя на канал."""
    service = SubscriptionService(db)
    
    is_subscribed = await service.is_subscribed(
        subscribed_user_id=current_user.id,
        subscribed_channel_id=channel_id,
    )
    
    return {"is_subscribed": is_subscribed}


@router.get("/count")
async def get_subscriber_count(
    channel_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Получить количество подписчиков канала."""
    service = SubscriptionService(db)
    
    count = await service.get_channel_subscriber_count(
        channel_id=channel_id,
    )
    
    return {"subscriber_count": count}


@router.get("", response_model=list[SubscriptionResponse])
async def list_subscribers(
    channel_id: int,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """Получить список подписчиков канала."""
    service = SubscriptionService(db)
    
    subscribers = await service.get_channel_subscribers(
        channel_id=channel_id,
        skip=skip,
        limit=limit,
    )
    
    return subscribers
