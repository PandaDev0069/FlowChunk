from app.models.user import UserOrm


def test_create_user_model():
    user = UserOrm(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123",
    )

    assert user.username == "testuser"
    assert user.email == "test@example.com"


def test_user_persisted(db_session):
    user = UserOrm(
        username="testuser",
        email="test@example.com",
        hashed_password="hashedpassword123",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
