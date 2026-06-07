from fastapi import APIRouter, Depends, HTTPException, status
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

# module-level dependency singletons to avoid calling Depends() in defaults
get_db_dep = Depends(get_db)
current_user_dep = Depends(get_current_user)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = get_db_dep) -> UserOrm:
    # Check if username or email already exists
    if db.query(UserOrm).filter(UserOrm.username == user_in.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    if db.query(UserOrm).filter(UserOrm.email == user_in.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
def login(user_in: LoginRequest, db: Session = get_db_dep):
    user = db.query(UserOrm).filter(UserOrm.email == user_in.username).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id), "email": user.email})
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: UserOrm = current_user_dep):
    return current_user
