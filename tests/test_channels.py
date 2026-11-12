"""Тесты каналов (API)."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_get_my_channel(client, test_user, test_channel):
    """Тест получения моего канала."""
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

    response = await client.get("/api/channels/me")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Channel"
    assert data["user_id"] == test_user.id


@pytest.mark.anyio
async def test_get_my_channel_no_channel(client, test_user):
    """Тест получения канала, если канал не создан."""
    # Создаём пользователя без канала
    from app.core.security import hash_password
    from app.models.users import User
    from datetime import datetime, timezone

    # Получаем сессию из клиента и создаём пользователя напрямую
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "nouuser",
            "email": "nou@example.com",
            "password": "password123",
        },
    )
    assert response.status_code == 201

    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": "nouuser",
            "password": "password123",
        },
    )
    assert login_response.status_code == 200

    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )

    # Пытаемся получить канал
    response = await client.get("/api/channels/me")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_channel(client, test_user):
    """Тест создания канала."""
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
        "/api/channels",
        json={
            "name": "My New Channel",
            "description": "Description",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My New Channel"
    assert "id" in data


@pytest.mark.anyio
async def test_create_channel_duplicate(client, test_user, test_channel):
    """Тест создания дублирующегося канала."""
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

    # Пытаемся создать второй канал
    response = await client.post(
        "/api/channels",
        json={
            "name": "Duplicate Channel",
            "description": "Desc",
        },
    )

    assert response.status_code == 409


@pytest.mark.anyio
async def test_create_channel_unauthorized(client):
    """Тест создания канала без авторизации."""
    response = await client.post(
        "/api/channels",
        json={
            "name": "Hacker Channel",
            "description": "Desc",
        },
    )

    assert response.status_code == 401


@pytest.mark.anyio
async def test_update_channel(client, test_user, test_channel):
    """Тест обновления канала."""
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

    response = await client.patch(
        "/api/channels/me",
        json={"name": "Updated Channel Name"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Channel Name"


@pytest.mark.anyio
async def test_get_channel(client, test_channel):
    """Тест получения канала по ID."""
    response = await client.get(f"/api/channels/{test_channel.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Channel"


@pytest.mark.anyio
async def test_get_channel_not_found(client):
    """Тест получения несуществующего канала."""
    response = await client.get("/api/channels/99999")

    assert response.status_code == 404


@pytest.mark.anyio
async def test_get_channel_videos(client, test_channel, test_video):
    """Тест получения видео канала."""
    response = await client.get(f"/api/channels/{test_channel.id}/videos")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.anyio
async def test_get_channel_videos_not_found(client):
    """Тест получения видео несуществующего канала."""
    response = await client.get("/api/channels/99999/videos")

    assert response.status_code == 404
