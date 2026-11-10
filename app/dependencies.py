"""Дependencies для FastAPI."""

from sqlalchemy import select
from app.database import get_db


async def get_db():
    """Dependency для получения async session (будет реализовано на Этапе 2)."""
    pass


async def get_current_user():
    """Dependency для получения текущего пользователя (будет реализована на Этапе 2)."""
    pass


def get_current_admin():
    """Для проверки прав администратора (будет реализована на Этапе 2)."""
    pass
