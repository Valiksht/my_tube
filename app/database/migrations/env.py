"""Environment configuration for alembic migrations."""
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.database.session import get_async_engine
from app.models.base import Base

context = None


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = "postgresql+asyncpg://postgres:mytubesecurepassword123!@localhost:5432/mytube"
    context.configure(
        url=url,
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = get_async_engine()

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=Base.metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if __name__ == "__main__":
    from alembic import config
    alembic_cfg = config.Config()
    alembic_cfg.set_main_option('sqlalchemy.url', 'postgresql+asyncpg://postgres:mytubesecurepassword123!@localhost:5432/mytube')
    if context.config.config_file_name:
        fileConfig(context.config.config_file_name)
    elif 'alembic.ini' in locals():
        fileConfig('alembic.ini')