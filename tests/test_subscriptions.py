"""Тесты подписок."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_toggle_subscription(client, test_user, test_channel):
    """Тест переключения подписки."""
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
    response = await client.post(
        f"/api/channels/{test_channel.id}/subscriptions"
    )

    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.anyio
async def test_toggle_subscription_again(client, test_user, test_channel):
    """Тест повторного переключения подписки (отписаться)."""
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
    await client.post(f"/api/channels/{test_channel.id}/subscriptions")

    # Отписываемся
    response = await client.post(
        f"/api/channels/{test_channel.id}/subscriptions"
    )

    # Должен вернуть 200 (подписка снята)
    assert response.status_code == 200


@pytest.mark.anyio
async def test_subscription_status(client, test_user, test_channel):
    """Тест проверки статуса подписки."""
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
    await client.post(f"/api/channels/{test_channel.id}/subscriptions")

    # Проверяем статус
    response = await client.get(
        f"/api/channels/{test_channel.id}/subscriptions/status"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_subscribed"] is True


@pytest.mark.anyio
async def test_subscription_count(client, test_user, test_channel):
    """Тест получения количества подписчиков."""
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
    await client.post(f"/api/channels/{test_channel.id}/subscriptions")

    # Получаем количество
    response = await client.get(
        f"/api/channels/{test_channel.id}/subscriptions/count"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["subscriber_count"] >= 1


@pytest.mark.anyio
async def test_list_subscribers(client, test_user, test_channel):
    """Тест получения списка подписчиков."""
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
    await client.post(f"/api/channels/{test_channel.id}/subscriptions")

    # Получаем список
    response = await client.get(
        f"/api/channels/{test_channel.id}/subscriptions"
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_subscription_status_unauthorized(client, test_channel):
    """Тест проверки статуса подписки без авторизации."""
    response = await client.get(
        f"/api/channels/{test_channel.id}/subscriptions/status"
    )

    assert response.status_code == 401
