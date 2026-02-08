from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from tripy.api.deps import require_permissions
from tripy.db.session import get_db
from tripy.repositories.user_repository import UserRepository
from tripy.schemas.auth import UserResponse

router = APIRouter(prefix="/admin", tags=["admin"])
user_repository = UserRepository()


@router.get(
    "/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_permissions("users:read"))],
)
def list_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
) -> list[UserResponse]:
    users = user_repository.list_users(db, skip=skip, limit=limit)
    return [UserResponse.from_user(user) for user in users]
