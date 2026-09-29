from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids
from app.auth.access import ensure_resource_owner_in_scope

from app.models.user import User
from app.models.risk import Risk

from app.schemas.risk import (
    RiskCreate,
    RiskUpdate,
    RiskResponse,
)

from app.services.risk_service import (
    create_risk,
    update_risk,
    delete_risk,
)

from app.services.continuous_risk_response_service import (
    get_continuous_risk_response,
)


router = APIRouter(
    prefix="/risks",
    tags=["Risk Management"]
)


# ==========================================================
# CREATE RISK
# ==========================================================

@router.post(
    "/",
    response_model=RiskResponse
)
def create_new_risk(
    risk_data: RiskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "create"
        )
    )
):
    """
    Create a new risk.

    The current user must have permission to create risks.

    The selected owner must belong to the user's
    organizational visibility scope.
    """

    # ------------------------------------------------------
    # Validate owner organizational scope
    # ------------------------------------------------------

    ensure_resource_owner_in_scope(
        db,
        current_user,
        risk_data.owner_id,
        "risks",
    )

    # ------------------------------------------------------
    # Create risk
    # ------------------------------------------------------

    risk = create_risk(
        db,
        risk_data,
        current_user.id
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Owner not found."
        )

    return risk


# ==========================================================
# LIST RISKS
# ==========================================================

@router.get(
    "/",
    response_model=list[RiskResponse]
)
def list_all_risks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view"
        )
    )
):
    """
    Get risks visible to the current user.

    Visibility is determined by the organizational
    hierarchy.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    return (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(visible_user_ids)
        )
        .all()
    )


# ==========================================================
# CONTINUOUS RISK RESPONSE
# ==========================================================

@router.get(
    "/{risk_id}/continuous-response"
)
def get_risk_continuous_response(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view"
        )
    )
):
    """
    Get the deterministic continuous risk response
    for a risk.

    The response is derived from the current continuous
    risk state and treatment state.

    This endpoint is read-only and does not:
      - modify the risk
      - modify the treatment
      - create corrective actions
      - send notifications
      - execute high-impact decisions

    High-impact decisions such as REASSESS_RISK and
    ESCALATE are explicitly marked as requiring human
    approval.
    """

    # ------------------------------------------------------
    # Enforce risk-level organizational visibility
    # ------------------------------------------------------

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
            Risk.owner_id.in_(visible_user_ids)
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    # ------------------------------------------------------
    # Build deterministic response
    # ------------------------------------------------------

    continuous_response = get_continuous_risk_response(
        db,
        risk,
        current_user=current_user,
    )

    # ------------------------------------------------------
    # Return explicit API representation
    # ------------------------------------------------------

    return {
        "risk_id": continuous_response.risk_id,
        "risk_state": continuous_response.risk_state,
        "treatment_state": continuous_response.treatment_state,
        "reassessment_required": (
            continuous_response.reassessment_required
        ),
        "response_required": (
            continuous_response.response_required
        ),
        "priority": continuous_response.priority.value,
        "human_approval_required": (
            continuous_response.human_approval_required
        ),
        "decisions": [
            {
                "decision": decision.decision.value,
                "priority": decision.priority.value,
                "reason_codes": list(decision.reason_codes),
                "human_approval_required": (
                    decision.human_approval_required
                ),
            }
            for decision in continuous_response.decisions
        ],
        "reasons": [
            {
                "code": reason.code.value,
                "severity": reason.severity,
                "message": reason.message,
                "resource_type": reason.resource_type,
                "resource_id": reason.resource_id,
            }
            for reason in continuous_response.reasons
        ],
    }


# ==========================================================
# GET SINGLE RISK
# ==========================================================

@router.get(
    "/{risk_id}",
    response_model=RiskResponse
)
def get_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view"
        )
    )
):
    """
    Get a risk by ID if the current user has
    organizational visibility.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
            Risk.owner_id.in_(visible_user_ids)
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    return risk


# ==========================================================
# UPDATE RISK
# ==========================================================

@router.patch(
    "/{risk_id}",
    response_model=RiskResponse
)
def update_existing_risk(
    risk_id: int,
    risk_data: RiskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "update"
        )
    )
):
    """
    Update a risk within the current user's
    organizational visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    # ------------------------------------------------------
    # Find risk within user's visibility scope
    # ------------------------------------------------------

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
            Risk.owner_id.in_(visible_user_ids)
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    # ------------------------------------------------------
    # Validate new owner if ownership is being changed
    # ------------------------------------------------------

    if risk_data.owner_id is not None:

        ensure_resource_owner_in_scope(
            db,
            current_user,
            risk_data.owner_id,
            "risks",
        )

    # ------------------------------------------------------
    # Update risk
    # ------------------------------------------------------

    updated_risk = update_risk(
        db,
        risk_id,
        risk_data
    )

    if updated_risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    if updated_risk == "OWNER_NOT_FOUND":
        raise HTTPException(
            status_code=404,
            detail="Owner not found."
        )

    return updated_risk


# ==========================================================
# DELETE RISK
# ==========================================================

@router.delete(
    "/{risk_id}"
)
def delete_existing_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "delete"
        )
    )
):
    """
    Delete a risk within the current user's
    organizational visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
            Risk.owner_id.in_(visible_user_ids)
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    deleted = delete_risk(
        db,
        risk_id
    )

    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found."
        )

    return {
        "message": "Risk deleted successfully."
    }