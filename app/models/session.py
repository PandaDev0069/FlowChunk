from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import DateTime, ForeignKey, Index, text
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SessionType(str, Enum):
    FOCUS = "focus"
    BREAK = "break"
    LONG_BREAK = "long_break"


class SessionOrm(Base):
    __tablename__ = "focus_sessions"

    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    session_type: Mapped[SessionType] = mapped_column(
        SQLAlchemyEnum(SessionType, native_enum=False, length=20),
        default=SessionType.FOCUS,
        server_default=text("'focus'"),
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    planned_duration: Mapped[int] = mapped_column(nullable=False)
    actual_duration: Mapped[int | None] = mapped_column(nullable=True)
    completed: Mapped[bool] = mapped_column(default=False, server_default=text("false"))

    __table_args__ = (
        Index("ix_focus_sessions_user_id_started_at", "user_id", "started_at"),
    )
