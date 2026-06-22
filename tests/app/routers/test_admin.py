from unittest.mock import patch


@patch("app.routers.admin.AdminService.permanently_delete_soft_deleted_users")
def test_cleanup_soft_deleted_users(
    mock_cleanup,
    admin_client,
):
    response = admin_client.delete("/admin/users/cleanup")

    assert response.status_code == 204
    mock_cleanup.assert_called_once()


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
