"""Модель лайков."""

from datetime import datetime, timezone
from sqlalchemy import Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Like:
    """Лайк на видео.

    Основные атрибуты:
    - video_id: связь с видео
    - user_id: кто поставил лайк
    - created_at: когда поставили лайк

    Это связующая таблица между User и Video (many-to-many).
    Каждый пользователь может поставить лайк только один раз на одно видео.
    """

    __tablename__ = "likes"

    # Поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id"),
        nullable=False,
        index=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    video: Mapped["Video"] = relationship(
        "Video", back_populates="likes"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="likes"
    )

    def __init__(self, video_id: int, user_id: int):
        self.video_id = video_id
        self.user_id = user_id
