"""Вспомогательные функции для seed_data.py.

Содержит TARGET_MODELS и ensure_database_is_empty().
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.models.comment import Comment
from app.models.like import Like
from app.models.subscription import Subscription
from app.models.users import User
from app.models.video import Video

# ---------------------------------------------------------------------------
# Модели для проверки пустоты базы данных
# ---------------------------------------------------------------------------

TARGET_MODELS = (
    User,
    Channel,
    Video,
    Comment,
    Like,
    Subscription,
)


async def ensure_database_is_empty(session: AsyncSession) -> None:
    """Запретить заполнение, если целевые таблицы уже содержат данные."""
    for model in TARGET_MODELS:
        result = await session.scalar(
            select(model.id).limit(1)
        )

        if result is not None:
            raise RuntimeError(
                f"Таблица '{model.__tablename__}' уже содержит данные. "
                "Заполнение отменено во избежание конфликтов. "
                "Используйте пустую dev-базу данных."
            )
