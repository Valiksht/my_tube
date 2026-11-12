"""API модуль приложения.

Подключает все API-роутеры к главному приложению.
HTML-роутеры подключаются отдельно без префикса /api.
"""

from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.videos import router as videos_router
from app.api.likes import router as likes_router
from app.api.subscriptions import router as subscriptions_router
from app.api.channels import router as channels_router
from app.api.moderation import router as moderation_router

router = APIRouter()

# Подключаем только API-роутеры
router.include_router(auth_router)
router.include_router(videos_router)
router.include_router(likes_router)
router.include_router(subscriptions_router)
router.include_router(channels_router)
router.include_router(moderation_router)

# HTML-роутеры экспортируются отдельно
from app.api.pages import pages_router  # noqa: E402

__all__ = ["router", "pages_router"]
