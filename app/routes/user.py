from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import (
    create_access_token,
    get_current_user,
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
    UpdateUserRequest,
    UserCreate,
)
from app.services.user_service import (
    delete_user_by_id,
    register_user,
    restore_user_by_id,
    update_user_by_id,
)

router = APIRouter(prefix="/users", tags=["users"])

DbSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[UserOrm, Depends(get_current_user)]


@router.post(
    "/register", response_model=PrivateUserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user_in: UserCreate, db: DbSessionDep) -> UserOrm:
    new_user = register_user(user_in, db)
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


@router.get("", response_model=PrivateUserResponse)
def get_current_user_info(current_user: CurrentUserDep) -> UserOrm:
    if current_user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return current_user


@router.get("/{user_id}", response_model=PublicUserResponse)
def get_user_by_id(user_id: UUID, db: DbSessionDep) -> UserOrm:
    stmt = select(UserOrm).where(UserOrm.id == user_id, UserOrm.is_deleted.is_(False))
    result = db.scalars(stmt).one_or_none()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return result


@router.patch("/{user_id}", response_model=PrivateUserResponse)
def update_user(
    user_id: UUID,
    db: DbSessionDep,
    current_user: CurrentUserDep,
    user_update: UpdateUserRequest,
) -> UserOrm:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only update their own account",
        )

    user = update_user_by_id(user_id, db, user_update)
    return user


@router.patch("/{user_id}/restore", response_model=RestoreUserResponse)
def restore_user(
    user_id: UUID, db: DbSessionDep, current_user: CurrentUserDep
) -> UserOrm:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only restore their own account",
        )
    user = restore_user_by_id(user_id, db)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, db: DbSessionDep, current_user: CurrentUserDep) -> None:
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Users can only delete their own account",
        )

    delete_user_by_id(user_id, db)
