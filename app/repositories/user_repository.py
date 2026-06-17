from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID

from sqlalchemy import CursorResult, delete
from sqlalchemy.orm import Session

from app.models.user import UserOrm


class UserRepository:
    @staticmethod
    def permanently_delete_soft_deleted_users(db: Session) -> int:
        cutoff_date = datetime.now(UTC) - timedelta(days=30)

        stmt = delete(UserOrm).where(
            UserOrm.is_deleted.is_(True),
            UserOrm.deleted_at <= cutoff_date,
        )

        result = cast(CursorResult, db.execute(stmt))
        db.commit()

        return result.rowcount or 0

    @staticmethod
    def hard_delete_user(db: Session, user_id: UUID) -> bool:
        stmt = delete(UserOrm).where(UserOrm.id == user_id)
        result = cast(CursorResult, db.execute(stmt))
        db.commit()
        return result.rowcount > 0
