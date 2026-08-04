from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.control import (
    ControlCreate,
    ControlUpdate,
    ControlResponse,
)

from app.services.control_service import (
    create_control,
    get_all_controls,
    get_control_by_id,
    update_control,
    delete_control,
)

router = APIRouter(
    prefix="/controls",
    tags=["Controls Management"]
)


@router.post(
    "/",
    response_model=ControlResponse
)
def create_new_control(
    control_data: ControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.RISK_ANALYST,
        )
    )
):
    """
    Create a new control.
    """

    control = create_control(db, control_data)

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found."
        )

    return control


@router.get(
    "/",
    response_model=list[ControlResponse]
)
def list_all_controls(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.RISK_ANALYST,
            UserRole.AUDITOR,
        )
    )
):
    """
    Get all controls.
    """

    return get_all_controls(db)


@router.get(
    "/{control_id}",
    response_model=ControlResponse
)
def get_control(
    control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.RISK_ANALYST,
            UserRole.AUDITOR,
        )
    )
):
    """
    Get a control by its ID.
    """

    control = get_control_by_id(db, control_id)

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    return control


@router.patch(
    "/{control_id}",
    response_model=ControlResponse
)
def update_existing_control(
    control_id: int,
    control_data: ControlUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.RISK_ANALYST,
        )
    )
):
    """
    Update an existing control.
    """

    control = update_control(
        db,
        control_id,
        control_data
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    if control == "OWNER_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Owner not found."
        )

    return control


@router.delete(
    "/{control_id}"
)
def delete_existing_control(
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
    Delete an existing control.
    """

    deleted = delete_control(
        db,
        control_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    return {
        "message": "Control deleted successfully."
    }