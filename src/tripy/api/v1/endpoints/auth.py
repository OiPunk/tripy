from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from tripy.api.deps import get_current_user, get_locale
from tripy.core.i18n import t
from tripy.db.models import User
from tripy.db.session import get_db
from tripy.schemas.auth import TokenResponse, UserCreate, UserLogin, UserResponse
from tripy.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale),
) -> UserResponse:
    try:
        user = service.register(db, payload)
    except ValueError as exc:
        if str(exc) == "user_exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=t("auth.user_exists", locale),
            ) from exc
        if str(exc) == "default_role_missing":
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=t("auth.user_not_ready", locale),
            ) from exc
        raise
    return UserResponse.from_user(user)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
    locale: str = Depends(get_locale),
) -> TokenResponse:
    user = service.authenticate(db, payload.username, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=t("auth.invalid_credentials", locale),
        )

    token, expires_in = service.issue_access_token(user)
    roles = sorted({role.name for role in user.roles})
    permissions = sorted(
        {permission.code for role in user.roles for permission in role.permissions}
    )
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        roles=roles,
        permissions=permissions,
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return UserResponse.from_user(current_user)
