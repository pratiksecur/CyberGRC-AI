from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids

from app.models.user import User
from app.models.control import Control

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
        require_permission(
            "control_framework_mappings",
            "create"
        )
    )
):
    """
    Assign a Control to a Framework Control.

    The Control must belong to a user inside the
    current user's organizational visibility scope.
    """

    # ------------------------------------------------------
    # Load the Control
    # ------------------------------------------------------

    control = (
        db.query(Control)
        .filter(
            Control.id == mapping_data.control_id
        )
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    # ------------------------------------------------------
    # Check Control owner's organizational scope
    # ------------------------------------------------------

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    if control.owner_id not in visible_user_ids:
        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot create a mapping for a "
                "Control outside your organizational scope."
            )
        )

    # ------------------------------------------------------
    # Create mapping
    # ------------------------------------------------------

    mapping = assign_framework_control(
        db,
        mapping_data.control_id,
        mapping_data.framework_control_id,
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
        require_permission(
            "control_framework_mappings",
            "view"
        )
    )
):
    """
    Get all Framework Controls assigned to a Control.

    Access is limited to Controls visible to the
    current user.
    """

    # ------------------------------------------------------
    # Load the Control
    # ------------------------------------------------------

    control = (
        db.query(Control)
        .filter(
            Control.id == control_id
        )
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    # ------------------------------------------------------
    # Check organizational scope
    # ------------------------------------------------------

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    if control.owner_id not in visible_user_ids:
        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot access mappings for a "
                "Control outside your organizational scope."
            )
        )

    # ------------------------------------------------------
    # Return mappings
    # ------------------------------------------------------

    return get_framework_controls_for_control(
        db,
        control_id,
        visible_user_ids,
    )


@router.get(
    "/framework-control/{framework_control_id}",
    response_model=list[ControlResponse]
)
def get_controls(
    framework_control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "control_framework_mappings",
            "view"
        )
    )
):
    """
    Get all Controls assigned to a Framework Control.

    Only Controls whose owners are inside the current
    user's visibility scope are returned.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    return get_controls_for_framework_control(
        db,
        framework_control_id,
        visible_user_ids,
    )


@router.delete(
    "/{mapping_id}"
)
def delete_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "control_framework_mappings",
            "delete"
        )
    )
):
    """
    Remove a Control-Framework mapping.

    The mapping can only be removed when the mapped
    Control is within the current user's scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    deleted = remove_framework_control_mapping(
        db,
        mapping_id,
        visible_user_ids,
    )

    if deleted == "MAPPING_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Mapping not found."
        )

    if deleted == "MAPPING_OUT_OF_SCOPE":
        raise HTTPException(
            status_code=403,
            detail=(
                "You cannot modify a mapping for a "
                "Control outside your organizational scope."
            )
        )

    return {
        "message": "Mapping deleted successfully."
    }