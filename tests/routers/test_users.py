from unittest.mock import patch

from tests.factories.user_factory import create_user


def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "newuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    data = response.json()

    assert data["username"] == "newuser"
    assert data["email"] == "test@example.com"
    assert "id" in data


@patch("app.routes.user.create_access_token")
def test_login_success(
    mock_create_token,
    client,
    db_session,
):
    mock_create_token.return_value = "fake-token"

    create_user(db_session)

    response = client.post(
        "/users/login",
        json={
            "email": "test@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"] == "fake-token"
    assert data["token_type"] == "bearer"

    mock_create_token.assert_called_once()


def test_login_invalid_credentials(
    client,
    db_session,
):
    create_user(db_session)

    response = client.post(
        "/users/login",
        json={
            "email": "test@test.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password"


def test_login_deleted_user(
    client,
    db_session,
):
    user = create_user(db_session)
    user.is_deleted = True
    db_session.commit()

    response = client.post(
        "/users/login",
        json={
            "email": user.email,
            "password": "password123",
        },
    )
    assert response.status_code == 401


def test_get_current_user_success(
    authorized_client,
    authenticated_user,
):
    response = authorized_client.get("/users")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(authenticated_user.id)
    assert data["username"] == authenticated_user.username
    assert data["email"] == authenticated_user.email


def test_get_current_user_deleted_user(
    authorized_client,
    authenticated_user,
    db_session,
):
    authenticated_user.is_deleted = True
    db_session.commit()

    response = authorized_client.get("/users")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_get_user_by_id_success(
    client,
    db_session,
):
    user = create_user(db_session)

    response = client.get(f"/users/{user.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(user.id)
    assert data["username"] == user.username


def test_get_user_by_id_not_found(client):
    response = client.get("/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_get_user_by_id_deleted_user(client, db_session):
    user = create_user(db_session)
    user.is_deleted = True
    db_session.commit()

    response = client.get(f"/users/{user.id}")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"


def test_update_user_success(
    authorized_client,
    authenticated_user,
):
    response = authorized_client.patch(
        f"/users/{authenticated_user.id}",
        json={
            "username": "updateduser",
            "email": "updateduser@example.com",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(authenticated_user.id)
    assert data["username"] == "updateduser"
    assert data["email"] == "updateduser@example.com"


def test_update_user_forbidden(
    authorized_client,
):
    response = authorized_client.patch(
        "/users/00000000-0000-0000-0000-000000000000",
        json={
            "username": "hacker",
            "email": "hacker@example.com",
        },
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Users can only update their own account"


def test_delete_user_success(
    authorized_client,
    authenticated_user,
):
    response = authorized_client.delete(f"/users/{authenticated_user.id}")

    assert response.status_code == 204


def test_delete_user_forbidden(
    authorized_client,
):
    response = authorized_client.delete("/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Users can only delete their own account"


def test_restore_user_success(
    authorized_client,
    authenticated_user,
    db_session,
):
    authenticated_user.is_deleted = True
    db_session.commit()

    response = authorized_client.patch(f"/users/{authenticated_user.id}/restore")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(authenticated_user.id)
    assert data["username"] == authenticated_user.username
    assert data["email"] == authenticated_user.email


def test_restore_user_forbidden(
    authorized_client,
):
    response = authorized_client.patch(
        "/users/00000000-0000-0000-0000-000000000000/restore"
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Users can only restore their own account"
