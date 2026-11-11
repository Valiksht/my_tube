"""Модель сессии пользователя для БД.

Хранит идентификатор сессии, хеш, user_id и срок действия.
Используется для серверных сессий с HttpOnly Cookie.
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserSession(Base):
    """Сессия авторизованного пользователя.
    
    Каждая сессия привязана к одному пользователю и хранит
    криптографически случайный идентификатор (хеш).
    
    Поля:
        id: Первичный ключ.
        session_id: Хеш идентификатора сессии (хранится в БД,
            исходное значение — в HttpOnly Cookie).
        user_id: Ссылка на пользователя.
        created_at: Время создания сессии.
        expires_at: Время истечения сессии.
        is_active: Флаг активности сессии (можно отозвать).
        ip_address: IP адрес при создании сессии.
        user_agent: User-Agent браузера.
    """

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )
    session_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
        comment="Хеш идентификатора сессии",
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()"),
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Время истечения сессии",
    )
    is_active: Mapped[bool] = mapped_column(
        String(1),
        default="1",
        nullable=False,
        comment="Флаг активности (1=active, 0=revoked)",
    )
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45),
        nullable=True,
        comment="IPv4 или IPv6 адрес",
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="User-Agent браузера",
    )

    # Связь с пользователем
    user = relationship("User", back_populates="sessions")
