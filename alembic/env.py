import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Импортируем все модели, чтобы populate metadata для autogenerate
import app.models.users       # noqa: F401
import app.models.channel     # noqa: F401
import app.models.video       # noqa: F401
import app.models.like        # noqa: F401
import app.models.comment     # noqa: F401
import app.models.subscription  # noqa: F401
import app.models.session     # noqa: F401
import app.models.moderation  # noqa: F401

from app.models.base import metadata

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = metadata


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

    # Читаем DATABASE_URL из переменных окружения,
    # иначе используем URL из alembic.ini
    database_url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if not database_url:
        raise RuntimeError("DATABASE_URL not set. Check .env file or alembic.ini")

    connectable: AsyncEngine = create_async_engine(
        database_url,
        echo=False,
        pool_size=1,
        max_overflow=0,
    )

    async def do_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(_run_migrations_sync)

        await connectable.dispose()

    import asyncio
    asyncio.run(do_migrations())


def _run_migrations_sync(connection) -> None:
    """Синхронные миграции внутри async-контекста.

    connection.run_sync() извлекает синхронный Connection
    из AsyncConnection, поэтому context.begin_transaction()
    возвращает обычный sync-контекстменеджер.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
