from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from tripy.core.config import get_settings
from tripy.core.security import hash_password
from tripy.db.base import Base
from tripy.db.models import Permission, Role, User
from tripy.db.session import SessionLocal, engine

DEFAULT_PERMISSION_SET = {
    "graph:execute": "Execute graph workflow requests",
    "users:read": "Read user profiles",
    "users:write": "Create or update users",
    "roles:manage": "Manage RBAC roles and permissions",
}

DEFAULT_ROLE_MAP = {
    "admin": {
        "description": "System administrator",
        "permissions": list(DEFAULT_PERMISSION_SET.keys()),
    },
    "traveler": {
        "description": "Default traveler role",
        "permissions": ["graph:execute"],
    },
}


def _ensure_sqlite_path() -> None:
    settings = get_settings()
    if settings.database_url.startswith("sqlite:///"):
        file_path = settings.database_url.replace("sqlite:///", "", 1)
        db_path = Path(file_path)
        if db_path.parent and str(db_path.parent) != ".":
            db_path.parent.mkdir(parents=True, exist_ok=True)


def _upsert_permissions() -> None:
    with SessionLocal() as session:
        existing = {
            permission.code: permission
            for permission in session.execute(select(Permission)).scalars().all()
        }

        for code, description in DEFAULT_PERMISSION_SET.items():
            if code not in existing:
                session.add(Permission(code=code, description=description))
            elif existing[code].description != description:
                existing[code].description = description

        session.commit()


def _upsert_roles() -> None:
    with SessionLocal() as session:
        permissions = {
            permission.code: permission
            for permission in session.execute(select(Permission)).scalars().all()
        }
        existing_roles = {
            role.name: role
            for role in session.execute(select(Role)).scalars().all()
        }

        for role_name, role_data in DEFAULT_ROLE_MAP.items():
            if role_name in existing_roles:
                role = existing_roles[role_name]
                role.description = role_data["description"]
            else:
                role = Role(name=role_name, description=role_data["description"])
                session.add(role)

            role.permissions = [
                permissions[permission_code]
                for permission_code in role_data["permissions"]
                if permission_code in permissions
            ]

        session.commit()


def _bootstrap_admin_user() -> None:
    settings = get_settings()
    with SessionLocal() as session:
        admin_role = session.execute(
            select(Role).where(Role.name == "admin")
        ).scalar_one_or_none()
        if admin_role is None:
            return

        existing = session.execute(
            select(User).where(User.username == settings.bootstrap_admin_username)
        ).scalar_one_or_none()
        if existing is None:
            existing = User(
                username=settings.bootstrap_admin_username,
                hashed_password=hash_password(settings.bootstrap_admin_password),
                passenger_id=settings.bootstrap_admin_passenger_id,
                is_active=True,
            )
            session.add(existing)
            session.flush()
        else:
            existing.hashed_password = hash_password(settings.bootstrap_admin_password)
            existing.passenger_id = settings.bootstrap_admin_passenger_id

        if admin_role not in existing.roles:
            existing.roles.append(admin_role)

        existing.is_active = True
        session.commit()


def init_db() -> None:
    settings = get_settings()
    _ensure_sqlite_path()

    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)

    try:
        _upsert_permissions()
        _upsert_roles()
        _bootstrap_admin_user()
    except OperationalError as exc:
        raise RuntimeError(
            "Database schema is not initialized. Run `alembic upgrade head` first."
        ) from exc
