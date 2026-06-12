from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.repositories.user_repository import UserRepository

db_deps = Depends(get_db)


class AdminService:
    @staticmethod
    def permanently_delete_soft_deleted_users(db: Session = db_deps) -> int:
        return UserRepository.permanently_delete_soft_deleted_users(db)

    @staticmethod
    def hard_delete_user(user_id: UUID, db: Session = db_deps) -> bool:
        return UserRepository.hard_delete_user(db, user_id)
