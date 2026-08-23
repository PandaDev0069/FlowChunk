from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.core.database import get_db
from app.models.pomodoro_session import SessionOrm
from app.models.user import UserOrm
from app.schemas.pomodoro_session import (
    SessionCreate,
    SessionResponse,
    SessionUpdate,
)
from app.services.pomodoro_session_service import (
    complete_session,
    create_session,
    get_active_session,
    get_session,
)

router = APIRouter(prefix="/pomodoro/sessions", tags=["Pomodoro_sessions"])

DbSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[UserOrm, Depends(get_current_user)]


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
)
def get_pomodoro_session(
    db: DbSessionDep,
    current_user: CurrentUserDep,
    session_id: UUID,
) -> SessionOrm:
    session = get_session(db, current_user.id, session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pomodoro session not found",
        )
    return session


@router.get(
    "/{session_id}/active",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
)
def get_active_pomodoro_session(
    db: DbSessionDep,
    current_user: CurrentUserDep,
    session_id: UUID,
) -> SessionOrm:
    session = get_active_session(db, current_user.id, session_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active Pomodoro session not found",
        )
    return session


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_pomodoro_session(
    db: DbSessionDep,
    current_user: CurrentUserDep,
    session_data: SessionCreate,
) -> SessionOrm:
    return create_session(db, current_user.id, session_data)


@router.patch(
    "/{session_id}",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
)
def complete_pomodoro_session(
    db: DbSessionDep,
    current_user: CurrentUserDep,
    session_id: UUID,
    session: SessionUpdate,
) -> SessionOrm:
    db_session = get_session(db, current_user.id, session_id)
    if db_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pomodoro session not found",
        )
    if db_session.ended_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pomodoro session has already ended",
        )

    return complete_session(
        db=db,
        db_session=db_session,
        completed=session.completed,
    )
