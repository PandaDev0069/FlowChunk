from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_superuser
from app.core.deps import get_db
from app.models.user import UserOrm
from app.services.admin import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])

db_deps = Depends(get_db)
superuser_deps = Depends(get_superuser)


@router.delete("/users/cleanup", status_code=204)
def cleanup_soft_deleted_users(
    db: Session = db_deps,
    current_user: UserOrm = superuser_deps,
) -> None:
    AdminService.permanently_delete_soft_deleted_users(db)


@router.delete("/users/{user_id}", status_code=204)
def hard_delete_user(
    user_id: UUID,
    db: Session = db_deps,
    current_user: UserOrm = superuser_deps,
) -> dict:
    success = AdminService.hard_delete_user(user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": f"User {user_id} has been permanently deleted."}
