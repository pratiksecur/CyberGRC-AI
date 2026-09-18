from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids

from app.models.user import User
from app.models.risk import Risk
from app.models.control import Control
from app.models.risk_control import RiskControl

from app.schemas.risk_control import (
    RiskControlCreate,
    RiskControlResponse,
)

from app.schemas.control import ControlResponse
from app.schemas.risk import RiskResponse

from app.services.risk_control_service import (
    assign_control_to_risk,
    get_controls_for_risk,
    get_risks_for_control,
    remove_control_from_risk,
)


router = APIRouter(
    prefix="/risk-controls",
    tags=["Risk-Control Mapping"],
)


# ==========================================================
# CREATE RISK-CONTROL MAPPING
# ==========================================================

@router.post(
    "/",
    response_model=RiskControlResponse,
)
def assign_control(
    mapping: RiskControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "control_framework_mappings",
            "create",
        )
    ),
):
    """
    Assign a Control to a Risk.

    The authenticated user must have permission to create
    mappings, and both the Risk and Control must belong to
    the user's organizational visibility scope.

    This prevents a user from creating relationships
    involving resources they cannot access.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    # ------------------------------------------------------
    # Verify Risk exists and is within scope
    # ------------------------------------------------------

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == mapping.risk_id,
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found.",
        )

    if risk.owner_id not in visible_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot create a mapping for a "
                "Risk outside your organizational scope."
            ),
        )

    # ------------------------------------------------------
    # Verify Control exists and is within scope
    # ------------------------------------------------------

    control = (
        db.query(Control)
        .filter(
            Control.id == mapping.control_id,
        )
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    if control.owner_id not in visible_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot create a mapping for a "
                "Control outside your organizational scope."
            ),
        )

    # ------------------------------------------------------
    # Create mapping
    # ------------------------------------------------------

    result = assign_control_to_risk(
        db,
        mapping.risk_id,
        mapping.control_id,
    )

    if result == "RISK_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found.",
        )

    if result == "CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    if result == "ALREADY_EXISTS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Control is already assigned to this risk.",
        )

    return result


# ==========================================================
# GET CONTROLS FOR RISK
# ==========================================================

@router.get(
    "/risk/{risk_id}",
    response_model=list[ControlResponse],
)
def get_controls(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "control_framework_mappings",
            "view",
        )
    ),
):
    """
    Get all Controls assigned to a Risk.

    The Risk must belong to the authenticated user's
    organizational visibility scope.

    This prevents an IDOR where a user could enumerate
    controls attached to another user's Risk by changing
    the risk_id.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    # ------------------------------------------------------
    # Verify Risk exists and is within scope
    # ------------------------------------------------------

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found.",
        )

    if risk.owner_id not in visible_user_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found.",
        )

    # ------------------------------------------------------
    # Return mapped Controls
    # ------------------------------------------------------

    return get_controls_for_risk(
        db,
        risk_id,
        visible_user_ids,
    )


# ==========================================================
# GET RISKS FOR CONTROL
# ==========================================================

@router.get(
    "/control/{control_id}",
    response_model=list[RiskResponse],
)
def get_risks(
    control_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "control_framework_mappings",
            "view",
        )
    ),
):
    """
    Get all Risks assigned to a Control.

    The Control must belong to the authenticated user's
    organizational visibility scope.

    This prevents an IDOR where a user could enumerate
    Risks attached to another user's Control.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    # ------------------------------------------------------
    # Verify Control exists and is within scope
    # ------------------------------------------------------

    control = (
        db.query(Control)
        .filter(
            Control.id == control_id,
        )
        .first()
    )

    if control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    if control.owner_id not in visible_user_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Control not found.",
        )

    # ------------------------------------------------------
    # Return mapped Risks
    # ------------------------------------------------------

    return get_risks_for_control(
        db,
        control_id,
        visible_user_ids,
    )


# ==========================================================
# DELETE RISK-CONTROL MAPPING
# ==========================================================

@router.delete(
    "/{mapping_id}",
)
def remove_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "control_framework_mappings",
            "delete",
        )
    ),
):
    """
    Remove a Risk-Control mapping.

    The mapping may only be removed when both the
    associated Risk and Control are within the
    authenticated user's organizational scope.

    This prevents a user with delete permission from
    deleting a relationship involving an out-of-scope
    resource.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "control_framework_mappings",
    )

    # ------------------------------------------------------
    # Load mapping and its related resources
    # ------------------------------------------------------

    mapping = (
        db.query(RiskControl)
        .filter(
            RiskControl.id == mapping_id,
        )
        .first()
    )

    if mapping is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found.",
        )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == mapping.risk_id,
        )
        .first()
    )

    control = (
        db.query(Control)
        .filter(
            Control.id == mapping.control_id,
        )
        .first()
    )

    if risk is None or control is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found.",
        )

    # ------------------------------------------------------
    # Verify both resources are within scope
    # ------------------------------------------------------

    if (
        risk.owner_id not in visible_user_ids
        or control.owner_id not in visible_user_ids
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found.",
        )

    # ------------------------------------------------------
    # Delete mapping
    # ------------------------------------------------------

    deleted = remove_control_from_risk(
        db,
        mapping_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found.",
        )

    return {
        "message": "Mapping removed successfully.",
    }