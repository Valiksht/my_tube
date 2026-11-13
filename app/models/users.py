__all__ = ["User"]
"""Модель пользователя."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Boolean, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base
from app.models.enum import UserRole


class User(Base):
    """Пользователь системы YouTube Clone.

    Основные атрибуты:
    - username: уникальный логин пользователя (минимум 3 символа)
    - email: адрес электронной почты (содержит @)
    - hashed_password: хеш пароля (BCrypt или Argon2)
    - is_active: флаг активности аккаунта
    - role: роль пользователя (user/moderator/admin)
    - created_at: время регистрации

    Связи с другими таблицами:
    - channel      → Один User имеет один Channel (One-to-One)
    - likes        → Пользователь может ставить лайки на видео (Many-to-Many через Like)
    - comments     → Пользователь пишет комментарии (Many-to-Many через Comment)
    - subscriptions → Пользователь подписан на каналы (Many-to-Many через Subscription)

    Примечания:
    - role использует UserRole.Enum со значениями "user", "moderator", "admin"
    - created_at использует server_default=text("now()")
    """

    __tablename__ = "users"

    # Поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Логин пользователя (минимум 3 символа)"
    )
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Email адрес пользователя"
    )
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(
        String(20),
        default=UserRole.USER.value,  # По умолчанию user
        nullable=False,
        index=True,
        comment="Роль пользователя (user/moderator/admin)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    channel: Mapped["Channel"] = relationship(
        "Channel",
        back_populates="user"  # Обратная связь из Channel
    )
    likes: Mapped[list["Like"]] = relationship(
        "Like",
        back_populates="user",
        lazy="selectin"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        back_populates="user",
        lazy="selectin"
    )
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="subscribed_user",
        lazy="selectin"
    )
    sessions: Mapped[list["UserSession"]] = relationship(
        "UserSession",
        back_populates="user",
        lazy="selectin",
        foreign_keys="UserSession.user_id",
    )

