"""Базовый класс SQLAlchemy для всех моделей."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy.

    Этот класс автоматически создаёт metadata для миграций Alembic.
    Все модели должны наследоваться от этого класса (явно или через Mixin).
    """
# Экспортируем metadata для миграций Alembic
metadata = Base.metadata  # noqa: F811
__all__ = ["metadata"]
