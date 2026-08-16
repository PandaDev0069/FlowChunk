from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pomodoro import PomodoroSettingsOrm
from app.schemas.pomodoro import (
    PomodoroSettingsCreate,
    PomodoroSettingsUpdate,
)


def get_settings(db: Session, user_id: UUID) -> PomodoroSettingsOrm:
    stmt = select(PomodoroSettingsOrm).where(PomodoroSettingsOrm.user_id == user_id)
    settings = db.execute(stmt).scalars().first()
    if settings is not None:
        return settings

    return create_settings(
        db,
        user_id,
        settings=PomodoroSettingsCreate(),
    )


def create_settings(
    db: Session,
    user_id: UUID,
    settings: PomodoroSettingsCreate,
) -> PomodoroSettingsOrm:
    db_settings = PomodoroSettingsOrm(user_id=user_id, **settings.model_dump())

    db.add(db_settings)
    db.commit()
    db.refresh(db_settings)
    return db_settings


def update_settings(
    db: Session,
    db_settings: PomodoroSettingsOrm,
    settings: PomodoroSettingsUpdate,
) -> PomodoroSettingsOrm:
    update_data = settings.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_settings, field, value)

    db.commit()
    db.refresh(db_settings)

    return db_settings
