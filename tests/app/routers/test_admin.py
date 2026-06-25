from datetime import UTC, datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

from tests.app.factories.user_factory import create_user

from app.models.user import UserOrm


@patch("app.routers.admin.AdminService.permanently_delete_soft_deleted_users")
def test_cleanup_soft_deleted_users(
    mock_cleanup,
    admin_client,
):
    response = admin_client.delete("/admin/users/cleanup")

    assert response.status_code == 204
    mock_cleanup.assert_called_once()


def test_cleanup_forbidden_for_regular_user(authorized_client):
    response = authorized_client.delete("/admin/users/cleanup")

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_cleanup_removes_old_soft_deleted_users(admin_client, db_session):
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

    response = admin_client.delete("/admin/users/cleanup")

    assert response.status_code == 204
    assert db_session.get(UserOrm, old_user.id) is None


@patch("app.routers.admin.AdminService.hard_delete_user")
def test_hard_delete_user_success(
    mock_hard_delete,
    admin_client,
):
    mock_hard_delete.return_value = True

    user_id = "00000000-0000-0000-0000-000000000001"

    response = admin_client.delete(f"/admin/users/{user_id}")

    assert response.status_code == 204

    mock_hard_delete.assert_called_once()


@patch("app.routers.admin.AdminService.hard_delete_user")
def test_hard_delete_user_not_found(
    mock_hard_delete,
    admin_client,
):
    mock_hard_delete.return_value = False

    user_id = "00000000-0000-0000-0000-000000000001"

    response = admin_client.delete(f"/admin/users/{user_id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "User not found"}


def test_cleanup_requires_superuser(
    client,
):
    response = client.delete("/admin/users/cleanup")

    assert response.status_code == 401


def test_hard_delete_forbidden_for_regular_user(authorized_client):
    user_id = "00000000-0000-0000-0000-000000000001"

    response = authorized_client.delete(f"/admin/users/{user_id}")

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


def test_hard_delete_requires_auth(client):
    user_id = "00000000-0000-0000-0000-000000000001"

    response = client.delete(f"/admin/users/{user_id}")

    assert response.status_code == 401


def test_hard_delete_user_integration(admin_client, db_session):
    user = create_user(db_session, username="todelete", email="delete@example.com")

    response = admin_client.delete(f"/admin/users/{user.id}")

    assert response.status_code == 204
    assert db_session.get(UserOrm, user.id) is None
