from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from tripy.db.models import Permission, Role


class RbacRepository:
    def get_role_by_name(self, db: Session, name: str) -> Role | None:
        stmt = select(Role).where(Role.name == name).options(selectinload(Role.permissions))
        return db.execute(stmt).scalar_one_or_none()

    def get_permission_by_code(self, db: Session, code: str) -> Permission | None:
        stmt = select(Permission).where(Permission.code == code)
        return db.execute(stmt).scalar_one_or_none()

    def list_roles(self, db: Session) -> list[Role]:
        stmt = select(Role).options(selectinload(Role.permissions)).order_by(Role.id.asc())
        return list(db.execute(stmt).scalars().all())
