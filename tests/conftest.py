"""Конфигурация тестов.

Использует тестовую базу данных и fixtures для pytest.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.database.dependencies import get_db
from app.core.config import get_settings

# Отключить кэш Jinja2 для тестов.
# LRU cache не может хешировать контекст с request (unhashable type: 'dict').
# Заменяем Jinja2Templates на новый без кэша.
from starlette.templating import Jinja2Templates
import app.main as main_module
main_module.templates = Jinja2Templates(directory="app/templates")

# Тестовая база данных
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost/mytube_db_test"

# Создаём движок для тестов
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def anyio_backend():
    """Бэкенд для асинхронных тестов."""
    return "asyncio"


@pytest.fixture(scope="session")
async def db_session():
    """Тестовая сессия базы данных."""
    from app.models.base import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with async_session() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session):
    """Тестовый клиент FastAPI."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def test_user(db_session):
    """Тестовый пользователь."""
    from app.core.security import hash_password
    from app.models.users import User
    from datetime import datetime, timezone
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hash_password("testpass123"),
        is_active=True,
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    
    return user


@pytest.fixture
async def test_channel(db_session, test_user):
    """Тестовый канал."""
    from app.models.channel import Channel
    from datetime import datetime, timezone
    
    channel = Channel(
        user_id=test_user.id,
        name="Test Channel",
        description="Test description",
        created_at=datetime.now(timezone.utc),
    )
    
    db_session.add(channel)
    await db_session.flush()
    await db_session.refresh(channel)
    
    return channel


@pytest.fixture
async def test_video(db_session, test_channel):
    """Тестовое видео."""
    from app.models.video import Video
    from datetime import datetime, timezone
    from app.models.enum import VideoPrivacy
    
    video = Video(
        channel_id=test_channel.id,
        title="Test Video",
        description="Test description",
        privacy=VideoPrivacy.PUBLIC.value,
        is_published=True,
        duration=120,
        view_count=0,
        created_at=datetime.now(timezone.utc),
    )
    
    db_session.add(video)
    await db_session.flush()
    await db_session.refresh(video)
    
    return video
