"""Like model."""
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, UniqueConstraint


class Like(Base):
    """Like model for video likes (one user can like one video at a time)."""

    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    video_id: Mapped[int] = mapped_column(
        ForeignKey("videos.id"),
        nullable=False,
        index=True
    )

    # UNIQUE constraint: один лайк от пользователя к одному видео
    __table_args__ = (
        UniqueConstraint("user_id", "video_id", name="uq_likes_user_video"),
    )

    # Relationships - use relationship objects, not column names
    user = relationship(
        "User",
        foreign_keys="Like.user_id"
    )
    video = relationship(
        "Video",
        foreign_keys="Like.video_id"
    )