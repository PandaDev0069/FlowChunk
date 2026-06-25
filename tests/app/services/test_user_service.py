from uuid import UUID

import pytest
from fastapi import HTTPException, status

from app.models.user import UserOrm
from app.schemas.user import UpdateUserRequest, UserCreate
from app.services import user_service


@pytest.fixture
def test_user(db_session) -> UserOrm:
    test_user = UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword",
    )
    user = user_service.register_user(test_user, db_session)
    return user


def test_register_user_success(db_session):
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        password="securepassword",
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
    assert exc_info.value.detail == "Email already registered"


def test_get_user_or_404_returns_user(db_session, test_user):
    retrieved_user = user_service.get_user_or_404(user_id=test_user.id, db=db_session)
    assert retrieved_user == test_user


def test_get_user_or_404_not_found(db_session):
    nil_uuid = UUID("00000000-0000-0000-0000-000000000000")
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user_or_404(user_id=nil_uuid, db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found"


def test_get_user_or_404_deleted_user(db_session, test_user):
    test_user.is_deleted = True
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user_or_404(user_id=test_user.id, db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found"


def test_update_user_success(db_session, test_user):
    update_data = UpdateUserRequest(
        username="updateduser",
        email="update@example.com",
    )
    updated_user = user_service.update_user_by_id(
        user_id=test_user.id, db=db_session, user_update=update_data
    )
    assert updated_user.username == "updateduser"
    assert updated_user.email == "update@example.com"


def test_update_user_duplicate_username(db_session, test_user):
    existing_user = UserCreate(
        username="existinguser",
        email="existing@example.com",
        password="securepassword",
    )
    user_service.register_user(existing_user, db_session)
    update_data = UpdateUserRequest(
        username="existinguser",
        email="update@example.com",
    )
    with pytest.raises(HTTPException) as exc_info:
        user_service.update_user_by_id(
            user_id=test_user.id, db=db_session, user_update=update_data
        )
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Username already taken"


def test_update_user_username_only(db_session, test_user):
    update_data = UpdateUserRequest(username="newusername")
    updated_user = user_service.update_user_by_id(
        user_id=test_user.id, db=db_session, user_update=update_data
    )
    assert updated_user.username == "newusername"
    assert updated_user.email == test_user.email


def test_update_user_email_only(db_session, test_user):
    update_data = UpdateUserRequest(email="newemail@example.com")
    updated_user = user_service.update_user_by_id(
        user_id=test_user.id, db=db_session, user_update=update_data
    )
    assert updated_user.email == "newemail@example.com"
    assert updated_user.username == test_user.username


def test_update_user_no_changes(db_session, test_user):
    update_data = UpdateUserRequest()
    updated_user = user_service.update_user_by_id(
        user_id=test_user.id, db=db_session, user_update=update_data
    )
    assert updated_user.username == test_user.username
    assert updated_user.email == test_user.email


def test_update_user_same_values(db_session, test_user):
    update_data = UpdateUserRequest(
        username=test_user.username,
        email=test_user.email,
    )
    updated_user = user_service.update_user_by_id(
        user_id=test_user.id, db=db_session, user_update=update_data
    )
    assert updated_user.username == test_user.username
    assert updated_user.email == test_user.email


def test_update_user_duplicate_email(db_session, test_user):
    existing_user = UserCreate(
        username="existinguser",
        email="existing@example.com",
        password="securepassword",
    )
    user_service.register_user(existing_user, db_session)
    update_data = UpdateUserRequest(
        username="updateduser",
        email="existing@example.com",
    )
    with pytest.raises(HTTPException) as exc_info:
        user_service.update_user_by_id(
            user_id=test_user.id, db=db_session, user_update=update_data
        )
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Email already registered"


def test_delete_user_by_id_success(db_session, test_user):
    user_service.delete_user_by_id(user_id=test_user.id, db=db_session)
    deleted_user = db_session.get(UserOrm, test_user.id)
    assert deleted_user.is_deleted is True


def test_delete_user_by_id_not_found(db_session):
    nil_uuid = UUID("00000000-0000-0000-0000-000000000000")
    with pytest.raises(HTTPException) as exc_info:
        user_service.delete_user_by_id(user_id=nil_uuid, db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found"


def test_delete_user_by_id_already_deleted(db_session, test_user):
    test_user.is_deleted = True
    db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        user_service.delete_user_by_id(user_id=test_user.id, db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found"


def test_restore_user_by_id_success(db_session, test_user):
    test_user.is_deleted = True
    db_session.commit()

    user_service.restore_user_by_id(user_id=test_user.id, db=db_session)
    restored_user = db_session.get(UserOrm, test_user.id)
    assert restored_user.is_deleted is False


def test_restore_user_by_id_not_found(db_session):
    nil_uuid = UUID("00000000-0000-0000-0000-000000000000")
    with pytest.raises(HTTPException) as exc_info:
        user_service.restore_user_by_id(user_id=nil_uuid, db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found or already deleted"


def test_restore_user_by_id_not_deleted(db_session, test_user):
    with pytest.raises(HTTPException) as exc_info:
        user_service.restore_user_by_id(user_id=test_user.id, db=db_session)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "User not found or already deleted"
