"""Comment model."""
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Text, DateTime, ForeignKey
import datetime


class Comment(Base):
    """Comment model for video comments."""

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("comments.id"), nullable=True)
    video_id: Mapped[int] = mapped_column(Integer, ForeignKey("videos.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc)
    )

    # Relationships to Video and User (back_populates не нужен, так как задано в родительских классах)
    video: Mapped["Video"] = relationship(
        "Video"  # FK автоматически определяется через column(video_id)
    )
    author: Mapped["User"] = relationship(
        "User"  # FK автоматически определяется через column(user_id)
    )

    # Self-referencing relationship for comment replies (SQLAlchemy 2.0 style)
    # Простая реализация для самореференции без back_populates
    parent = relationship(
        "Comment",
        viewonly=True,  # Только чтение через parent_id FK
        uselist=False,  # ONE side — каждый комментарий имеет максимум одного родителя
        lazy="joined"
    )

    replies = relationship(
        "Comment",
        lazy="selectin",  # Ленивая загрузка детей комментария
        overlaps="parent",  # Указываем что этот relationship пересекается с parent
        uselist=True,  # MANY side — parent может иметь множество детей
    )