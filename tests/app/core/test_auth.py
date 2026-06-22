from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from tests.app.factories.user_factory import create_user

from app.core.auth import (
    create_access_token,
    decode_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.schemas.user import TokenData


def test_hash_password_returns_hashed_value():
    password = "secret123"

    hashed = hash_password(password)

    assert hashed != password
    assert isinstance(hashed, str)


def test_verify_password_success():
    password = "secret123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    hashed = hash_password("secret123")

    assert verify_password("wrong-password", hashed) is False


def test_create_and_decode_access_token():
    user_id = uuid4()

    token = create_access_token(
        {
            "sub": str(user_id),
            "email": "test@example.com",
        }
    )
    token_data = decode_access_token(token)

    assert token_data.user_id == user_id
    assert token_data.email == "test@example.com"


def test_create_access_token_with_custom_expiration():
    token = create_access_token(
        {"sub": str(uuid4())},
        expires_delta=timedelta(minutes=1),
    )

    assert isinstance(token, str)


@patch("app.core.auth.SECRET_KEY", None)
def test_create_access_token_without_secret_key():
    with pytest.raises(
        RuntimeError,
        match="SECRET_KEY is not set in environment",
    ):
        create_access_token({"sub": str(uuid4())})


@patch("app.core.auth.SECRET_KEY", None)
def test_decode_access_token_without_secret_key():
    with pytest.raises(
        RuntimeError,
        match="SECRET_KEY is not set in environment",
    ):
        decode_access_token("some-token")


def test_decode_with_invalid_token():
    with pytest.raises(HTTPException) as exc:
        decode_access_token("Invalid-token")

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid or expired token"


def test_decode_token_missing_subject():
    token = create_access_token({"email": "test@example.com"})

    with pytest.raises(HTTPException) as exc:
        decode_access_token(token)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token: missing subject"


def test_get_current_user_success(db_session):
    user = create_user(db_session)

    token = create_access_token({"sub": str(user.id), "email": user.email})

    current_user = get_current_user(token, db_session)

    assert current_user.id == user.id
    assert current_user.email == user.email
    assert current_user.username == user.username


def test_get_current_user_not_found(db_session):
    token = create_access_token(
        {
            "sub": str(uuid4()),
            "email": "missing@exmple.com",
        }
    )

    with pytest.raises(HTTPException) as exc:
        get_current_user(
            token,
            db_session,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "User not found"


@patch("app.core.auth.decode_access_token")
def test_get_current_user_invalid_token_data(
    mock_decode,
    db_session,
):
    mock_decode.return_value = TokenData(user_id=None, email=None)

    with pytest.raises(HTTPException) as exc:
        get_current_user(
            "token",
            db_session,
        )

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid token data"
