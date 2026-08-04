from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

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
    tags=["Risk-Control Mapping"]
)


@router.post(
    "/",
    response_model=RiskControlResponse
)
def assign_control(
    mapping: RiskControlCreate,
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
    Assign a control to a risk.
    """

    result = assign_control_to_risk(
        db,
        mapping.risk_id,
        mapping.control_id
    )

    if result == "RISK_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    if result == "CONTROL_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Control not found."
        )

    if result == "ALREADY_EXISTS":
        raise HTTPException(
            status_code=400,
            detail="Control is already assigned to this risk."
        )

    return result


@router.get(
    "/risk/{risk_id}",
    response_model=list[ControlResponse]
)
def get_controls(
    risk_id: int,
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
    Get all controls assigned to a risk.
    """

    return get_controls_for_risk(
        db,
        risk_id
    )


@router.get(
    "/control/{control_id}",
    response_model=list[RiskResponse]
)
def get_risks(
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
    Get all risks assigned to a control.
    """

    return get_risks_for_control(
        db,
        control_id
    )


@router.delete(
    "/{mapping_id}"
)
def remove_mapping(
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
    Remove a control-risk mapping.
    """

    deleted = remove_control_from_risk(
        db,
        mapping_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Mapping not found."
        )

    return {
        "message": "Mapping removed successfully."
    }