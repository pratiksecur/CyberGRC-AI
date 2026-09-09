from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.core.roles import UserRole


class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserListResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: UserRole

class UserOrganizationUpdate(BaseModel):
    manager_id: int | None = None
    department: str | None = Field(
        default=None,
        max_length=100
    )

class Token(BaseModel):
    access_token: str
    token_type: str