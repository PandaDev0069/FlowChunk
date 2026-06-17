import pytest
from fastapi import HTTPException, status

from app.models.user import UserOrm
from app.schemas.user import UserCreate
from app.services import user_service


def test_register_user_success(db_session):
    user_in = UserCreate(
        username="testuser", email="test@example.com", password="securepassword"
    )
    user = user_service.register_user(user_in, db_session)
    assert isinstance(user, UserOrm)
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_register_user_duplicate_username(db_session):
    user_in1 = UserCreate(
        username="testuser",
        email="test1@example.com",
        password="securepassword",
    )
    user_in2 = UserCreate(
        username="testuser",
        email="test2@example.com",
        password="securepassword",
    )
    user_service.register_user(user_in1, db_session)
    with pytest.raises(HTTPException) as exc_info:
        user_service.register_user(user_in2, db_session)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Username already taken"


def test_register_user_duplicate_email(db_session):
    user_in1 = UserCreate(
        username="testuser1",
        email="test@example.com",
        password="securepassword",
    )
    user_in2 = UserCreate(
        username="testuser2",
        email="test@example.com",
        password="securepassword",
    )
    user_service.register_user(user_in1, db_session)
    with pytest.raises(HTTPException) as exc_info:
        user_service.register_user(user_in2, db_session)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Email already taken"
