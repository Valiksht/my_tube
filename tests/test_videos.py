"""Тесты видео."""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.anyio
async def test_list_videos(client: AsyncClient, test_video):
    """Тест получения списка видео."""
    response = await client.get("/api/videos")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.anyio
async def test_get_video(client: AsyncClient, test_video):
    """Тест получения видео по ID."""
    response = await client.get(f"/api/videos/{test_video.id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_video.id
    assert data["title"] == "Test Video"
    assert data["privacy"] == "public"


@pytest.mark.anyio
async def test_get_video_not_found(client: AsyncClient):
    """Тест получения несуществующего видео."""
    response = await client.get("/api/videos/99999")
    assert response.status_code == 404


@pytest.mark.anyio
async def test_create_video(client: AsyncClient, test_user, test_channel):
    """Тест создания видео."""
    # Сначала авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    assert login_response.status_code == 200
    
    # Устанавливаем session cookie
    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )
    
    # Создаём видео
    response = await client.post(
        "/api/videos",
        json={
            "channel_id": test_channel.id,
            "title": "New Video",
            "description": "New description",
            "privacy": "public",
        },
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Video"
    assert data["channel_id"] == test_channel.id


@pytest.mark.anyio
async def test_create_video_unauthorized(client: AsyncClient):
    """Тест создания видео без авторизации."""
    response = await client.post(
        "/api/videos",
        json={
            "channel_id": 1,
            "title": "New Video",
        },
    )
    
    assert response.status_code == 401


@pytest.mark.anyio
async def test_update_video(client: AsyncClient, test_video, test_user, test_channel):
    """Тест обновления видео."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )
    
    # Обновляем видео
    response = await client.patch(
        f"/api/videos/{test_video.id}",
        json={"title": "Updated Title"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"


@pytest.mark.anyio
async def test_delete_video(client: AsyncClient, test_video, test_user, test_channel):
    """Тест удаления видео."""
    # Авторизуемся
    login_response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": "testpass123",
        },
    )
    client.cookies.set(
        "session",
        login_response.json()["access_token"],
        domain="test",
    )
    
    # Удаляем видео
    response = await client.delete(f"/api/videos/{test_video.id}")
    assert response.status_code == 204


@pytest.mark.anyio
async def test_search_videos(client: AsyncClient, test_video):
    """Тест поиска видео."""
    response = await client.get("/api/videos/search?q=Test")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
