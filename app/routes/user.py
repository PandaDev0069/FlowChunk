from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.core.deps import get_db
from app.models.user import UserOrm
from app.schemas.user import LoginRequest, Token, UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])

DbSessionDep = Annotated[Session, Depends(get_db)]
CurrentUserDep = Annotated[UserOrm, Depends(get_current_user)]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: DbSessionDep) -> UserOrm:
    # Check if username or email already exists
    exitsting_user = (
        db.query(UserOrm)
        .where(
            or_(
                UserOrm.username == user_in.username,
                UserOrm.email == user_in.email,
            )
        )
        .first()
    )

    if exitsting_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or User already Registered",
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
    user = db.query(UserOrm).filter(UserOrm.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "username": user.username}
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: CurrentUserDep) -> UserOrm:
    return current_user
