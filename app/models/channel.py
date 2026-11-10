"""Модель видеоканала."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text as SqlText, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Channel:
    """Видео Канал пользователя.

    Основные атрибуты:
    - user_id: связь с пользователем (владелец канала)
    - name: название канала
    - description: описание канала
    - avatar_url: ссылка на аватарку
    - banner_url: ссылка на баннер
    - subscribers_count: количество подписчиков
    - video_count: количество видео в канале
    - created_at: время создания канала
    """

    __tablename__ = "channels"

    # Поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
        index=True
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(
        SqlText,
        default="Описание канала..."
    )
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    banner_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    subscribers_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    videos: Mapped[list["Video"]] = relationship(
        "Video", back_populates="channel", lazy="selectin"
    )
    subscribers: Mapped[list["Subscription"]] = relationship(
        "Subscription", back_populates="subscribed_channel", lazy="selectin"
    )

    def __init__(
        self,
        user_id: int,
        name: str,
        description: str = "",
        avatar_url: str | None = None,
        banner_url: str | None = None
    ):
        self.user_id = user_id
        self.name = name
        self.description = description
        self.avatar_url = avatar_url
        self.banner_url = banner_url
