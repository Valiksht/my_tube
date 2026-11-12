"""HTML-роутер для страницы модерации."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.csrf import generate_csrf_token
from app.database.dependencies import get_db
from app.dependencies import require_moderator_or_admin
from app.models.users import User
from app.models.video import Video
from app.models.comment import Comment
from app.services.moderation import ModerationService

router = APIRouter()


@router.get("/moderation", response_class=HTMLResponse)
async def moderation_page(
    request: Request,
    current_user: User = Depends(require_moderator_or_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Страница модерации."""
    service = ModerationService(db)
    reports = await service.get_pending_reports(skip=0, limit=100)

    csrf_token = getattr(request.state, "csrf_token", generate_csrf_token())

    report_details = []
    for report in reports:
        reporter = None
        video = None
        comment = None

        if report.target_type == "video":
            result = await db.execute(select(Video).where(Video.id == report.target_id))
            video = result.scalar_one_or_none()
        elif report.target_type == "comment":
            result = await db.execute(select(Comment).where(Comment.id == report.target_id))
            comment = result.scalar_one_or_none()

        result = await db.execute(select(User).where(User.id == report.reporter_id))
        reporter = result.scalar_one_or_none()

        report_details.append({
            "report": report,
            "reporter": reporter,
            "video": video,
            "comment": comment,
        })

    return request.app.templates.TemplateResponse("moderation.html", {
        "request": request,
        "current_user": current_user,
        "reports": report_details,
        "csrf_token": csrf_token,
    })
