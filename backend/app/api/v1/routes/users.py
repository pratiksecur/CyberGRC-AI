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
    AdminPasswordReset,
    UserListResponse,
    UserRoleUpdate,
    UserOrganizationUpdate,
)

from app.services.account_service import (
    admin_reset_password,
    set_user_active,
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
        visible_user_ids,
        current_user,
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

    return get_all_users(db, current_user)


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
        user_id,
        current_user,
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
        role_data.role.value,
        current_user,
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
            organization_data.department,
            current_user,
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


# ==========================================================
# ACCOUNT STATE AND PASSWORD RESET
# ==========================================================

def _target_user(
    db: Session,
    user_id: int,
    current_user: User,
) -> User:
    user = get_user_by_id(db, user_id, current_user)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )

    return user


@router.post(
    "/{user_id}/deactivate"
)
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    """
    Deactivate a user (offboarding).

    The user can no longer sign in and every existing session stops
    working. Records they own are kept. You cannot deactivate yourself or
    the last active administrator.
    """

    target = _target_user(db, user_id, current_user)

    try:
        user = set_user_active(db, current_user, target, False)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "message": "User deactivated.",
        "user": UserListResponse.model_validate(user),
    }


@router.post(
    "/{user_id}/activate"
)
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    """
    Reactivate a previously deactivated user.
    """

    target = _target_user(db, user_id, current_user)

    user = set_user_active(db, current_user, target, True)

    return {
        "message": "User activated.",
        "user": UserListResponse.model_validate(user),
    }


@router.post(
    "/{user_id}/reset-password"
)
def reset_user_password(
    user_id: int,
    data: AdminPasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN)
    )
):
    """
    Set a new password for another user.

    All of that user's sessions are signed out. Administrators change
    their own password with /auth/change-password instead.
    """

    target = _target_user(db, user_id, current_user)

    try:
        user = admin_reset_password(
            db,
            current_user,
            target,
            data.new_password,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return {
        "message": "Password reset. The user must sign in again.",
        "user": UserListResponse.model_validate(user),
    }