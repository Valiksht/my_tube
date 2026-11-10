"""Video model."""
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey
import datetime


class Video(Base):
    """Video model representing uploaded video content."""

    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    video_object_key: Mapped[str] = mapped_column(String(500), nullable=False)  # MinIO object key
    thumbnail_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)  # Nullable пока загрузка не завершена
    duration: Mapped[int] = mapped_column(Integer, default=0)  # in seconds
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc)
    )

    # Relationships
    channel_id: Mapped[int] = mapped_column(Integer, ForeignKey("channels.id"), nullable=False)
    channel: Mapped["Channel"] = relationship(
        "Channel",
        back_populates="videos"
    )
    likes: Mapped[list["Like"]] = relationship(
        "Like",
        foreign_keys="Like.video_id",
        back_populates="video",
        lazy="selectin"
    )
    comments: Mapped[list["Comment"]] = relationship(
        "Comment",
        foreign_keys="Comment.video_id",
        back_populates="video",
        lazy="selectin"
    )