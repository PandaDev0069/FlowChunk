from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.pomodoro import PomodoroSettingsOrm
from app.models.user import UserOrm
from app.schemas.pomodoro import (
    PomodoroSettingsResponse,
    PomodoroSettingsUpdate,
)
from app.services.pomodoro_service import (
    get_settings,
    update_settings,
)

router = APIRouter(prefix="/pomodoro", tags=["Pomodoro_settings"])

DbSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[UserOrm, Depends(get_current_user)]


@router.get("/settings", response_model=PomodoroSettingsResponse)
def read_pomodoro_settings(
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> PomodoroSettingsOrm:
    settings = get_settings(db, current_user.id)
    return settings


@router.patch("/settings", response_model=PomodoroSettingsResponse)
def update_pomodoro_settings(
    updated_settings: PomodoroSettingsUpdate,
    db: DbSessionDep,
    current_user: CurrentUserDep,
) -> PomodoroSettingsOrm:
    settings = get_settings(db, current_user.id)

    return update_settings(db, settings, updated_settings)
