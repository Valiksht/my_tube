__all__ = ["Channel"]
"""Модель видеоканала."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.models.base import Base


class Channel(Base):
    """Видео-канал пользователя YouTube Clone.

    Каждый пользователь может иметь только один канал (One-to-One связь с User).
    
    Основные атрибуты:
    - user_id: уникальный внешний ключ к таблице users (на один канал приходится один user)
    - name: название канала (публичное имя канала)
    - description: описание содержания канала
    - avatar_url: URL аватарки канала
    - banner_url: URL баннера канала
    - created_at: время создания канала

    Связи с другими таблицами:
    - user        → Обратная связь от владельца канала (One-to-One)
    - videos      → Видео загруженные на канал (One-to-Many)
    - subscribers → Подписчики канала через таблицу Subscription (One-to-Many)

    Примечания:
    - subscribers_count удален - для получения количества подписчиков используем count() из связи subscribers
    - video_count удален - для получения количества видео используем count() из связи videos
    - description использует Text с пустым дефолтным значением ""
    """

    __tablename__ = "channels"

    # Поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,  # Один канал на пользователя
        nullable=False,
        index=True
        # ondelete удалён — не используется при импорте без БД
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=""  # Пустая строка по умолчанию
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    banner_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    user: Mapped["User"] = relationship(  # Обратная связь от User
        "User",
        back_populates="channel"
    )
    videos: Mapped[list["Video"]] = relationship(
        "Video",
        back_populates="channel",
        lazy="selectin"
    )
    subscribers: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="subscribed_channel",
        lazy="selectin"
    )


__all__ = ["Channel"]
"""Модель видеоканала."""
