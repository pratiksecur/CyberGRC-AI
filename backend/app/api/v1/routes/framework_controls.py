from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.framework_control import (
    FrameworkControlCreate,
    FrameworkControlUpdate,
    FrameworkControlResponse,
)

from app.services.framework_control_service import (
    create_framework_control,
    get_all_framework_controls,
    get_framework_control_by_id,
    update_framework_control,
    delete_framework_control,
)

router = APIRouter(
    prefix="/framework-controls",
    tags=["Framework Controls"]
)


@router.post(
    "/",
    response_model=FrameworkControlResponse
)
def create_new_framework_control(
    control_data: FrameworkControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Create a framework control.
    """

    control = create_framework_control(
        db,
        control_data
    )

    if control == "FRAMEWORK_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Framework not found."
        )

    if control == "CONTROL_EXISTS":
        raise HTTPException(
            status_code=400,
            detail="Framework control already exists."
        )

    return control


@router.get(
    "/",
    response_model=list[FrameworkControlResponse]
)
def list_all_framework_controls(
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
    Get all framework controls.
    """

    return get_all_framework_controls(db)


@router.get(
    "/{control_id}",
    response_model=FrameworkControlResponse
)
def get_framework_control(
    control_id: int,
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
    Get framework control by ID.
    """

    control = get_framework_control_by_id(
        db,
        control_id
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Framework control not found."
        )

    return control


@router.patch(
    "/{control_id}",
    response_model=FrameworkControlResponse
)
def update_existing_framework_control(
    control_id: int,
    control_data: FrameworkControlUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Update framework control.
    """

    control = update_framework_control(
        db,
        control_id,
        control_data
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Framework control not found."
        )

    return control


@router.delete(
    "/{control_id}"
)
def delete_existing_framework_control(
    control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Delete framework control.
    """

    deleted = delete_framework_control(
        db,
        control_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Framework control not found."
        )

    return {
        "message": "Framework control deleted successfully."
    }