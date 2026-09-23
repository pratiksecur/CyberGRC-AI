from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.auth.access import (
    ensure_resource_owner_in_scope,
)
from app.auth.permissions import (
    require_permission,
)
from app.auth.visibility import (
    get_visible_user_ids,
)
from app.core.roles import UserRole
from app.database.database import get_db
from app.models.risk import Risk
from app.models.risk_treatment import RiskTreatment
from app.models.user import User
from app.schemas.risk_treatment import (
    RiskTreatmentCreate,
    RiskTreatmentResponse,
    RiskTreatmentUpdate,
)
from app.services.risk_treatment_service import (
    create_risk_treatment,
    delete_risk_treatment,
    update_risk_treatment,
)


router = APIRouter(
    tags=["Risk Treatments"],
)


APPROVAL_ROLES = {
    UserRole.ADMIN.value,
    UserRole.GRC_MANAGER.value,
}


# ==========================================================
# HELPERS
# ==========================================================

def _visible_risk_treatments_query(
    db: Session,
    current_user: User,
):
    """
    A treatment is visible only when BOTH the parent Risk and
    the Treatment Owner are within the current user's scope.
    """

    visible_risk_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    visible_treatment_user_ids = (
        get_visible_user_ids(
            db,
            current_user,
            "risk_treatments",
        )
    )

    return (
        db.query(RiskTreatment)
        .join(
            Risk,
            RiskTreatment.risk_id == Risk.id,
        )
        .filter(
            Risk.owner_id.in_(
                visible_risk_user_ids
            ),
            RiskTreatment.owner_id.in_(
                visible_treatment_user_ids
            ),
        )
    )


def _get_visible_treatment(
    db: Session,
    current_user: User,
    treatment_id: int,
):
    return (
        _visible_risk_treatments_query(
            db,
            current_user,
        )
        .filter(
            RiskTreatment.id == treatment_id
        )
        .first()
    )


# ==========================================================
# CREATE
# ==========================================================

@router.post(
    "/risk-treatments/",
    response_model=RiskTreatmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_new_risk_treatment(
    treatment_data: RiskTreatmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risk_treatments",
            "create",
        )
    ),
):
    """
    Create a treatment for a risk visible to the current user.

    The treatment owner must also be within the creator's
    treatment visibility scope.
    """

    # ------------------------------------------------------
    # Verify parent risk is visible
    # ------------------------------------------------------

    visible_risk_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == treatment_data.risk_id,
            Risk.owner_id.in_(
                visible_risk_user_ids
            ),
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    # ------------------------------------------------------
    # Verify treatment owner is visible
    # ------------------------------------------------------

    ensure_resource_owner_in_scope(
        db,
        current_user,
        treatment_data.owner_id,
        "risk_treatments",
    )

    # ------------------------------------------------------
    # Prevent non-management roles from self-approving
    # ------------------------------------------------------

    if (
        treatment_data.acceptance_status.value
        in {"Approved", "Rejected"}
    ) and current_user.role not in APPROVAL_ROLES:
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized to approve "
                "or reject risk acceptance."
            ),
        )

    # ------------------------------------------------------
    # Attribute approval to the authenticated user
    # ------------------------------------------------------

    if (
        treatment_data.acceptance_status.value
        in {"Approved", "Rejected"}
    ):
        from datetime import datetime, timezone

        treatment_data.accepted_by_id = (
            current_user.id
        )

        treatment_data.accepted_at = (
            datetime.now(timezone.utc)
        )

    try:

        treatment = create_risk_treatment(
            db,
            treatment_data,
            current_user,
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return treatment


# ==========================================================
# LIST
# ==========================================================

@router.get(
    "/risk-treatments/",
    response_model=list[RiskTreatmentResponse],
)
def list_risk_treatments(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risk_treatments",
            "view",
        )
    ),
):
    return (
        _visible_risk_treatments_query(
            db,
            current_user,
        )
        .order_by(
            RiskTreatment.created_at.desc()
        )
        .all()
    )


# ==========================================================
# GET ONE
# ==========================================================

@router.get(
    "/risk-treatments/{treatment_id}",
    response_model=RiskTreatmentResponse,
)
def get_risk_treatment(
    treatment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risk_treatments",
            "view",
        )
    ),
):
    treatment = _get_visible_treatment(
        db,
        current_user,
        treatment_id,
    )

    if treatment is None:
        raise HTTPException(
            status_code=404,
            detail="Risk treatment not found.",
        )

    return treatment


# ==========================================================
# GET TREATMENTS FOR RISK
# ==========================================================

@router.get(
    "/risks/{risk_id}/treatments",
    response_model=list[RiskTreatmentResponse],
)
def list_risk_treatments_for_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risk_treatments",
            "view",
        )
    ),
):
    visible_risk_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
            Risk.owner_id.in_(
                visible_risk_user_ids
            ),
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    visible_treatment_user_ids = (
        get_visible_user_ids(
            db,
            current_user,
            "risk_treatments",
        )
    )

    return (
        db.query(RiskTreatment)
        .filter(
            RiskTreatment.risk_id == risk_id,
            RiskTreatment.owner_id.in_(
                visible_treatment_user_ids
            ),
        )
        .order_by(
            RiskTreatment.created_at.desc()
        )
        .all()
    )


# ==========================================================
# UPDATE
# ==========================================================

@router.patch(
    "/risk-treatments/{treatment_id}",
    response_model=RiskTreatmentResponse,
)
def update_existing_risk_treatment(
    treatment_id: int,
    treatment_data: RiskTreatmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risk_treatments",
            "update",
        )
    ),
):
    treatment = _get_visible_treatment(
        db,
        current_user,
        treatment_id,
    )

    if treatment is None:
        raise HTTPException(
            status_code=404,
            detail="Risk treatment not found.",
        )

    # ------------------------------------------------------
    # Validate reassignment
    # ------------------------------------------------------

    if treatment_data.owner_id is not None:

        ensure_resource_owner_in_scope(
            db,
            current_user,
            treatment_data.owner_id,
            "risk_treatments",
        )

    # ------------------------------------------------------
    # Prevent approval by unauthorized roles
    # ------------------------------------------------------

    if (
        treatment_data.acceptance_status is not None
        and treatment_data.acceptance_status.value
        in {"Approved", "Rejected"}
        and current_user.role not in APPROVAL_ROLES
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "You are not authorized to approve "
                "or reject risk acceptance."
            ),
        )

    try:

        updated = update_risk_treatment(
            db,
            treatment,
            treatment_data,
            current_user.id,
            current_user.role in APPROVAL_ROLES,
        )

    except PermissionError as exc:

        db.rollback()

        raise HTTPException(
            status_code=403,
            detail=str(exc),
        )

    except ValueError as exc:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return updated


# ==========================================================
# DELETE
# ==========================================================

@router.delete(
    "/risk-treatments/{treatment_id}",
)
def delete_existing_risk_treatment(
    treatment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risk_treatments",
            "delete",
        )
    ),
):
    treatment = _get_visible_treatment(
        db,
        current_user,
        treatment_id,
    )

    if treatment is None:
        raise HTTPException(
            status_code=404,
            detail="Risk treatment not found.",
        )

    delete_risk_treatment(
        db,
        treatment,
    )

    return {
        "message": (
            "Risk treatment deleted successfully."
        ),
    }