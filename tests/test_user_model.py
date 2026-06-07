from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.user import UserOrm
from app.schemas.user import UserResponse


def test_user_orm_generates_uuid_primary_key() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    user = UserOrm(
        username="string",
        email="user@example.com",
        hashed_password="hashed-password",
    )

    session.add(user)
    session.flush()

    assert user.id is not None
    assert str(user.id)


def test_user_response_serializes_uuid_id() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()

    user = UserOrm(
        username="string",
        email="user@example.com",
        hashed_password="hashed-password",
    )

    session.add(user)
    session.flush()

    payload = UserResponse.model_validate(user).model_dump(mode="json")

    assert payload["id"] == str(user.id)
