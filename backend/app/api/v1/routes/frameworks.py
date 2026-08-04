from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.framework import (
    FrameworkCreate,
    FrameworkUpdate,
    FrameworkResponse,
)

from app.services.framework_service import (
    create_framework,
    get_all_frameworks,
    get_framework_by_id,
    update_framework,
    delete_framework,
)

router = APIRouter(
    prefix="/frameworks",
    tags=["Compliance Frameworks"]
)


@router.post(
    "/",
    response_model=FrameworkResponse
)
def create_new_framework(
    framework_data: FrameworkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Create a new compliance framework.
    """

    framework = create_framework(
        db,
        framework_data
    )

    if framework == "FRAMEWORK_EXISTS":
        raise HTTPException(
            status_code=400,
            detail="Framework already exists."
        )

    return framework


@router.get(
    "/",
    response_model=list[FrameworkResponse]
)
def list_all_frameworks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    """
    Get all compliance frameworks.
    """

    return get_all_frameworks(db)


@router.get(
    "/{framework_id}",
    response_model=FrameworkResponse
)
def get_framework(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    )
):
    """
    Get a framework by ID.
    """

    framework = get_framework_by_id(
        db,
        framework_id
    )

    if framework is None:
        raise HTTPException(
            status_code=404,
            detail="Framework not found."
        )

    return framework


@router.patch(
    "/{framework_id}",
    response_model=FrameworkResponse
)
def update_existing_framework(
    framework_id: int,
    framework_data: FrameworkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Update a compliance framework.
    """

    framework = update_framework(
        db,
        framework_id,
        framework_data
    )

    if framework is None:
        raise HTTPException(
            status_code=404,
            detail="Framework not found."
        )

    if framework == "FRAMEWORK_EXISTS":
        raise HTTPException(
            status_code=400,
            detail="Framework already exists."
        )

    return framework


@router.delete(
    "/{framework_id}"
)
def delete_existing_framework(
    framework_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Delete a compliance framework.
    """

    deleted = delete_framework(
        db,
        framework_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Framework not found."
        )

    return {
        "message": "Framework deleted successfully."
    }