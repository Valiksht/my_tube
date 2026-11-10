"""Базовый класс SQLAlchemy для всех моделей."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy.

    Этот класс автоматически создаёт таблицы в базе данных при запуске приложения.
    Все модели должны наследоваться от этого класса (явно или через Mixin).
    """
    pass