from datetime import datetime, timedelta, timezone

import pytest

from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)
from app.services.continuous_risk_response_notification_service import (
    ResponseGovernanceLevel,
    build_response_event_key,
)
from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
    RiskResponsePriority,
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


def _response(
    *,
    risk_id=1,
    risk_state="REASSESSMENT_REQUIRED",
    treatment_state="REQUIRES_REASSESSMENT",
    decision=RiskResponseDecision.REASSESS_RISK,
    priority=RiskResponsePriority.HIGH,
    human_approval_required=True,
    reason_codes=("TREATMENT_MISSING_RESIDUAL",),
):
    action = RiskResponseAction(
        decision=decision,
        priority=priority,
        reason_codes=reason_codes,
        human_approval_required=human_approval_required,
    )

    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state=risk_state,
        treatment_state=treatment_state,
        reassessment_required=(
            risk_state == "REASSESSMENT_REQUIRED"
        ),
        response_required=True,
        priority=priority,
        decisions=(action,),
        human_approval_required=human_approval_required,
        reasons=(),
    )


def test_create_response_decision_persists_governance_snapshot(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        employee,
        response=response,
    )

    assert record.id is not None
    assert record.risk_id == risk.id
    assert record.decision == "REASSESS_RISK"
    assert record.priority == "HIGH"
    assert (
        record.governance_level
        == ResponseGovernanceLevel.HUMAN_APPROVAL_REQUIRED.value
    )
    assert (
        record.status
        == RiskResponseDecisionStatus.PENDING.value
    )
    assert record.human_approval_required is True
    assert (
        record.response_event_key
        == build_response_event_key(response)
    )
    assert record.reason_codes == [
        "TREATMENT_MISSING_RESIDUAL"
    ]
    assert record.risk_state == "REASSESSMENT_REQUIRED"
    assert record.treatment_state == "REQUIRES_REASSESSMENT"
    assert record.requested_by_id == employee.id


