"""Subscription model."""
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, ForeignKey, UniqueConstraint


class Subscription(Base):
    """Subscription model for channel subscriptions (follow/subscribe)."""

    __tablename__ = "subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"),
        nullable=False,
        index=True
    )

    # UNIQUE constraint: один пользователь подписан на один канал
    __table_args__ = (
        UniqueConstraint("user_id", "channel_id", name="uq_subscriptions_user_channel"),
    )

    # Relationships - use relationship objects with full path
    user = relationship(
        "User",
        foreign_keys="Subscription.user_id",
        back_populates="subscriptions"
    )
    channel = relationship(
        "Channel",
        back_populates="subscribers",
        lazy="selectin"
    )