"""Модель комментариев."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Comment:
    """Комментарий под видео.

    Основные атрибуты:
    - video_id: связь с видео
    - user_id: кто написал комментарий
    - content: текст комментария
    - created_at: когда написал комментарий

    Каждый пользователь может оставить много комментариев на разных видео.
    """

    __tablename__ = "comments"

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
    content: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    video: Mapped["Video"] = relationship(
        "Video", back_populates="comments"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="comments"
    )

    def __init__(
        self,
        video_id: int,
        user_id: int,
        content: str
    ):
        self.video_id = video_id
        self.user_id = user_id
        self.content = content
