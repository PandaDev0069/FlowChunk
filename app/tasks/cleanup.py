# file: app/tasks/cleanup.py
from sqlalchemy.orm import Session

from app.repositories.user_repository import UserRepository


def run_user_cleanup(db: Session):
    deleted_count = UserRepository.permanently_delete_soft_deleted_users(db)
    print(f"Successfully cleaned up {deleted_count} soft-deleted users.")
