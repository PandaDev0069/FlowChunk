from datetime import UTC, datetime
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import (
    hash_password,
)
from app.models.user import UserOrm
from app.schemas.user import (
    UpdateUserRequest,
    UserCreate,
)


def register_user(user_in: UserCreate, db: Session) -> UserOrm:
    # Check if username or email already exists
    stmt = select(UserOrm).where(
        UserOrm.username == user_in.username,
    )
    existing_username = db.scalars(stmt).one_or_none()

    if existing_username is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    stmt = select(UserOrm).where(
        UserOrm.email == user_in.email,
    )
    existing_email = db.scalars(stmt).one_or_none()

    if existing_email is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Create new user
    new_user = UserOrm(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_or_404(
    user_id: UUID,
    db: Session,
) -> UserOrm:
    stmt = select(UserOrm).where(
        UserOrm.id == user_id,
        UserOrm.is_deleted.is_(False),
    )
    user = db.scalars(stmt).one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


def update_user_by_id(
    user_id: UUID, db: Session, user_update: UpdateUserRequest
) -> UserOrm:
    user = get_user_or_404(user_id, db)
    if user_update.username and user_update.username != user.username:
        stmt = select(UserOrm).where(
            UserOrm.username == user_update.username,
            UserOrm.id != user.id,
        )
        existing_username = db.scalars(stmt).one_or_none()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )
        user.username = user_update.username
    if user_update.email and user_update.email != user.email:
        stmt = select(UserOrm).where(
            UserOrm.email == user_update.email,
            UserOrm.id != user.id,
        )
        existing_email = db.scalars(stmt).one_or_none()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user.email = user_update.email

    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(user_id: UUID, db: Session) -> None:
    user = get_user_or_404(user_id, db)
    user.is_deleted = True
    user.deleted_at = datetime.now(UTC)
    db.commit()
    db.refresh(user)


def restore_user_by_id(user_id: UUID, db: Session) -> UserOrm:
    user = get_user_or_404(user_id, db)
    user.is_deleted = False
    user.deleted_at = None
    db.commit()
    db.refresh(user)
    return user
