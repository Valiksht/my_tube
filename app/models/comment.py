__all__ = ["Comment"]
"""Модель комментариев."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from app.models.base import Base


class Comment(Base):
    """Комментарий под видео.

    Основные атрибуты:
    - video_id: связь с видео
    - user_id: кто написал комментарий
    - content: текст комментария
    - created_at: когда написал комментарий

    Связи с другими таблицами:
    - video → Видео которому написан комментарий
    - user  → Пользователь написавший комментарий
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


__all__ = ["Comment"]
"""Модель комментариев."""