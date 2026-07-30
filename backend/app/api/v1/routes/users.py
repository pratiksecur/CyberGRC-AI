from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User
from app.schemas.user import UserListResponse, UserRoleUpdate
from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user_role,
)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/",
    response_model=List[UserListResponse]
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    """
    Retrieve all users.
    Only Admins can access this endpoint.
    """
    return get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserListResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    """
    Retrieve a user by ID.
    """

    user = get_user_by_id(db, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return user

@router.patch("/{user_id}/role")
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN))
):
    """
    Update a user's role.
    """

    user = update_user_role(
        db,
        user_id,
        role_data.role.value
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return {
        "message": "User role updated successfully.",
        "user": user
    }