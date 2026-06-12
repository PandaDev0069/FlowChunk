from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=255)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)


class PrivateUserResponse(UserBase):
    id: UUID

    model_config = {
        "from_attributes": True,
    }


class PublicUserResponse(BaseModel):
    id: UUID
    username: str

    model_config = {
        "from_attributes": True,
    }


class RestoreUserResponse(PrivateUserResponse):
    is_deleted: bool = False


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[UUID] = None  # noqa: UP007
    email: Optional[EmailStr] = None  # noqa: UP007
