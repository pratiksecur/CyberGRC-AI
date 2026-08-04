from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.control_framework_control import (
    ControlFrameworkControlCreate,
    ControlFrameworkControlResponse,
)

from app.schemas.control import ControlResponse
from app.schemas.framework_control import FrameworkControlResponse

from app.services.control_framework_control_service import (
    assign_framework_control,
    get_framework_controls_for_control,
    get_controls_for_framework_control,
    remove_framework_control_mapping,
)

router = APIRouter(
    prefix="/control-framework-controls",
    tags=["Control-Framework Mapping"]
)


@router.post(
    "/",
    response_model=ControlFrameworkControlResponse
)
def assign_control_to_framework_control(
    mapping_data: ControlFrameworkControlCreate,
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
    Assign a Control to a Framework Control.
    """

    mapping = assign_framework_control(
        db,
        mapping_data.control_id,
        mapping_data.framework_control_id,
    )

    if mapping == "CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    if mapping == "FRAMEWORK_CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Framework Control not found."
        )

    if mapping == "MAPPING_EXISTS":
        raise HTTPException(
            status_code=400,
            detail="Mapping already exists."
        )

    return mapping


@router.get(
    "/control/{control_id}",
    response_model=list[FrameworkControlResponse]
)
def get_framework_controls(
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
    Get all Framework Controls assigned to a Control.
    """

    return get_framework_controls_for_control(
        db,
        control_id,
    )


@router.get(
    "/framework-control/{framework_control_id}",
    response_model=list[ControlResponse]
)
def get_controls(
    framework_control_id: int,
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
    Get all Controls assigned to a Framework Control.
    """

    return get_controls_for_framework_control(
        db,
        framework_control_id,
    )


@router.delete(
    "/{mapping_id}"
)
def delete_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    )
):
    """
    Remove Control-Framework mapping.
    """

    deleted = remove_framework_control_mapping(
        db,
        mapping_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Mapping not found."
        )

    return {
        "message": "Mapping deleted successfully."
    }