from app.core.auth import hash_password
from app.models.user import UserOrm


def create_user(
    db,
    username: str = "testuser",
    email: str = "test@test.com",
    password: str = "password123",
    is_deleted: bool = False,
) -> UserOrm:
    user = UserOrm(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        is_deleted=is_deleted,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user
