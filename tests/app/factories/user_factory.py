from app.core.auth import hash_password
from app.models.user import UserOrm


def create_user(
    db,
    username="testuser",
    email="test@test.com",
    password="password123",
    is_deleted=False,
    is_superuser=False,
):
    user = UserOrm(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        is_deleted=is_deleted,
        is_superuser=is_superuser,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
