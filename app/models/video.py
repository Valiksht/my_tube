"""Модель видео."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Text as SqlText, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


# Перечисление для статуса приватности видео
class VideoPrivacy(str, enum.Enum):
    """Типы приватности видео."""
    PUBLIC = "public"       # Публичное видео для всех
    UNLISTED = "unlisted"   # Не добавлено в каталог, но доступно по ссылке
    PRIVATE = "private"     # Доступно только для авторизованных пользователей


class Video:
    """Видео на YouTube канале.

    Основные атрибуты:
    - channel_id: связь с каналом (автор)
    - title: название видео
    - description: описание видео
    - video_url: прямая ссылка на видеофайл в объектном хранилище
    - thumbnail_url: ссылка на превью/скриншот
    - duration: длительность видео в секундах
    - view_count: количество просмотров
    - like_count: количество лайков
    - comment_count: количество комментариев
    - privacy: статус приватности (public/unlisted/private)
    - is_published: флаг публикации
    - created_at: время загрузки
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
    like_count: Mapped[int] = mapped_column(Integer, default=0)
    comment_count: Mapped[int] = mapped_column(Integer, default=0)
    privacy: Mapped[str] = mapped_column(
        String(10),
        default="public",
        nullable=False
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    author: Mapped["Channel"] = relationship(
        "Channel", back_populates="videos"
    )
    likes: Mapped[list["Like"]] = relationship(
        "Like", back_populates="video", lazy="selectin"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="video", lazy="selectin"
    )

    def __init__(
        self,
        channel_id: int,
        title: str,
        description: str = "",
        video_url: str | None = None,
        thumbnail_url: str | None = None,
        duration: int = 0,
        privacy: str = "public",
        is_published: bool = True
    ):
        self.channel_id = channel_id
        self.title = title
        self.description = description
        self.video_url = video_url
        self.thumbnail_url = thumbnail_url
        self.duration = duration
        self.privacy = privacy.lower()
        self.is_published = is_published
