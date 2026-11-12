"""HTML-роутеры для страниц сайта."""

from fastapi import APIRouter

from app.api.pages.auth_pages import router as auth_pages_router
from app.api.pages.video_pages import router as video_pages_router
from app.api.pages.channel_pages import router as channel_pages_router
from app.api.pages.moderation_page import router as moderation_pages_router
from app.api.pages.subscriptions_pages import router as subscriptions_pages_router

pages_router = APIRouter()

pages_router.include_router(auth_pages_router)
pages_router.include_router(video_pages_router)
pages_router.include_router(channel_pages_router)
pages_router.include_router(moderation_pages_router)
pages_router.include_router(subscriptions_pages_router)
