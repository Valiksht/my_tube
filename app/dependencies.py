"""Dependencies for FastAPI."""


async def get_db():
    """Dependency для получения async session."""
    from app.database.session import get_async_session
    db = get_async_session()
    return db


async def get_current_user():
    """Dependency для получения текущего пользователя (будет реализована на Этапе 2)."""
    pass


def get_current_admin():
    """Для проверки прав администратора (будет реализована на Этапе 2)."""
    pass
