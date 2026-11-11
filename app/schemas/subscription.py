"""Pydantic схемы для подписок."""

from datetime import datetime

from pydantic import BaseModel, Field


class SubscriptionResponse(BaseModel):
    """Ответ с данными подписки."""
    
    id: int
    subscribed_user_id: int
    subscribed_channel_id: int
    notification_enabled: bool
    created_at: datetime
    
    model_config = {"from_attributes": True}
