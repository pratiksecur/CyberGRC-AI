"""
Governed Risk Response Execution Service

Phase 59.5.1
------------

Provides the execution boundary for an approved continuous-risk response.

Important security properties:

- Only APPROVED decisions can execute.
- The current continuous response is recomputed before execution.
- The stored response_event_key must still match.
- The approved decision must still represent the current response.
- A decision can execute only once.
- Only explicitly supported response decisions are accepted.
- Required governance fields are validated before execution is recorded.
- Execution records preserve the approved decision snapshot.
- This layer does not invoke AI.
- This layer does not silently mutate risk/treatment/control data.

Phase 59.5.1 strengthens the execution boundary by validating the
integrity of the decision record before a governed execution record
is persisted.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.risk_response_decision import RiskResponseDecisionRecord
from app.models.risk_response_execution import RiskResponseExecutionRecord
from app.models.user import User
from app.services.continuous_risk_response_notification_service import (
    build_response_event_key,
)
from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseDecision,
    get_continuous_risk_response,
)
from app.services.risk_response_decision_service import (
    RiskResponseDecisionStatus,
    refresh_response_decision_state,
)


class RiskResponseExecutionStatus(str, Enum):
    EXECUTED = "EXECUTED"


class ResponseExecutionError(Exception):
    """Base error for governed response execution."""


class ResponseExecutionValidationError(ResponseExecutionError):
    """Raised when execution data is invalid."""


class ResponseExecutionNotApproved(ResponseExecutionError):
    """Raised when a decision is not approved for execution."""


class StaleResponseExecution(ResponseExecutionError):
    """Raised when the approved response is no longer current."""


class ResponseAlreadyExecuted(ResponseExecutionError):
    """Raised when a decision has already been executed."""


class UnsupportedResponseExecution(ResponseExecutionError):
    """Raised when the response decision has no execution boundary."""


EXECUTABLE_DECISIONS = frozenset(
    {
        RiskResponseDecision.REVIEW.value,
        RiskResponseDecision.REASSESS_RISK.value,
        RiskResponseDecision.UPDATE_TREATMENT.value,
        RiskResponseDecision.CORRECTIVE_ACTION_REVIEW.value,
        RiskResponseDecision.CONTROL_REVIEW.value,
        RiskResponseDecision.EVIDENCE_REVIEW.value,
        RiskResponseDecision.ESCALATE.value,
    }
)


def _require_actor(actor: User | None) -> User:
    if actor is None or actor.id is None:
        raise ResponseExecutionValidationError(
            "actor is required."
        )

    return actor


def _require_approved(
    decision: RiskResponseDecisionRecord,
) -> None:
    if decision.status != RiskResponseDecisionStatus.APPROVED.value:
        raise ResponseExecutionNotApproved(
            "Only an APPROVED response decision can be executed."
        )


def _validate_decision_integrity(
    decision: RiskResponseDecisionRecord,
) -> None:
    """
    Validate the persisted governance decision before execution.

    The execution record is an audit/governance snapshot. Therefore,
    required decision identity and governance fields must be present
    before that snapshot is persisted.
    """

    if decision.id is None:
        raise ResponseExecutionValidationError(
            "Response decision id is required."
        )

    if decision.risk_id is None:
        raise ResponseExecutionValidationError(
            "Response decision risk_id is required."
        )

    if not isinstance(decision.decision, str) or not decision.decision.strip():
        raise ResponseExecutionValidationError(
            "Response decision value is required."
        )

    if (
        not isinstance(decision.response_event_key, str)
        or not decision.response_event_key.strip()
    ):
        raise ResponseExecutionValidationError(
            "Response event key is required."
        )

    if (
        not isinstance(decision.priority, str)
        or not decision.priority.strip()
    ):
        raise ResponseExecutionValidationError(
            "Response decision priority is required."
        )

    if (
        not isinstance(decision.governance_level, str)
        or not decision.governance_level.strip()
    ):
        raise ResponseExecutionValidationError(
            "Response decision governance level is required."
        )

    if decision.human_approval_required is not True:
        raise ResponseExecutionValidationError(
            "Human approval verification is required before execution."
        )

    if decision.requested_by_id is None:
        raise ResponseExecutionValidationError(
            "Response decision requester is required."
        )

    if not decision.resolution_reason or not decision.resolution_reason.strip():
        raise ResponseExecutionValidationError(
            "An approval resolution reason is required before execution."
        )


def _validate_current_response(
    decision: RiskResponseDecisionRecord,
    current_response: ContinuousRiskResponse,
) -> None:
    if current_response.risk_id != decision.risk_id:
        raise StaleResponseExecution(
            "The current response belongs to a different risk."
        )

    current_event_key = build_response_event_key(
        current_response
    )

    if current_event_key != decision.response_event_key:
        raise StaleResponseExecution(
            "The approved response decision is stale because "
            "the underlying continuous risk response changed."
        )


def _validate_supported_decision(
    decision: RiskResponseDecisionRecord,
    current_response: ContinuousRiskResponse,
) -> None:
    current_decisions = {
        action.decision.value
        for action in current_response.decisions
    }

    if decision.decision not in current_decisions:
        raise StaleResponseExecution(
            "The approved decision is no longer present in "
            "the current continuous risk response."
        )

    if decision.decision not in EXECUTABLE_DECISIONS:
        raise UnsupportedResponseExecution(
            f"Response decision '{decision.decision}' "
            "does not have a governed execution boundary."
        )


def _find_existing_execution(
    db: Session,
    decision_id: int,
) -> RiskResponseExecutionRecord | None:
    return (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision_id
        )
        .first()
    )


def execute_approved_response(
    db: Session,
    decision: RiskResponseDecisionRecord,
    *,
    actor: User,
    current_response: ContinuousRiskResponse | None = None,
) -> RiskResponseExecutionRecord:
    """
    Execute the governed boundary for an approved response decision.

    This function records the governed execution event. It deliberately
    does not mutate the underlying risk, treatment, control, evidence,
    finding, or corrective-action records.

    Domain-specific side effects belong to later execution handlers.
    """

    actor = _require_actor(actor)

    _require_approved(decision)

    _validate_decision_integrity(decision)

    existing = _find_existing_execution(
        db,
        decision.id,
    )

    if existing is not None:
        raise ResponseAlreadyExecuted(
            "This response decision has already been executed."
        )

    if current_response is None:
        risk = decision.risk

        if risk is None:
            raise ResponseExecutionValidationError(
                "Risk associated with the response decision was not found."
            )

        current_response = get_continuous_risk_response(
            db,
            risk,
            current_user=actor,
        )

    _validate_current_response(
        decision,
        current_response,
    )

    _validate_supported_decision(
        decision,
        current_response,
    )

    # Refreshing here provides an additional lifecycle consistency check.
    # Approved decisions are terminal, so this will not change their state,
    # but it verifies the associated decision remains structurally valid.
    refresh_response_decision_state(
        db,
        decision,
        current_user=actor,
        current_response=current_response,
    )

    # An approved decision must remain approved after validation.
    if decision.status != RiskResponseDecisionStatus.APPROVED.value:
        raise ResponseExecutionNotApproved(
            "The response decision is no longer approved."
        )

    now = datetime.now(timezone.utc)

    execution = RiskResponseExecutionRecord(
        decision_id=decision.id,
        risk_id=decision.risk_id,
        decision=decision.decision,
        response_event_key=decision.response_event_key,
        status=RiskResponseExecutionStatus.EXECUTED.value,
        execution_action=decision.decision,
        human_approval_verified=True,
        response_event_verified=True,
        executed_by_id=actor.id,
        execution_reason=decision.resolution_reason.strip(),
        result_message=(
            "Governed response execution recorded successfully. "
            "No underlying risk-domain record was mutated."
        ),
        executed_at=now,
    )

    db.add(execution)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()

        existing = _find_existing_execution(
            db,
            decision.id,
        )

        if existing is not None:
            raise ResponseAlreadyExecuted(
                "This response decision has already been executed."
            ) from exc

        raise ResponseExecutionError(
            "The governed response execution could not be persisted."
        ) from exc

    return execution