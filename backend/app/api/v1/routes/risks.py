from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission, require_roles
from app.auth.visibility import get_visible_user_ids
from app.auth.access import ensure_resource_owner_in_scope

from app.core.roles import UserRole

from app.models.user import User
from app.models.risk import Risk
from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)

from app.schemas.risk import (
    RiskCreate,
    RiskUpdate,
    RiskResponse,
)

from app.schemas.risk_response_decision import (
    RiskResponseDecisionCreate,
    RiskResponseDecisionResolution,
    RiskResponseDecisionDefer,
    RiskResponseDecisionResponse,
)

from app.schemas.risk_response_execution import (
    RiskResponseExecutionResponse,
)

from app.services.risk_service import (
    create_risk,
    update_risk,
    delete_risk,
)

from app.services.continuous_risk_response_service import (
    get_continuous_risk_response,
)

from app.services.risk_response_decision_service import (
    InvalidResponseDecisionTransition,
    ResponseDecisionValidationError,
    RiskResponseDecisionStatus,
    StaleResponseDecision,
    create_response_decision,
    refresh_response_decision_state,
    transition_response_decision,
)

from app.services.risk_response_execution_service import (
    ResponseAlreadyExecuted,
    ResponseExecutionNotApproved,
    ResponseExecutionValidationError,
    StaleResponseExecution,
    UnsupportedResponseExecution,
    execute_approved_response,
)


router = APIRouter(
    prefix="/risks",
    tags=["Risk Management"],
)


# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _get_visible_risk(
    db: Session,
    current_user: User,
    risk_id: int,
) -> Risk:
    """
    Resolve a risk only if it belongs to the current user's
    resource-specific visibility scope.

    This prevents IDOR/BOLA through risk IDs.
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
            Risk.owner_id.in_(visible_user_ids),
        )
        .first()
    )

    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found.",
        )

    return risk


def _get_visible_decision(
    db: Session,
    current_user: User,
    risk_id: int,
    decision_id: int,
) -> RiskResponseDecisionRecord:
    """
    Resolve a response decision only when both:
      1. the parent risk is visible
      2. the decision belongs to that risk

    This prevents direct decision-ID enumeration from bypassing
    risk-level visibility.
    """

    _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    decision = (
        db.query(RiskResponseDecisionRecord)
        .filter(
            RiskResponseDecisionRecord.id == decision_id,
            RiskResponseDecisionRecord.risk_id == risk_id,
        )
        .first()
    )

    if decision is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Response decision not found.",
        )

    return decision


def _decision_response(
    decision: RiskResponseDecisionRecord,
) -> RiskResponseDecisionResponse:
    return RiskResponseDecisionResponse.model_validate(
        decision
    )


def _handle_decision_service_error(
    exc: Exception,
) -> None:
    """
    Translate domain lifecycle failures into stable HTTP
    semantics.

    This function always raises.
    """

    if isinstance(exc, StaleResponseDecision):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if isinstance(exc, InvalidResponseDecisionTransition):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if isinstance(exc, ResponseDecisionValidationError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )

    raise exc


# ==========================================================
# CREATE RISK
# ==========================================================

@router.post(
    "/",
    response_model=RiskResponse,
)
def create_new_risk(
    risk_data: RiskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "create",
        )
    ),
):
    """
    Create a new risk.

    The current user must have permission to create risks.

    The selected owner must belong to the user's
    organizational visibility scope.
    """

    ensure_resource_owner_in_scope(
        db,
        current_user,
        risk_data.owner_id,
        "risks",
    )

    risk = create_risk(
        db,
        risk_data,
        current_user.id,
    )

    if risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found.",
        )

    return risk


# ==========================================================
# LIST RISKS
# ==========================================================

@router.get(
    "/",
    response_model=list[RiskResponse],
)
def list_all_risks(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Get risks visible to the current user.
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
# PHASE 59.2
# GOVERNED RESPONSE DECISION
# ==========================================================

@router.post(
    "/{risk_id}/response-decisions",
    response_model=RiskResponseDecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_risk_response_decision(
    risk_id: int,
    decision_data: RiskResponseDecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "update",
        )
    ),
):
    """
    Create a governed decision request for the current
    continuous risk response.

    The response posture is calculated server-side.

    The client cannot submit:
      - decision
      - priority
      - governance level
      - reason codes
      - response event key
      - risk state
      - treatment state

    This prevents clients from forging governance state.
    """

    risk = _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    assigned_to = None

    if decision_data.assigned_to_id is not None:

        visible_user_ids = get_visible_user_ids(
            db,
            current_user,
            "risks",
        )

        if decision_data.assigned_to_id not in visible_user_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You cannot assign a response decision "
                    "outside your organizational scope."
                ),
            )

        assigned_to = (
            db.query(User)
            .filter(
                User.id == decision_data.assigned_to_id
            )
            .first()
        )

        if assigned_to is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assigned user not found.",
            )

    try:

        decision = create_response_decision(
            db,
            risk,
            current_user,
            assigned_to=assigned_to,
        )

        db.commit()
        db.refresh(decision)

        return decision

    except (
        ResponseDecisionValidationError,
        InvalidResponseDecisionTransition,
        StaleResponseDecision,
    ) as exc:

        db.rollback()

        _handle_decision_service_error(
            exc
        )


# ==========================================================
# LIST RESPONSE DECISIONS
# ==========================================================

@router.get(
    "/{risk_id}/response-decisions",
    response_model=list[RiskResponseDecisionResponse],
)
def list_risk_response_decisions(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    List governed response decisions for a visible risk.

    Open decisions are refreshed against the current
    continuous response before being returned.

    This ensures an old governance request becomes STALE
    when the underlying response event changes.
    """

    risk = _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    decisions = (
        db.query(RiskResponseDecisionRecord)
        .filter(
            RiskResponseDecisionRecord.risk_id == risk.id
        )
        .order_by(
            RiskResponseDecisionRecord.created_at.desc(),
            RiskResponseDecisionRecord.id.desc(),
        )
        .all()
    )

    changed = False

    for decision in decisions:

        previous_status = decision.status

        refresh_response_decision_state(
            db,
            decision,
            current_user=current_user,
        )

        if decision.status != previous_status:
            changed = True

    if changed:
        db.commit()

        for decision in decisions:
            db.refresh(decision)

    return decisions


