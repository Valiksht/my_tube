"""Модель пользователя."""

from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, Boolean, Text as SqlText
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
import secrets


class User:
    """Пользователь системы.

    Основные атрибуты:
    - username: уникальный логин пользователя
    - email: адрес электронной почты
    - hashed_password: хеш пароля
    - is_active: флаг активности аккаунта
    - created_at: время регистрации
    """

    __tablename__ = "users"

    # Поля таблицы
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    # Связи с другими таблицами
    videos: Mapped[list["Video"]] = relationship(
        "Video", back_populates="author", lazy="selectin"
    )
    likes: Mapped[list["Like"]] = relationship(
        "Like", back_populates="user", lazy="selectin"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="user", lazy="selectin"
    )

    def __init__(
        self,
        username: str,
        email: str,
        hashed_password: str,
        is_active: bool = True
    ):
        self.username = username
        self.email = email
        self.hashed_password = hashed_password
        self.is_active = is_active
        self.created_at = datetime.now(timezone.utc)

    @validates("username")
    def validate_username(self, key: str, username: str) -> str:
        """Валидация поля username."""
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters long.")
        return username.lower().strip()

    @validates("email")
    def validate_email(self, key: str, email: str) -> str:
        """Валидация поля email."""
        if "@" not in email:
            raise ValueError("Invalid email address.")
        return email.strip()
