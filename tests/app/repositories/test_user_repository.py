from datetime import UTC, datetime, timedelta
from uuid import uuid4

from app.models.user import UserOrm
from app.repositories.user_repository import UserRepository


def test_permanently_delete_soft_deleted_users_deletes_old_soft_deleted_users(
    db_session,
):
    old_user = UserOrm(
        id=uuid4(),
        username="old_user",
        email="old@example.com",
        hashed_password="password",
        is_deleted=True,
        deleted_at=datetime.now(UTC) - timedelta(days=31),
    )

    db_session.add(old_user)
    db_session.commit()

    deleted_count = UserRepository.permanently_delete_soft_deleted_users(db_session)

    assert deleted_count == 1
    assert db_session.get(UserOrm, old_user.id) is None


def test_permanently_delete_soft_deleted_users_does_not_delete_recent_users(
    db_session,
):
    recent_user = UserOrm(
        id=uuid4(),
        username="recent_user",
        email="recent@example.com",
        hashed_password="password",
        is_deleted=True,
        deleted_at=datetime.now(UTC) - timedelta(days=10),
    )

    db_session.add(recent_user)
    db_session.commit()

    deleted_count = UserRepository.permanently_delete_soft_deleted_users(db_session)

    assert deleted_count == 0
    assert db_session.get(UserOrm, recent_user.id) is not None


def test_permanently_delete_soft_deleted_users_does_not_delete_active_users(
    db_session,
):
    active_user = UserOrm(
        id=uuid4(),
        username="active_user",
        email="active@example.com",
        hashed_password="password",
        is_deleted=False,
    )

    db_session.add(active_user)
    db_session.commit()

    deleted_count = UserRepository.permanently_delete_soft_deleted_users(db_session)

    assert deleted_count == 0
    assert db_session.get(UserOrm, active_user.id) is not None


def test_permanently_delete_soft_deleted_users_at_30_day_boundary(
    db_session,
):
    boundary_user = UserOrm(
        id=uuid4(),
        username="boundary_user",
        email="boundary@example.com",
        hashed_password="password",
        is_deleted=True,
        deleted_at=datetime.now(UTC) - timedelta(days=30),
    )
    db_session.add(boundary_user)
    db_session.commit()

    deleted_count = UserRepository.permanently_delete_soft_deleted_users(db_session)

    assert deleted_count == 1
    assert db_session.get(UserOrm, boundary_user.id) is None


def test_permanently_delete_soft_deleted_users_removes_multiple(
    db_session,
):
    for i in range(2):
        user = UserOrm(
            id=uuid4(),
            username=f"old_user_{i}",
            email=f"old{i}@example.com",
            hashed_password="password",
            is_deleted=True,
            deleted_at=datetime.now(UTC) - timedelta(days=40),
        )
        db_session.add(user)
    db_session.commit()

    deleted_count = UserRepository.permanently_delete_soft_deleted_users(db_session)

    assert deleted_count == 2


def test_hard_delete_user_success(db_session):
    user = UserOrm(
        id=uuid4(),
        username="test_user",
        email="test@example.com",
        hashed_password="password",
    )

    db_session.add(user)
    db_session.commit()

    result = UserRepository.hard_delete_user(
        db_session,
        user.id,
    )

    assert result is True
    assert db_session.get(UserOrm, user.id) is None


def test_hard_delete_user_returns_false_for_missing_user(
    db_session,
):
    result = UserRepository.hard_delete_user(
        db_session,
        uuid4(),
    )

    assert result is False
