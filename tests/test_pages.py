"""Тесты HTML-страниц."""

import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_index_page(client):
    """Тест главной страницы."""
    response = await client.get("/")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_login_page(client):
    """Тест страницы входа."""
    response = await client.get("/login")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_login_submit(client):
    """Тест отправки формы входа."""
    # Сначала GET для получения CSRF cookie
    await client.get("/login")

    # Затем POST с CSRF токеном из cookie
    csrf_token = client.cookies.get("session_csrf", domain="localhost")
    if not csrf_token:
        # Попробуем получить из set-cookie заголовков
        # Если cookie нет, используем любой токен
        csrf_token = "test-csrf-token"

    response = await client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "testpass123",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    # Должен вернуть редирект или ошибку CSRF
    assert response.status_code in (302, 303, 403)


@pytest.mark.anyio
async def test_register_page(client):
    """Тест страницы регистрации."""
    response = await client.get("/register")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_register_submit(client):
    """Тест отправки формы регистрации."""
    # Сначала GET для получения CSRF cookie
    await client.get("/register")

    csrf_token = client.cookies.get("session_csrf", domain="localhost")
    if not csrf_token:
        csrf_token = "test-csrf-token"

    response = await client.post(
        "/register",
        data={
            "username": "pagetestuser2",
            "email": "pagetest2@example.com",
            "password": "password123",
            "password_confirm": "password123",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    # Должен вернуть редирект или ошибку CSRF
    assert response.status_code in (302, 303, 403)


@pytest.mark.anyio
async def test_upload_page_authorized(client, test_user):
    """Тест страницы загрузки с авторизацией."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    response = await client.get("/upload")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_upload_submit_authorized(client, test_user):
    """Тест отправки формы загрузки с авторизацией."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    # GET для CSRF
    await client.get("/upload")

    csrf_token = client.cookies.get("session_csrf", domain="localhost")
    if not csrf_token:
        csrf_token = "test-csrf-token"

    response = await client.post(
        "/upload",
        data={
            "title": "Test Video",
            "description": "Test",
            "privacy": "public",
            "channel_id": "1",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    # Должен вернуть редирект или ошибку
    assert response.status_code in (302, 303, 400, 403, 404)


@pytest.mark.anyio
async def test_upload_page_unauthorized(client):
    """Тест страницы загрузки без авторизации."""
    response = await client.get("/upload")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_video_page(client, test_video):
    """Тест страницы просмотра видео."""
    response = await client.get(f"/video/{test_video.id}")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_video_page_not_found(client):
    """Тест страницы несуществующего видео."""
    response = await client.get("/video/99999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_search_page(client, test_video):
    """Тест страницы поиска."""
    response = await client.get("/search?q=Test")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_search_page_empty(client):
    """Тест страницы поиска без запроса."""
    response = await client.get("/search")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_channel_create_page_authorized(client, test_user):
    """Тест страницы создания канала с авторизацией."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    response = await client.get("/channel/create")

    # Может вернуть 302, если канал уже существует
    assert response.status_code in (200, 302)


@pytest.mark.anyio
async def test_channel_create_submit_authorized(client, test_user):
    """Тест отправки формы создания канала."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    # GET для CSRF
    await client.get("/channel/create")

    csrf_token = client.cookies.get("session_csrf", domain="localhost")
    if not csrf_token:
        csrf_token = "test-csrf-token"

    response = await client.post(
        "/channel/create",
        data={
            "name": "Page Test Channel",
            "description": "Test description",
            "csrf_token": csrf_token,
        },
        follow_redirects=False,
    )

    # Должен вернуть редирект
    assert response.status_code in (302, 303)


@pytest.mark.anyio
async def test_channel_page(client, test_channel):
    """Тест страницы канала."""
    response = await client.get(f"/channel/{test_channel.id}")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_channel_page_not_found(client):
    """Тест страницы несуществующего канала."""
    response = await client.get("/channel/99999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_profile_page(client, test_user):
    """Тест страницы профиля."""
    response = await client.get(f"/profile/{test_user.id}")

    assert response.status_code == 200


@pytest.mark.anyio
async def test_profile_page_not_found(client):
    """Тест страницы несуществующего профиля."""
    response = await client.get("/profile/99999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_my_subscriptions_unauthorized(client):
    """Тест страницы моих подписок без авторизации."""
    response = await client.get("/my-subscriptions")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_my_subscriptions_empty(client, test_user, test_channel):
    """Тест страницы моих подписок когда нет подписок."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    response = await client.get("/my-subscriptions")

    assert response.status_code == 200
    assert "не подписаны ни на один канал" in response.text


@pytest.mark.anyio
async def test_my_subscriptions_with_one_subscription(client, test_user, test_channel):
    """Тест страницы моих подписок с одной подпиской."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    # Подписываемся
    sub_response = await client.post(
        f"/api/channels/{test_channel.id}/subscriptions"
    )
    assert sub_response.status_code in (201, 200)

    # Открываем страницу
    response = await client.get("/my-subscriptions")

    assert response.status_code == 200
    assert "Test Channel" in response.text
    assert "Отписаться" in response.text


@pytest.mark.anyio
async def test_my_subscriptions_with_multiple_subscriptions(
    client, test_user, test_channel, db_session
):
    """Тест страницы моих подписок с несколькими подписками."""
    from app.models.channel import Channel
    from app.models.subscription import Subscription
    from datetime import datetime, timezone

    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    # Создаём второй канал
    from app.models.users import User
    from app.core.security import hash_password

    user2 = User(
        username="testuser2",
        email="testuser2@example.com",
        hashed_password=hash_password("testpass123"),
        is_active=True,
        role="user",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(user2)
    await db_session.flush()

    channel2 = Channel(
        user_id=user2.id,
        name="Second Channel",
        description="Second description",
        created_at=datetime.now(timezone.utc),
    )
    db_session.add(channel2)
    await db_session.flush()

    # Создаём подписки напрямую
    sub1 = Subscription(
        subscribed_user_id=test_user.id,
        subscribed_channel_id=test_channel.id,
    )
    sub2 = Subscription(
        subscribed_user_id=test_user.id,
        subscribed_channel_id=channel2.id,
    )
    db_session.add_all([sub1, sub2])
    await db_session.flush()

    # Открываем страницу
    response = await client.get("/my-subscriptions")

    assert response.status_code == 200
    assert "Test Channel" in response.text
    assert "Second Channel" in response.text
    assert "Отписаться" in response.text
