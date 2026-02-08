from __future__ import annotations

from sqlalchemy.orm import Session

from tripy.core.config import get_settings
from tripy.core.security import create_access_token, hash_password, verify_password
from tripy.db.models import User
from tripy.repositories.rbac_repository import RbacRepository
from tripy.repositories.user_repository import UserRepository
from tripy.schemas.auth import UserCreate


class AuthService:
    def __init__(
        self,
        repository: UserRepository | None = None,
        rbac_repository: RbacRepository | None = None,
    ):
        self.repository = repository or UserRepository()
        self.rbac_repository = rbac_repository or RbacRepository()

    def register(self, db: Session, payload: UserCreate) -> User:
        settings = get_settings()
        existing = self.repository.get_by_username(db, payload.username)
        if existing:
            raise ValueError("user_exists")

        default_role = self.rbac_repository.get_role_by_name(db, settings.default_user_role)
        if default_role is None:
            raise ValueError("default_role_missing")

        return self.repository.create(
            db,
            username=payload.username,
            hashed_password=hash_password(payload.password),
            real_name=payload.real_name,
            email=payload.email,
            phone=payload.phone,
            passenger_id=payload.passenger_id,
            roles=[default_role],
        )

    def authenticate(self, db: Session, username: str, password: str) -> User | None:
        user = self.repository.get_by_username(db, username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def issue_access_token(self, user: User) -> tuple[str, int]:
        settings = get_settings()
        roles = sorted({role.name for role in user.roles})
        permissions = sorted(
            {permission.code for role in user.roles for permission in role.permissions}
        )
        token = create_access_token(
            subject=str(user.id),
            extra_claims={
                "username": user.username,
                "roles": roles,
                "permissions": permissions,
            },
        )
        return token, settings.jwt_access_token_expire_minutes * 60
