"""HTML-роутеры для страницы «Мои подписки»."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.csrf import generate_csrf_token
from app.database.dependencies import get_db
from app.dependencies import get_current_user
from app.models.users import User
from app.services.subscription import SubscriptionService

router = APIRouter()


@router.get("/my-subscriptions", response_class=HTMLResponse)
async def my_subscriptions_page(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Страница «Мои подписки» — список каналов, на которые подписан пользователь."""

    sub_service = SubscriptionService(db)
    subscriptions = await sub_service.get_user_subscriptions(
        user_id=current_user.id, skip=0, limit=100,
    )

    # Извлекаем каналы из подписок и сортируем по имени (алфавитный порядок)
    channels = [
        sub.subscribed_channel
        for sub in subscriptions
        if sub.subscribed_channel is not None
    ]
    channels.sort(key=lambda ch: ch.name.lower())

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    return request.app.templates.TemplateResponse("my_subscriptions.html", {
        "request": request,
        "current_user": current_user,
        "channels": channels,
        "csrf_token": csrf_token,
    })