# ==========================================================
# GET SINGLE RESPONSE DECISION
# ==========================================================

@router.get(
    "/{risk_id}/response-decisions/{decision_id}",
    response_model=RiskResponseDecisionResponse,
)
def get_risk_response_decision(
    risk_id: int,
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Get one governed response decision.

    The decision must belong to the requested risk and
    the risk must be within the current user's visibility.
    """

    decision = _get_visible_decision(
        db,
        current_user,
        risk_id,
        decision_id,
    )

    previous_status = decision.status

    refresh_response_decision_state(
        db,
        decision,
        current_user=current_user,
    )

    if decision.status != previous_status:
        db.commit()
        db.refresh(decision)

    return decision


# ==========================================================
# APPROVE RESPONSE DECISION
# ==========================================================

@router.post(
    "/{risk_id}/response-decisions/{decision_id}/approve",
    response_model=RiskResponseDecisionResponse,
)
def approve_risk_response_decision(
    risk_id: int,
    decision_id: int,
    resolution: RiskResponseDecisionResolution,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    ),
):
    """
    Approve a governed response decision.

    Approval is intentionally limited to Admin and
    GRC Manager.

    IMPORTANT:
    Approval records the human governance decision only.
    It does NOT execute REASSESS_RISK, ESCALATE,
    CONTROL_REVIEW, or any other response.
    """

    decision = _get_visible_decision(
        db,
        current_user,
        risk_id,
        decision_id,
    )

    risk = _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    response = get_continuous_risk_response(
        db,
        risk,
        current_user=current_user,
    )

    try:

        updated = transition_response_decision(
            db,
            decision,
            RiskResponseDecisionStatus.APPROVED,
            actor=current_user,
            resolution_reason=resolution.resolution_reason,
            current_user=current_user,
            current_response=response,
        )

        db.commit()
        db.refresh(updated)

        return updated

    except (
        ResponseDecisionValidationError,
        InvalidResponseDecisionTransition,
        StaleResponseDecision,
    ) as exc:

        db.rollback()

        _handle_decision_service_error(
            exc
        )


# ==========================================================
# REJECT RESPONSE DECISION
# ==========================================================

@router.post(
    "/{risk_id}/response-decisions/{decision_id}/reject",
    response_model=RiskResponseDecisionResponse,
)
def reject_risk_response_decision(
    risk_id: int,
    decision_id: int,
    resolution: RiskResponseDecisionResolution,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    ),
):
    """
    Reject a governed response decision.

    A rejection requires an explicit human justification.
    """

    decision = _get_visible_decision(
        db,
        current_user,
        risk_id,
        decision_id,
    )

    risk = _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    response = get_continuous_risk_response(
        db,
        risk,
        current_user=current_user,
    )

    try:

        updated = transition_response_decision(
            db,
            decision,
            RiskResponseDecisionStatus.REJECTED,
            actor=current_user,
            resolution_reason=resolution.resolution_reason,
            current_user=current_user,
            current_response=response,
        )

        db.commit()
        db.refresh(updated)

        return updated

    except (
        ResponseDecisionValidationError,
        InvalidResponseDecisionTransition,
        StaleResponseDecision,
    ) as exc:

        db.rollback()

        _handle_decision_service_error(
            exc
        )


# ==========================================================
# DEFER RESPONSE DECISION
# ==========================================================

@router.post(
    "/{risk_id}/response-decisions/{decision_id}/defer",
    response_model=RiskResponseDecisionResponse,
)
def defer_risk_response_decision(
    risk_id: int,
    decision_id: int,
    resolution: RiskResponseDecisionDefer,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    ),
):
    """
    Defer a governed response decision.

    Deferral requires:
      - an explicit reason
      - a future timestamp

    A deferred decision remains an open governance record
    and can later become STALE if the underlying response
    event changes.
    """

    decision = _get_visible_decision(
        db,
        current_user,
        risk_id,
        decision_id,
    )

    risk = _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    response = get_continuous_risk_response(
        db,
        risk,
        current_user=current_user,
    )

    try:

        updated = transition_response_decision(
            db,
            decision,
            RiskResponseDecisionStatus.DEFERRED,
            actor=current_user,
            resolution_reason=resolution.resolution_reason,
            deferred_until=resolution.deferred_until,
            current_user=current_user,
            current_response=response,
        )

        db.commit()
        db.refresh(updated)

        return updated

    except (
        ResponseDecisionValidationError,
        InvalidResponseDecisionTransition,
        StaleResponseDecision,
    ) as exc:

        db.rollback()

        _handle_decision_service_error(
            exc
        )


# ==========================================================
# PHASE 59.4
# EXECUTE APPROVED RESPONSE DECISION
# ==========================================================

@router.post(
    "/{risk_id}/response-decisions/{decision_id}/execute",
    response_model=RiskResponseExecutionResponse,
)
def execute_risk_response_decision(
    risk_id: int,
    decision_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
        )
    ),
):
    """
    Execute an approved governed risk response decision.

    Execution is intentionally limited to Admin and
    GRC Manager.

    Security boundary:

      1. The parent risk must be visible.
      2. The decision must belong to that risk.
      3. The decision must already be APPROVED.
      4. The approval must still match the current
         continuous risk response event.
      5. The decision must not already have an execution.
      6. The response decision must remain executable.

    The execution service remains authoritative for
    approval, event-key and duplicate-execution checks.

    This endpoint does not directly mutate risk,
    treatment, control, evidence or other GRC state.
    """

    decision = _get_visible_decision(
        db,
        current_user,
        risk_id,
        decision_id,
    )

    risk = _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    try:

        execution = execute_approved_response(
            db,
            decision,
            actor=current_user,
        )

        db.commit()
        db.refresh(execution)

        return execution

    except (
        ResponseExecutionNotApproved,
        StaleResponseExecution,
        ResponseAlreadyExecuted,
        UnsupportedResponseExecution,
        ResponseExecutionValidationError,
    ) as exc:

        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
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
            "view",
        )
    ),
):
    """
    Get the deterministic continuous risk response
    for a risk.

    This endpoint remains read-only.
    """

    risk = _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    continuous_response = get_continuous_risk_response(
        db,
        risk,
        current_user=current_user,
    )

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
                "reason_codes": list(
                    decision.reason_codes
                ),
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
    response_model=RiskResponse,
)
def get_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Get a risk by ID if the current user has
    organizational visibility.
    """

    return _get_visible_risk(
        db,
        current_user,
        risk_id,
    )


# ==========================================================
# UPDATE RISK
# ==========================================================

@router.patch(
    "/{risk_id}",
    response_model=RiskResponse,
)
def update_existing_risk(
    risk_id: int,
    risk_data: RiskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "update",
        )
    ),
):
    """
    Update a risk within the current user's
    organizational visibility scope.
    """

    risk = _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    if risk_data.owner_id is not None:

        ensure_resource_owner_in_scope(
            db,
            current_user,
            risk_data.owner_id,
            "risks",
        )

    updated_risk = update_risk(
        db,
        risk_id,
        risk_data,
    )

    if updated_risk is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found.",
        )

    if updated_risk == "OWNER_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found.",
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
            "delete",
        )
    ),
):
    """
    Delete a risk within the current user's
    organizational visibility scope.
    """

    _get_visible_risk(
        db,
        current_user,
        risk_id,
    )

    deleted = delete_risk(
        db,
        risk_id,
    )

    if deleted is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found.",
        )

    return {
        "message": "Risk deleted successfully."
    }