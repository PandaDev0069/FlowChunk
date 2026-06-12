from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.core.database import get_db
from app.models.user import UserOrm
from app.schemas.user import (
    LoginRequest,
    PrivateUserResponse,
    PublicUserResponse,
    RestoreUserResponse,
    Token,
    UserCreate,
)

router = APIRouter(prefix="/users", tags=["users"])

DbSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[UserOrm, Depends(get_current_user)]


@router.post(
    "/register", response_model=PrivateUserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user_in: UserCreate, db: DbSessionDep) -> UserOrm:
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


@router.post("/login", response_model=Token)
def login(user_in: LoginRequest, db: DbSessionDep) -> Token:
    stmt = select(UserOrm).where(UserOrm.email == user_in.email)
    user = db.scalars(stmt).one_or_none()
    if (
        not user
        or not verify_password(user_in.password, user.hashed_password)
        or user.is_deleted
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "username": user.username}
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/", response_model=PrivateUserResponse)
def get_current_user_info(current_user: CurrentUserDep) -> UserOrm:
    return current_user


@router.get("/{user_id}", response_model=PublicUserResponse)
def get_user_by_id(user_id: UUID, db: DbSessionDep) -> UserOrm:
    stmt = select(UserOrm).where(UserOrm.id == user_id, UserOrm.is_deleted == False)  # noqa: E712
    result = db.scalars(stmt).one_or_none()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result


@router.patch("/{user_id}", response_model=RestoreUserResponse)
def restore_user(user_id: UUID, db: DbSessionDep) -> UserOrm:
    stmt = select(UserOrm).where(UserOrm.id == user_id)
    user = db.scalars(stmt).one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.is_deleted = False
    user.deleted_at = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: DbSessionDep) -> None:
    stmt = select(UserOrm).where(UserOrm.id == user_id, UserOrm.is_superuser == False)  # noqa: E712 # Prevent deleting superusers
    user = db.scalars(stmt).one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.is_deleted = True
    user.deleted_at = datetime.now(tz=UTC)
    db.add(user)
    db.commit()
