"""Модерация: жалобы, скрытие видео, управление контентом.

Роли:
- user: может отправлять жалобы
- moderator: может скрывать видео/комментарии
- admin: полное управление
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, text, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Report(Base):
    """Жалоба на видео или комментарий.
    
    Поля:
        id: Первичный ключ.
        reporter_id: ID пользователя который пожаловался.
        target_type: Тип объекта ('video' или 'comment').
        target_id: ID объекта на который жалоба.
        reason: Причина жалобы.
        status: Статус обработки ('pending', 'reviewing', 'resolved', 'rejected').
        created_at: Время создания жалобы.
        moderator_id: ID модератора который обработал.
        resolved_at: Время обработки.
        moderator_notes: Заметки модератора.
    """
    
    __tablename__ = "reports"
    
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    reporter_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="'video' или 'comment'",
    )
    target_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="ID объекта на который жалоба",
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False,
        comment="'pending', 'reviewing', 'resolved', 'rejected'",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )
    moderator_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    moderator_notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    
    # Связи
    reporter = relationship("User", foreign_keys=[reporter_id])
    moderator = relationship("User", foreign_keys=[moderator_id])


class HiddenContent(Base):
    """Скрытый контент.
    
    Модераторы могут скрывать видео или комментарии.
    Это логическое удаление - контент остаётся в БД но скрыт от пользователей.
    
    Поля:
        id: Первичный ключ.
        content_type: Тип контента ('video' или 'comment').
        content_id: ID скрытого контента.
        moderator_id: ID модератора который скрыл.
        reason: Причина скрытия.
        hidden_at: Время скрытия.
    """
    
    __tablename__ = "hidden_content"
    
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    content_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="'video' или 'comment'",
    )
    content_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    moderator_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    hidden_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )
    
    # Связи
    moderator = relationship("User")
