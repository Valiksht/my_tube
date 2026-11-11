from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

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
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine
    
    database_url = config.get_main_option("sqlalchemy.url")
    if not database_url:
        return

    engine = create_async_engine(
        database_url,
        echo=False,
        pool_size=1,
        max_overflow=0,
    )

    async def do_migrate():
        conn = await engine.connect()
        try:
            context.configure(
                connection=conn,
                target_metadata=target_metadata,
                compare_type=True,
                render_as_batch=True,
            )
            
            with context.begin_transaction():
                context.run_migrations()
        finally:
            await conn.close()

    asyncio.run(do_migrate())


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
