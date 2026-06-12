import os
from datetime import UTC, datetime, timedelta
from typing import Optional
from uuid import UUID as UUIDClass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.user import UserOrm
from app.schemas.user import TokenData

dotenv_path = os.path.join(os.path.dirname(__file__), "../../.env")
if os.path.exists(dotenv_path):
    from dotenv import load_dotenv

    load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt"],
    deprecated="auto",
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
# use module-level dependency singletons to avoid calling `Depends()`
oauth2_scheme_dep = Depends(oauth2_scheme)
get_db_dep = Depends(get_db)

# --- Password hashing ---


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT token handling ---


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:  # noqa: UP007
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set in environment")

    to_encode = data.copy()
    expire = datetime.now(tz=UTC) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> TokenData:
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not set in environment")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return TokenData(user_id=UUIDClass(user_id), email=email)
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        ) from err


# --- Current user dependency ---


def get_current_user(
    token: str = oauth2_scheme_dep,
    db: Session = get_db_dep,
) -> UserOrm:
    token_data = decode_access_token(token)

    if token_data.user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token data"
        )

    try:
        user_uuid = UUIDClass(str(token_data.user_id))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user id in token"
        ) from err

    stmt = select(UserOrm).where(
        UserOrm.id == user_uuid,
    )
    user = db.scalars(stmt).one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


current_user_dep = Depends(get_current_user)


def get_superuser(current_user: UserOrm = current_user_dep) -> UserOrm:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
        )
    return current_user
