from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from tripy.db.models import Role, User


class UserRepository:
    def get_by_username(self, db: Session, username: str) -> User | None:
        stmt = (
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, db: Session, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        return db.execute(stmt).scalar_one_or_none()

    def list_users(self, db: Session, *, skip: int = 0, limit: int = 50) -> list[User]:
        stmt = (
            select(User)
            .offset(skip)
            .limit(limit)
            .options(selectinload(User.roles).selectinload(Role.permissions))
            .order_by(User.id.asc())
        )
        return list(db.execute(stmt).scalars().all())

    def create(
        self,
        db: Session,
        *,
        username: str,
        hashed_password: str,
        real_name: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        passenger_id: str | None = None,
        roles: list[Role] | None = None,
    ) -> User:
        user = User(
            username=username,
            hashed_password=hashed_password,
            real_name=real_name,
            email=email,
            phone=phone,
            passenger_id=passenger_id,
            is_active=True,
        )
        if roles:
            user.roles = roles
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
