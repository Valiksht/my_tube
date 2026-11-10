"""User model."""
from app.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean, DateTime
import datetime


class User(Base):
    """User model representing account holder."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),
        index=True
    )

    # Relationships
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        foreign_keys="Subscription.user_id",
        back_populates="user",
        lazy="selectin"
    )
    channel: Mapped["Channel"] = relationship(
        "Channel",
        uselist=False,
        back_populates="owner",
        cascade="all, delete-orphan"
    )
