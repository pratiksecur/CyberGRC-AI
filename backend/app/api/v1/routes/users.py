from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db

from app.auth.dependencies import get_current_user
from app.auth.permissions import require_roles
from app.auth.visibility import get_visible_user_ids

from app.core.roles import UserRole
from app.models.user import User

from app.schemas.user import (
    UserListResponse,
    UserRoleUpdate,
    UserOrganizationUpdate,
)

from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user_role,
    update_user_organization,
    get_visible_users,
)


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ==========================================================
# VISIBLE USERS
# ==========================================================

@router.get(
    "/visible",
    response_model=List[UserListResponse]
)
def list_visible_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve users within the current user's
    organizational visibility scope.

    This endpoint is for organizational visibility
    and resource ownership/assignment.

    It does NOT provide user administration access.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "users",
    )

    return get_visible_users(
        db,
        visible_user_ids
    )


# ==========================================================
# ADMIN USER MANAGEMENT
# ==========================================================

@router.get(
    "/",
    response_model=List[UserListResponse]
)
def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    """
    Retrieve all users.

    Only Administrators can access this endpoint.
    """

    return get_all_users(db)


@router.get(
    "/{user_id}",
    response_model=UserListResponse
)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    """
    Retrieve a user by ID.

    Only Administrators can access this endpoint.
    """

    user = get_user_by_id(
        db,
        user_id
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return user


# ==========================================================
# UPDATE USER ROLE
# ==========================================================

@router.patch(
    "/{user_id}/role"
)
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    """
    Update a user's role.

    Only Administrators can change roles.
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


# ==========================================================
# UPDATE ORGANIZATIONAL INFORMATION
# ==========================================================

@router.patch(
    "/{user_id}/organization"
)
def change_user_organization(
    user_id: int,
    organization_data: UserOrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    """
    Update a user's organizational hierarchy.

    Administrators can assign:
    - Manager
    - Department
    """

    try:

        user = update_user_organization(
            db,
            user_id,
            organization_data.manager_id,
            organization_data.department
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return {
        "message": (
            "User organizational information "
            "updated successfully."
        ),
        "user": user
    }