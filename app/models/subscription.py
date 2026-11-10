"""Модель подписок."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Subscription:
    """Подписка пользователя на канал.

    Основные атрибуты:
    - subscribed_user_id: пользователь, который подписался
    - subscribed_channel_id: канал, на который подписались
    - notification_enabled: уведомления от канала включены или нет
    - created_at: когда оформлена подписка

    Таблица связывает пользователей и каналы (many-to-many).
    Пользователь может подписываться на много каналов.
    """

    __tablename__ = "subscriptions"

    # Поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    subscribed_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    subscribed_channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"),
        nullable=False,
        index=True
    )
    notification_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    subscribed_user: Mapped["User"] = relationship(
        "User", back_populates="subscriptions"
    )
    subscribed_channel: Mapped["Channel"] = relationship(
        "Channel", back_populates="subscribers"
    )

    def __init__(
        self,
        subscribed_user_id: int,
        subscribed_channel_id: int,
        notification_enabled: bool = True
    ):
        self.subscribed_user_id = subscribed_user_id
        self.subscribed_channel_id = subscribed_channel_id
        self.notification_enabled = notification_enabled
