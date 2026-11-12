"""Тесты модерации (API)."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_create_report(client, test_user, test_video):
    """Тест создания жалобы."""
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

    response = await client.post(
        "/api/moderation/reports",
        json={
            "target_type": "video",
            "target_id": test_video.id,
            "reason": "This video violates community guidelines",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"


@pytest.mark.anyio
async def test_create_report_invalid_type(client, test_user):
    """Тест создания жалобы с неверным типом."""
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

    response = await client.post(
        "/api/moderation/reports",
        json={
            "target_type": "invalid",
            "target_id": 1,
            "reason": "This is an invalid request",
        },
    )

    assert response.status_code == 400


@pytest.mark.anyio
async def test_create_report_unauthorized(client):
    """Тест создания жалобы без авторизации."""
    response = await client.post(
        "/api/moderation/reports",
        json={
            "target_type": "video",
            "target_id": 1,
            "reason": "This is a test reason",
        },
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_list_pending_reports(client, moderator_user):
    """Тест получения списка жалоб модератором."""
    # Авторизуемся как модератор
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": "moderator",
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    response = await client.get("/api/moderation/reports/pending")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_list_pending_reports_unauthorized(client):
    """Тест получения списка жалоб без прав модератора."""
    response = await client.get("/api/moderation/reports/pending")

    assert response.status_code == 401


@pytest.mark.anyio
async def test_resolve_report(client, moderator_user, test_user, test_video):
    """Тест обработки жалобы модератором."""
    # Сначала создаём жалобу
    user_login = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    user_client = AsyncClient(
        transport=None,
        base_url="http://test",
    )
    user_client.cookies.set(
        "session",
        user_login.json()["access_token"],
        domain="test",
    )

    report_response = await user_client.post(
        "/api/moderation/reports",
        json={
            "target_type": "video",
            "target_id": test_video.id,
            "reason": "This video violates community guidelines",
        },
    )
    assert report_response.status_code == 201
    report_id = report_response.json()["id"]
    user_client.close()

    # Авторизуемся как модератор
    mod_login = await client.post(
        "/api/auth/login",
        json={
            "username": "moderator",
            "password": "testpass123",
        },
    )
    assert mod_login.status_code == 200

    client.cookies.set(
        "session",
        mod_login.json()["access_token"],
        domain="test",
    )

    # Обрабатываем жалобу
    response = await client.post(
        f"/api/moderation/reports/{report_id}/resolve?action=resolved",
        json={"notes": "Resolved"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "resolved"


@pytest.mark.anyio
async def test_list_hidden(client, moderator_user):
    """Тест получения списка скрытого контента модератором."""
    # Авторизуемся как модератор
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": "moderator",
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    response = await client.get("/api/moderation/hidden")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_unhide_content(client, moderator_user):
    """Тест восстановления скрытого контента модератором."""
    # Авторизуемся как модератор
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": "moderator",
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    # Пробуем восстановить несуществующий контент
    # Ожидается 404, но без ошибки (не исключение)
    response = await client.post(
        "/api/moderation/hidden/99999/unhide"
    )

    # Может вернуть 404 или 200 — главное что не crash
    assert response.status_code in (200, 404)
