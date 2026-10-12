from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)

from app.auth.emails import normalize_email
from app.core.roles import UserRole


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.EMPLOYEE

    @field_validator("email", mode="after")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return normalize_email(value)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email", mode="after")
    @classmethod
    def lowercase_email(cls, value: str) -> str:
        return normalize_email(value)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserListResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class UserRoleUpdate(BaseModel):
    role: UserRole


class UserOrganizationUpdate(BaseModel):
    manager_id: int | None = None
    department: str | None = Field(
        default=None,
        max_length=100
    )


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1, max_length=256)
    new_password: str = Field(..., min_length=1, max_length=256)


class AdminPasswordReset(BaseModel):
    new_password: str = Field(..., min_length=1, max_length=256)


class Token(BaseModel):
    access_token: str
    token_type: str