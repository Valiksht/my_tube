"""API роутеры для модерации.

Жалобы, скрытие видео/комментариев, панель модератора.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dependencies import get_db
from app.dependencies import get_current_user, require_moderator_or_admin
from app.models.users import User
from app.schemas.video import VideoResponse
from app.schemas.comment import CommentResponse

router = APIRouter(prefix="/moderation", tags=["moderation"])


class ReportCreate(BaseModel):
    """Схема для создания жалобы."""
    target_type: str = Field(..., description="'video' или 'comment'")
    target_id: int = Field(..., description="ID объекта")
    reason: str = Field(..., min_length=10, description="Причина жалобы")


@router.post("/reports", status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать жалобу от пользователя."""
    from app.services.moderation import ModerationService
    
    if report_data.target_type not in ["video", "comment"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="target_type must be 'video' or 'comment'",
        )
    
    service = ModerationService(db)
    report = await service.create_report(
        reporter_id=current_user.id,
        target_type=report_data.target_type,
        target_id=report_data.target_id,
        reason=report_data.reason,
    )
    
    return {
        "id": report.id,
        "status": report.status,
    }


@router.get("/reports/pending")
async def list_pending_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_moderator_or_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Получить жалобы на модерацию."""
    from app.services.moderation import ModerationService
    
    service = ModerationService(db)
    reports = await service.get_pending_reports(skip=skip, limit=limit)
    
    return [
        {
            "id": report.id,
            "reporter_id": report.reporter_id,
            "target_type": report.target_type,
            "target_id": report.target_id,
            "reason": report.reason,
            "status": report.status,
            "created_at": report.created_at.isoformat(),
        }
        for report in reports
    ]


class ReportResolve(BaseModel):
    """Схема для решения жалобы."""
    notes: str = ""


@router.post("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: int,
    action: str = Query(..., description="'resolved' или 'rejected'"),
    resolve_data: ReportResolve | None = None,
    current_user: User = Depends(require_moderator_or_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Обработать жалобу."""
    from app.services.moderation import ModerationService
    
    if action not in ["resolved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Action must be 'resolved' or 'rejected'",
        )
    
    notes = resolve_data.notes if resolve_data else ""
    
    service = ModerationService(db)
    report = await service.resolve_report(
        report_id=report_id,
        moderator_id=current_user.id,
        action=action,
        notes=notes,
    )
    
    return {
        "id": report.id,
        "status": report.status,
        "resolved_at": report.resolved_at,
    }


@router.get("/hidden")
async def list_hidden_content(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_moderator_or_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Получить список скрытого контента."""
    from app.services.moderation import ModerationService
    
    service = ModerationService(db)
    hidden = await service.get_hidden_content(skip=skip, limit=limit)
    
    return [
        {
            "id": item.id,
            "content_type": item.content_type,
            "content_id": item.content_id,
            "reason": item.reason,
            "hidden_at": item.hidden_at.isoformat(),
        }
        for item in hidden
    ]


@router.post("/hidden/{content_id}/unhide")
async def unhide_content(
    content_id: int,
    current_user: User = Depends(require_moderator_or_admin()),
    db: AsyncSession = Depends(get_db),
):
    """Восстановить скрытый контент."""
    from app.services.moderation import ModerationService
    
    service = ModerationService(db)
    await service.unhide_content(
        content_id=content_id,
        moderator_id=current_user.id,
    )
    
    return {"status": "ok"}
