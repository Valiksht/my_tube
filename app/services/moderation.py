"""Сервисы модерации.

Жалобы, скрытие контента, управление модерацией.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.moderation import Report, HiddenContent
from app.models.users import User
from app.models.video import Video
from app.models.comment import Comment


class ModerationService:
    """Сервис модерации."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_report(
        self,
        reporter_id: int,
        target_type: str,
        target_id: int,
        reason: str,
    ) -> Report:
        """Создать жалобу.
        
        Args:
            reporter_id: ID пользователя.
            target_type: 'video' или 'comment'.
            target_id: ID объекта.
            reason: Причина жалобы.
            
        Returns:
            Созданная жалоба.
        """
        report = Report(
            reporter_id=reporter_id,
            target_type=target_type,
            target_id=target_id,
            reason=reason,
            status="pending",
        )
        
        self.db.add(report)
        await self.db.flush()
        await self.db.refresh(report)
        
        return report
    
    async def get_pending_reports(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Report]:
        """Получить жалобы на модерацию.
        
        Args:
            skip: Сколько пропустить.
            limit: Максимум записей.
            
        Returns:
            Список жалоб.
        """
        query = (
            select(Report)
            .where(Report.status == "pending")
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def resolve_report(
        self,
        report_id: int,
        moderator_id: int,
        action: str = "resolved",
        notes: str = "",
    ) -> Report:
        """Обработать жалобу.
        
        Args:
            report_id: ID жалобы.
            moderator_id: ID модератора.
            action: Действие ('resolved', 'rejected').
            notes: Заметки модератора.
            
        Returns:
            Обновлённая жалоба.
        """
        query = select(Report).where(Report.id == report_id)
        result = await self.db.execute(query)
        report = result.scalar_one_or_none()
        
        if not report:
            raise ValueError("Report not found")
        
        report.status = action
        report.moderator_id = moderator_id
        report.moderator_notes = notes
        
        if action == "resolved":
            from datetime import datetime, timezone
            report.resolved_at = datetime.now(timezone.utc)
            
            # Скрываем контент если жалоба подтверждена
            if report.target_type == "video":
                await self._hide_content(
                    "video",
                    report.target_id,
                    moderator_id,
                    f"Жалоба #{report_id}: {report.reason}",
                )
            elif report.target_type == "comment":
                await self._hide_content(
                    "comment",
                    report.target_id,
                    moderator_id,
                    f"Жалоба #{report_id}: {report.reason}",
                )
        
        await self.db.flush()
        await self.db.refresh(report)
        
        return report
    
    async def _hide_content(
        self,
        content_type: str,
        content_id: int,
        moderator_id: int,
        reason: str,
    ) -> None:
        """Скрыть контент.
        
        Args:
            content_type: 'video' или 'comment'.
            content_id: ID контента.
            moderator_id: ID модератора.
            reason: Причина.
        """
        hidden = HiddenContent(
            content_type=content_type,
            content_id=content_id,
            moderator_id=moderator_id,
            reason=reason,
        )
        
        self.db.add(hidden)
        
        # Логически скрываем контент
        if content_type == "video":
            query = select(Video).where(Video.id == content_id)
            result = await self.db.execute(query)
            video = result.scalar_one_or_none()
            if video:
                video.is_published = False
        elif content_type == "comment":
            query = select(Comment).where(Comment.id == content_id)
            result = await self.db.execute(query)
            comment = result.scalar_one_or_none()
            if comment:
                comment.content = "[Удалён модератором]"
        
        await self.db.flush()
    
    async def get_hidden_content(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[HiddenContent]:
        """Получить список скрытого контента.
        
        Args:
            skip: Сколько пропустить.
            limit: Максимум записей.
            
        Returns:
            Список скрытого контента.
        """
        query = (
            select(HiddenContent)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def unhide_content(
        self,
        content_id: int,
        moderator_id: int,
    ) -> None:
        """Восстановить скрытый контент.
        
        Args:
            content_id: ID контента.
            moderator_id: ID модератора.
        """
        query = select(HiddenContent).where(
            HiddenContent.content_id == content_id,
        )
        result = await self.db.execute(query)
        hidden = result.scalar_one_or_none()
        
        if not hidden:
            raise ValueError("Hidden content not found")
        
        # Восстанавливаем контент
        if hidden.content_type == "video":
            query = select(Video).where(Video.id == content_id)
            result = await self.db.execute(query)
            video = result.scalar_one_or_none()
            if video:
                video.is_published = True
        
        await self.db.delete(hidden)
        await self.db.flush()


moderation_service = ModerationService(None)  # type: ignore[arg-type]
