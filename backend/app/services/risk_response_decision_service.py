"""
Governed Risk Response Decision Service

Phase 59.1 / 59.2
------------------

Persists and governs a human decision request derived from the
continuous risk response.

This service does NOT execute the proposed response.

It is responsible for:

- creating governance records
- preventing duplicate open decisions
- tracking the response event identity
- detecting stale decisions
- enforcing lifecycle transitions
- requiring human resolution reasons
- validating future deferrals
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)
from app.models.user import User

from app.services.continuous_risk_response_notification_service import (
    build_response_event_key,
    get_response_governance_level,
)

from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    get_continuous_risk_response,
)


class RiskResponseDecisionStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"
    STALE = "STALE"


class ResponseDecisionError(Exception):
    """
    Base error for governed response decision operations.
    """


class InvalidResponseDecisionTransition(
    ResponseDecisionError
):
    """
    Raised when a decision cannot move to the requested status.
    """


class ResponseDecisionValidationError(
    ResponseDecisionError
):
    """
    Raised when required governance data is missing or invalid.
    """


class StaleResponseDecision(
    ResponseDecisionError
):
    """
    Raised when an approval is attempted against an old response.
    """


def _require_nonblank(
    value: str | None,
    field_name: str,
) -> str:

    if value is None or not value.strip():
        raise ResponseDecisionValidationError(
            f"{field_name} is required."
        )

    return value.strip()


def _primary_decision(
    response: ContinuousRiskResponse,
):
    if not response.decisions:
        raise ResponseDecisionValidationError(
            "A response decision must contain at least one decision."
        )

    priority_rank = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4,
    }

    return max(
        response.decisions,
        key=lambda action: (
            priority_rank[
                action.priority.value
                if hasattr(action.priority, "value")
                else action.priority
            ],
            action.decision.value,
        ),
    )


def _reason_codes(
    response: ContinuousRiskResponse,
) -> list[str]:

    return sorted(
        {
            code
            for action in response.decisions
            for code in action.reason_codes
        }
    )


def _find_open_decision(
    db: Session,
    risk_id: int,
    response_event_key: str,
) -> RiskResponseDecisionRecord | None:

    return (
        db.query(
            RiskResponseDecisionRecord
        )
        .filter(
            RiskResponseDecisionRecord.risk_id == risk_id,
            RiskResponseDecisionRecord.response_event_key
            == response_event_key,
            RiskResponseDecisionRecord.status.in_(
                [
                    RiskResponseDecisionStatus.PENDING.value,
                    RiskResponseDecisionStatus.DEFERRED.value,
                ]
            ),
        )
        .order_by(
            RiskResponseDecisionRecord.id.desc()
        )
        .first()
    )


def create_response_decision(
    db: Session,
    risk: Risk,
    requested_by: User,
    *,
    assigned_to: User | None = None,
    response: ContinuousRiskResponse | None = None,
) -> RiskResponseDecisionRecord:
    """
    Create one governed decision request for the current
    response posture.

    Repeated creation attempts for the same open response
    event return the existing open record.
    """

    if (
        requested_by is None
        or requested_by.id is None
    ):
        raise ResponseDecisionValidationError(
            "requested_by is required."
        )

    if response is None:
        response = get_continuous_risk_response(
            db,
            risk,
            current_user=requested_by,
        )

    if response.risk_id != risk.id:
        raise ResponseDecisionValidationError(
            "Response risk_id does not match the supplied risk."
        )

    if not response.response_required:
        raise ResponseDecisionValidationError(
            "A response decision can only be created "
            "when a response is required."
        )

    primary = _primary_decision(
        response
    )

    governance = get_response_governance_level(
        response
    )

    event_key = build_response_event_key(
        response
    )

    existing = _find_open_decision(
        db,
        risk.id,
        event_key,
    )

    if existing is not None:
        return existing

    record = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision=primary.decision.value,
        priority=(
            primary.priority.value
            if hasattr(primary.priority, "value")
            else primary.priority
        ),
        governance_level=governance.value,
        status=RiskResponseDecisionStatus.PENDING.value,
        human_approval_required=(
            response.human_approval_required
        ),
        response_event_key=event_key,
        reason_codes=_reason_codes(response),
        risk_state=response.risk_state,
        treatment_state=response.treatment_state,
        reassessment_required=(
            response.reassessment_required
        ),
        response_required=(
            response.response_required
        ),
        requested_by_id=requested_by.id,
        assigned_to_id=(
            assigned_to.id
            if assigned_to is not None
            else None
        ),
    )

    db.add(record)
    db.flush()

    return record


def refresh_response_decision_state(
    db: Session,
    decision: RiskResponseDecisionRecord,
    *,
    current_user: User | None = None,
    current_response: ContinuousRiskResponse | None = None,
) -> RiskResponseDecisionRecord:
    """
    Mark an open decision STALE when its reviewed response
    is no longer current.
    """

    if decision.status not in {
        RiskResponseDecisionStatus.PENDING.value,
        RiskResponseDecisionStatus.DEFERRED.value,
    }:
        return decision

    risk = (
        db.query(Risk)
        .filter(
            Risk.id == decision.risk_id
        )
        .first()
    )

    if risk is None:
        raise ResponseDecisionValidationError(
            "Risk associated with the response decision "
            "was not found."
        )

    if current_response is None:
        current_response = (
            get_continuous_risk_response(
                db,
                risk,
                current_user=current_user,
            )
        )

    current_event_key = (
        build_response_event_key(
            current_response
        )
    )

    if (
        current_event_key
        != decision.response_event_key
    ):

        decision.status = (
            RiskResponseDecisionStatus.STALE.value
        )

        decision.resolved_at = (
            datetime.now(timezone.utc)
        )

        decision.resolution_reason = (
            "The underlying continuous risk response "
            "changed after this decision was created."
        )

        db.flush()

    return decision


def transition_response_decision(
    db: Session,
    decision: RiskResponseDecisionRecord,
    new_status: RiskResponseDecisionStatus,
    *,
    actor: User,
    resolution_reason: str | None = None,
    deferred_until: datetime | None = None,
    current_user: User | None = None,
    current_response: ContinuousRiskResponse | None = None,
) -> RiskResponseDecisionRecord:
    """
    Apply a governed lifecycle transition.

    The service itself does not execute the underlying
    response.

    High-impact decisions cannot be approved against
    a stale response.

    All human resolution decisions require a reason.
    """

    if (
        actor is None
        or actor.id is None
    ):
        raise ResponseDecisionValidationError(
            "actor is required."
        )

    allowed_open_states = {
        RiskResponseDecisionStatus.PENDING.value,
        RiskResponseDecisionStatus.DEFERRED.value,
    }

    if decision.status not in allowed_open_states:
        raise InvalidResponseDecisionTransition(
            f"Decision in status {decision.status} cannot transition."
        )

    refreshed = refresh_response_decision_state(
        db,
        decision,
        current_user=current_user,
        current_response=current_response,
    )

    if (
        refreshed.status
        == RiskResponseDecisionStatus.STALE.value
    ):

        if (
            new_status
            == RiskResponseDecisionStatus.APPROVED
        ):
            raise StaleResponseDecision(
                "The response decision is stale and cannot be approved."
            )

        raise InvalidResponseDecisionTransition(
            "A stale response decision cannot be transitioned."
        )

    if new_status not in {
        RiskResponseDecisionStatus.APPROVED,
        RiskResponseDecisionStatus.REJECTED,
        RiskResponseDecisionStatus.DEFERRED,
    }:
        raise InvalidResponseDecisionTransition(
            f"Unsupported transition target: {new_status.value}."
        )

    reason = _require_nonblank(
        resolution_reason,
        "resolution_reason",
    )

    if (
        new_status
        == RiskResponseDecisionStatus.DEFERRED
    ):

        if deferred_until is None:
            raise ResponseDecisionValidationError(
                "deferred_until is required when deferring "
                "a response decision."
            )

        now = datetime.now(
            timezone.utc
        )

        if deferred_until <= now:
            raise ResponseDecisionValidationError(
                "deferred_until must be in the future."
            )

    decision.status = new_status.value

    decision.resolution_reason = reason

    decision.deferred_until = (
        deferred_until
        if (
            new_status
            == RiskResponseDecisionStatus.DEFERRED
        )
        else None
    )

    if new_status in {
        RiskResponseDecisionStatus.APPROVED,
        RiskResponseDecisionStatus.REJECTED,
    }:

        decision.resolved_at = (
            datetime.now(timezone.utc)
        )

    else:

        decision.resolved_at = None

    db.flush()

    return decision