from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=128)
    real_name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    phone: str | None = Field(default=None, max_length=30)
    passenger_id: str | None = Field(default=None, max_length=64)


class UserLogin(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)


class UserResponse(BaseModel):
    id: int
    username: str
    real_name: str | None
    email: str | None
    phone: str | None
    passenger_id: str | None
    is_active: bool
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)

    @classmethod
    def from_user(cls, user: Any) -> UserResponse:
        roles = sorted({role.name for role in getattr(user, "roles", [])})
        permissions = sorted(
            {
                permission.code
                for role in getattr(user, "roles", [])
                for permission in getattr(role, "permissions", [])
            }
        )
        return cls(
            id=user.id,
            username=user.username,
            real_name=user.real_name,
            email=user.email,
            phone=user.phone,
            passenger_id=user.passenger_id,
            is_active=user.is_active,
            roles=roles,
            permissions=permissions,
        )
