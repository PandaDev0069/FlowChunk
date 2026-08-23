from uuid import UUID, uuid4

from sqlalchemy import UUID as SQLAlchemyUUID
from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PomodoroSettingsOrm(Base):
    __tablename__ = "pomodoro_settings"

    id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        SQLAlchemyUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    focus_duration: Mapped[int] = mapped_column(
        default=1500, server_default=text("1500")
    )
    short_break_duration: Mapped[int] = mapped_column(
        default=300, server_default=text("300")
    )
    long_break_duration: Mapped[int] = mapped_column(
        default=900, server_default=text("900")
    )
    sessions_before_long_break: Mapped[int] = mapped_column(
        default=4, server_default=text("4")
    )
    auto_start_focus: Mapped[bool] = mapped_column(
        default=False, server_default=text("false")
    )
    auto_start_break: Mapped[bool] = mapped_column(
        default=False, server_default=text("false")
    )
