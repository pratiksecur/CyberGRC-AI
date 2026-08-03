from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.models.user import User

from app.schemas.risk import (
    RiskCreate,
    RiskUpdate,
    RiskResponse,
)

from app.services.risk_service import (
    create_risk,
    get_all_risks,
    get_risk_by_id,
    update_risk,
)

router = APIRouter(
    prefix="/risks",
    tags=["Risk Management"]
)


@router.post(
    "/",
    response_model=RiskResponse
)
def create_new_risk(
    risk_data: RiskCreate,
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
    Create a new risk.
    """

    risk = create_risk(db, risk_data)

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found."
        )

    return risk


@router.get(
    "/",
    response_model=list[RiskResponse]
)
def list_all_risks(
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
    Get all risks.
    """

    return get_all_risks(db)


@router.get(
    "/{risk_id}",
    response_model=RiskResponse
)
def get_risk(
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
    Get a risk by its ID.
    """

    risk = get_risk_by_id(db, risk_id)

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    return risk


@router.patch(
    "/{risk_id}",
    response_model=RiskResponse
)
def update_existing_risk(
    risk_id: int,
    risk_data: RiskUpdate,
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
    Update an existing risk.
    """

    risk = update_risk(
        db,
        risk_id,
        risk_data
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    if risk == "OWNER_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Owner not found."
        )

    return risk