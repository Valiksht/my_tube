"""Channel model."""
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
import datetime


class Channel(Base):
    """Channel model representing user's content channel."""

    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    avatar_url: Mapped[str] = mapped_column(String(500), nullable=False)
    banner_url: Mapped[str] = mapped_column(String(500), nullable=True)
    subscriber_count: Mapped[int] = mapped_column(Integer, default=0)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True  # Уникально — один канал у одного пользователя
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc)
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        uselist=False,
        back_populates="channel"
    )
    subscribers: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="channel",
        lazy="selectin"
    )
    videos: Mapped[list["Video"]] = relationship(
        "Video",
        foreign_keys="Video.channel_id",
        back_populates="channel",
        lazy="selectin"
    )