from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pomodoro_session import SessionOrm
from app.schemas.pomodoro_session import SessionCreate, SessionUpdate


def get_session(
    db: Session,
    user_id: UUID,
    session_id: UUID,
) -> SessionOrm | None:
    stmt = select(SessionOrm).where(
        SessionOrm.id == session_id,
        SessionOrm.user_id == user_id,
    )
    return db.execute(stmt).scalars().first()

def get_active_session(
    db: Session,
    user_id: UUID,
    session_id: UUID,
) -> SessionOrm | None:
    stmt = select(SessionOrm).where(
        SessionOrm.id == session_id,
        SessionOrm.user_id == user_id,
        SessionOrm.ended_at.is_(None),
    )
    return db.execute(stmt).scalars().first()


def create_session(
    db: Session,
    user_id: UUID,
    session: SessionCreate,
) -> SessionOrm:
    db_session = SessionOrm(user_id=user_id, **session.model_dump())

    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_session(
    db: Session,
    db_session: SessionOrm,
    session: SessionUpdate,
) -> SessionOrm:
    update_data = session.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(db_session, field, value)

    db.commit()
    db.refresh(db_session)

    return db_session
