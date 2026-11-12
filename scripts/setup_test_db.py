"""Скрипт для создания тестовой базы данных.

Запускается перед выполнением тестов для подготовки
тестовой базы данных PostgreSQL.
"""

import asyncio
import asyncpg


TEST_DB_NAME = "mytube_db_test"
DB_HOST = "localhost"
DB_PORT = 5432
DB_USER = "postgres"
DB_PASSWORD = "postgres"
DEFAULT_DB = "postgres"


async def create_test_database():
    """Создать тестовую базу данных, если она не существует."""
    # Подключаемся к дефолтной базе postgres
    conn = await asyncpg.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DEFAULT_DB,
    )

    try:
        # Проверяем, существует ли тестовая база
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            TEST_DB_NAME,
        )

        if exists:
            print(f"База данных '{TEST_DB_NAME}' уже существует.")
            return

        # Создаём тестовую базу
        await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}"')
        print(f"База данных '{TEST_DB_NAME}' успешно создана.")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(create_test_database())