def test_duplicate_open_response_event_returns_same_record(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    response = _response(risk_id=risk.id)

    first = create_response_decision(
        db,
        risk,
        employee,
        response=response,
    )

    second = create_response_decision(
        db,
        risk,
        employee,
        response=response,
    )

    assert first.id == second.id
    assert (
        db.query(RiskResponseDecisionRecord).count()
        == 1
    )


def test_approved_decision_requires_nonblank_reason(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]

    record = create_response_decision(
        db,
        risk,
        employee,
        response=_response(risk_id=risk.id),
    )

    with pytest.raises(ResponseDecisionValidationError):
        transition_response_decision(
            db,
            record,
            RiskResponseDecisionStatus.APPROVED,
            actor=employee,
            resolution_reason="   ",
            current_response=_response(
                risk_id=risk.id,
            ),
        )

    assert (
        record.status
        == RiskResponseDecisionStatus.PENDING.value
    )


def test_approved_decision_records_resolution(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.APPROVED,
        actor=manager,
        resolution_reason=(
            "Reviewed the current risk response "
            "and approved reassessment."
        ),
        current_response=response,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.APPROVED.value
    )
    assert record.resolution_reason.startswith(
        "Reviewed"
    )
    assert record.resolved_at is not None
    assert record.deferred_until is None


def test_rejected_decision_records_resolution(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.REJECTED,
        actor=manager,
        resolution_reason=(
            "Rejected after review because "
            "compensating evidence was supplied."
        ),
        current_response=response,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.REJECTED.value
    )
    assert record.resolved_at is not None


def test_deferred_decision_requires_future_time_and_reason(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    with pytest.raises(ResponseDecisionValidationError):
        transition_response_decision(
            db,
            record,
            RiskResponseDecisionStatus.DEFERRED,
            actor=manager,
            resolution_reason="Need more time.",
            current_response=response,
        )

    future = datetime.now(timezone.utc) + timedelta(days=2)

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.DEFERRED,
        actor=manager,
        resolution_reason=(
            "Deferred pending additional evidence review."
        ),
        deferred_until=future,
        current_response=response,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.DEFERRED.value
    )
    assert record.deferred_until == future
    assert record.resolved_at is None


def test_changed_response_marks_pending_decision_stale(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original = _response(
        risk_id=risk.id,
    )

    changed = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        risk_state="DEGRADED",
        treatment_state="DEGRADED",
        human_approval_required=True,
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    record = create_response_decision(
        db,
        risk,
        manager,
        response=original,
    )

    refresh_response_decision_state(
        db,
        record,
        current_response=changed,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.STALE.value
    )
    assert record.resolved_at is not None
    assert (
        "changed"
        in record.resolution_reason.lower()
    )


def test_stale_response_cannot_be_approved(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original = _response(
        risk_id=risk.id,
    )

    changed = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        risk_state="DEGRADED",
        treatment_state="DEGRADED",
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    record = create_response_decision(
        db,
        risk,
        manager,
        response=original,
    )

    with pytest.raises(StaleResponseDecision):
        transition_response_decision(
            db,
            record,
            RiskResponseDecisionStatus.APPROVED,
            actor=manager,
            resolution_reason="Approve the old response.",
            current_response=changed,
        )

    assert (
        record.status
        == RiskResponseDecisionStatus.STALE.value
    )


def test_terminal_decision_cannot_be_changed_again(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.REJECTED,
        actor=manager,
        resolution_reason=(
            "Rejected after governance review."
        ),
        current_response=response,
    )

    with pytest.raises(
        InvalidResponseDecisionTransition
    ):
        transition_response_decision(
            db,
            record,
            RiskResponseDecisionStatus.APPROVED,
            actor=manager,
            resolution_reason=(
                "Attempted second resolution."
            ),
            current_response=response,
        )


def test_non_response_risk_cannot_create_decision(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]

    response = ContinuousRiskResponse(
        risk_id=risk.id,
        risk_state="CURRENT",
        treatment_state="CURRENT",
        reassessment_required=False,
        response_required=False,
        priority=RiskResponsePriority.LOW,
        decisions=(
            RiskResponseAction(
                decision=RiskResponseDecision.MONITOR,
                priority=RiskResponsePriority.LOW,
                reason_codes=(),
                human_approval_required=False,
            ),
        ),
        human_approval_required=False,
        reasons=(),
    )

    with pytest.raises(ResponseDecisionValidationError):
        create_response_decision(
            db,
            risk,
            employee,
            response=response,
        )

def test_approved_decision_is_terminal_and_execution_ready(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.APPROVED,
        actor=manager,
        resolution_reason=(
            "Reviewed the response and approved governed execution."
        ),
        current_response=response,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.APPROVED.value
    )
    assert record.resolution_reason
    assert record.resolved_at is not None

    with pytest.raises(
        InvalidResponseDecisionTransition
    ):
        transition_response_decision(
            db,
            record,
            RiskResponseDecisionStatus.REJECTED,
            actor=manager,
            resolution_reason=(
                "Attempted to change an approved decision."
            ),
            current_response=response,
        )


def test_rejected_decision_is_terminal_and_not_execution_ready(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.REJECTED,
        actor=manager,
        resolution_reason=(
            "Rejected during governance review."
        ),
        current_response=response,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.REJECTED.value
    )
    assert record.resolved_at is not None

    with pytest.raises(
        InvalidResponseDecisionTransition
    ):
        transition_response_decision(
            db,
            record,
            RiskResponseDecisionStatus.APPROVED,
            actor=manager,
            resolution_reason=(
                "Attempted to approve a rejected decision."
            ),
            current_response=response,
        )


def test_deferred_decision_can_be_reconsidered_for_approval(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    future = datetime.now(timezone.utc) + timedelta(days=2)

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.DEFERRED,
        actor=manager,
        resolution_reason=(
            "Deferred pending additional evidence review."
        ),
        deferred_until=future,
        current_response=response,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.DEFERRED.value
    )
    assert record.resolved_at is None
    assert record.deferred_until == future

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.APPROVED,
        actor=manager,
        resolution_reason=(
            "Additional evidence was reviewed and "
            "the response is now approved."
        ),
        current_response=response,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.APPROVED.value
    )
    assert record.resolution_reason.startswith(
        "Additional evidence"
    )
    assert record.resolved_at is not None
    assert record.deferred_until is None


def test_stale_decision_cannot_be_reactivated_after_refresh(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original = _response(
        risk_id=risk.id,
    )

    changed = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        risk_state="DEGRADED",
        treatment_state="DEGRADED",
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    record = create_response_decision(
        db,
        risk,
        manager,
        response=original,
    )

    refresh_response_decision_state(
        db,
        record,
        current_response=changed,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.STALE.value
    )

    with pytest.raises(
        InvalidResponseDecisionTransition
    ):
        transition_response_decision(
            db,
            record,
            RiskResponseDecisionStatus.APPROVED,
            actor=manager,
            resolution_reason=(
                "Attempted to reactivate stale governance."
            ),
            current_response=changed,
        )

    assert (
        record.status
        == RiskResponseDecisionStatus.STALE.value
    )


def test_approved_decision_preserves_response_event_identity(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    original_event_key = record.response_event_key

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.APPROVED,
        actor=manager,
        resolution_reason=(
            "Approved after governance review."
        ),
        current_response=response,
    )

    assert record.response_event_key == original_event_key
    assert (
        record.response_event_key
        == build_response_event_key(response)
    )

def test_deferred_decision_preserves_governance_snapshot(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    response = _response(risk_id=risk.id)

    record = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    original_event_key = record.response_event_key
    original_decision = record.decision
    original_priority = record.priority
    original_governance_level = record.governance_level

    future = datetime.now(timezone.utc) + timedelta(days=2)

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.DEFERRED,
        actor=manager,
        resolution_reason="Deferred for additional review.",
        deferred_until=future,
        current_response=response,
    )

    assert record.decision == original_decision
    assert record.priority == original_priority
    assert record.governance_level == original_governance_level
    assert record.response_event_key == original_event_key
    assert record.deferred_until == future


def test_deferred_decision_becomes_stale_when_response_changes(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original = _response(
        risk_id=risk.id,
    )

    changed = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        risk_state="DEGRADED",
        treatment_state="DEGRADED",
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    record = create_response_decision(
        db,
        risk,
        manager,
        response=original,
    )

    future = datetime.now(timezone.utc) + timedelta(days=2)

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.DEFERRED,
        actor=manager,
        resolution_reason="Deferred for additional review.",
        deferred_until=future,
        current_response=original,
    )

    refresh_response_decision_state(
        db,
        record,
        current_response=changed,
    )

    assert (
        record.status
        == RiskResponseDecisionStatus.STALE.value
    )
    assert record.resolved_at is not None


def test_stale_deferred_decision_cannot_be_approved(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original = _response(
        risk_id=risk.id,
    )

    changed = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        risk_state="DEGRADED",
        treatment_state="DEGRADED",
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    record = create_response_decision(
        db,
        risk,
        manager,
        response=original,
    )

    future = datetime.now(timezone.utc) + timedelta(days=2)

    transition_response_decision(
        db,
        record,
        RiskResponseDecisionStatus.DEFERRED,
        actor=manager,
        resolution_reason="Deferred for review.",
        deferred_until=future,
        current_response=original,
    )

    with pytest.raises(StaleResponseDecision):
        transition_response_decision(
            db,
            record,
            RiskResponseDecisionStatus.APPROVED,
            actor=manager,
            resolution_reason="Approve old response.",
            current_response=changed,
        )

    assert (
        record.status
        == RiskResponseDecisionStatus.STALE.value
    )