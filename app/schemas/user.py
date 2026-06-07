from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: UUID
    email: EmailStr
    username: str

    model_config = {
        "from_attributes": True,
    }


class LoginRequest(BaseModel):
    username: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[str] = None  # noqa: UP007
    email: Optional[EmailStr] = None  # noqa: UP007
