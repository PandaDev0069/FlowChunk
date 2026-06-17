from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_superuser
from app.core.database import get_db
from app.models.user import UserOrm
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])

DbSessionDep = Annotated[Session, Depends(get_db)]
SuperuserDep = Annotated[UserOrm, Depends(get_superuser)]


@router.delete("/users/cleanup", status_code=204)
def cleanup_soft_deleted_users(
    db: DbSessionDep,
    current_user: SuperuserDep,
) -> None:
    AdminService.permanently_delete_soft_deleted_users(db)


@router.delete("/users/{user_id}", status_code=204)
def hard_delete_user(
    user_id: UUID,
    db: DbSessionDep,
    current_user: SuperuserDep,
) -> None:
    success = AdminService.hard_delete_user(user_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
