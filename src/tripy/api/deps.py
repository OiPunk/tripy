from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from tripy.core.i18n import detect_locale, t
from tripy.core.security import oauth2_scheme, validate_token
from tripy.db.models import User
from tripy.db.session import get_db
from tripy.repositories.user_repository import UserRepository


user_repository = UserRepository()


def get_locale(accept_language: str | None = Header(default=None)) -> str:
    return detect_locale(accept_language)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale),
) -> User:
    try:
        payload = validate_token(token)
        user_id = int(payload.get("sub", "0"))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("auth.unauthorized", locale),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user = user_repository.get_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("auth.unauthorized", locale),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_roles(current_user: User = Depends(get_current_user)) -> set[str]:
    return {role.name for role in current_user.roles}


def get_current_permissions(current_user: User = Depends(get_current_user)) -> set[str]:
    return {
        permission.code
        for role in current_user.roles
        for permission in role.permissions
    }


def require_roles(*roles: str) -> Callable[[set[str], str], None]:
    required = set(roles)

    def _dependency(
        current_roles: set[str] = Depends(get_current_roles),
        locale: str = Depends(get_locale),
    ) -> None:
        if not required.issubset(current_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=t("auth.forbidden", locale),
            )

    return _dependency


def require_permissions(*permissions: str) -> Callable[[set[str], str], None]:
    required = set(permissions)

    def _dependency(
        current_permissions: set[str] = Depends(get_current_permissions),
        locale: str = Depends(get_locale),
    ) -> None:
        if not required.issubset(current_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=t("auth.forbidden", locale),
            )

    return _dependency
