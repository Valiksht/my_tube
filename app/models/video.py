__all__ = ["Video", "VideoPrivacy"]
"""Модель видео."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.channel import Channel
from app.models.like import Like
from app.models.comment import Comment
from app.models.enum import VideoPrivacy


class Video:
    """Видео загруженное на канал YouTube Clone.

    Основные атрибуты:
    - channel_id: внешний ключ к таблице channels (автор канала)
    - title: название видео (обязательное)
    - description: описание видео (опциональное, пустая строка по умолчанию)
    - video_url: URL файла видео в объектном хранилище (например MinIO/S3)
    - thumbnail_url: URL превью видео (опционально)
    - duration: длительность видео в секундах
    - view_count: количество просмотров видео
    - privacy: статус приватности видео (PUBLIC/UNLISTED/PRIVATE через Enum)
    - is_published: флаг публикации для публичных видео

    Связи с другими таблицами:
    - channel → Автор канала (One-to-Many)
    - likes   → Лайки от пользователей (Many-to-Many)
    - comments→ Комментарии под видео (One-to-Many)

    Примечания:
    - author переименован в channel для согласования именовании связей
    - like_count и comment_count удалены - подсчитываются через SQLAlchemy relationships
    - privacy использует Python Enum VideoPrivacy со значениями "public", "unlisted", "private"
    - duration, view_count должны быть >= 0 (валидация на уровне приложения)
    - Не содержит собственного __init__ - инициализация через Pydantic Schemas
    """

    __tablename__ = "videos"

    # Поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"),
        nullable=False,
        index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    video_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    duration: Mapped[int] = mapped_column(Integer, default=0)
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    privacy: Mapped[str] = mapped_column(
        String(10),
        default=VideoPrivacy.PUBLIC.value,
        nullable=False
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    channel: Mapped["Channel"] = relationship(
        "Channel", back_populates="videos"
    )
    likes: Mapped[list["Like"]] = relationship(
        "Like", back_populates="video", lazy="selectin"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="video", lazy="selectin"
    )