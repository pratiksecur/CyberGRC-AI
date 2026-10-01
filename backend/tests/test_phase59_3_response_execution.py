from datetime import datetime, timezone

import pytest

from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)

from app.models.risk_response_execution import (
    RiskResponseExecutionRecord,
)

from app.services.continuous_risk_response_notification_service import (
    build_response_event_key,
)
from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
    RiskResponsePriority,
)

from app.services.risk_response_decision_service import (
    RiskResponseDecisionStatus,
    create_response_decision,
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


def _response(
    *,
    risk_id: int,
    decision: RiskResponseDecision = RiskResponseDecision.REASSESS_RISK,
    priority: RiskResponsePriority = RiskResponsePriority.HIGH,
    risk_state: str = "REASSESSMENT_REQUIRED",
    treatment_state: str = "REQUIRES_REASSESSMENT",
    reason_codes=("TREATMENT_MISSING_RESIDUAL",),
):
    action = RiskResponseAction(
        decision=decision,
        priority=priority,
        reason_codes=reason_codes,
        human_approval_required=True,
    )

    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state=risk_state,
        treatment_state=treatment_state,
        reassessment_required=True,
        response_required=True,
        priority=priority,
        decisions=(action,),
        human_approval_required=True,
        reasons=(),
    )


def _approved_decision(
    db,
    *,
    risk,
    manager,
    response,
):
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

    return record


def test_approved_response_executes_once(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.id is not None
    assert execution.decision_id == decision.id
    assert execution.risk_id == risk.id
    assert execution.decision == "REASSESS_RISK"
    assert execution.execution_action == "REASSESS_RISK"
    assert execution.status == "EXECUTED"
    assert execution.human_approval_verified is True
    assert execution.response_event_verified is True
    assert execution.executed_by_id == manager.id
    assert execution.executed_at is not None

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 1
    )


def test_pending_decision_cannot_execute(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    with pytest.raises(ResponseExecutionNotApproved):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )


def test_rejected_decision_cannot_execute(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    transition_response_decision(
        db,
        decision,
        RiskResponseDecisionStatus.REJECTED,
        actor=manager,
        resolution_reason="Rejected after governance review.",
        current_response=response,
    )

    with pytest.raises(ResponseExecutionNotApproved):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )


def test_deferred_decision_cannot_execute(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    transition_response_decision(
        db,
        decision,
        RiskResponseDecisionStatus.DEFERRED,
        actor=manager,
        resolution_reason="Deferred for additional evidence.",
        deferred_until=datetime(
            2099,
            1,
            1,
            tzinfo=timezone.utc,
        ),
        current_response=response,
    )

    with pytest.raises(ResponseExecutionNotApproved):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )


def test_stale_approved_decision_cannot_execute(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original_response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=original_response,
    )

    changed_response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        risk_state="REASSESSMENT_REQUIRED",
        treatment_state="REQUIRES_REASSESSMENT",
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    assert (
        build_response_event_key(changed_response)
        != decision.response_event_key
    )

    with pytest.raises(StaleResponseExecution):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=changed_response,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )


def test_changed_decision_is_not_current_even_when_decision_name_matches(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original_response = _response(
        risk_id=risk.id,
        reason_codes=("TREATMENT_MISSING_RESIDUAL",),
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=original_response,
    )

    changed_response = _response(
        risk_id=risk.id,
        reason_codes=("ELEVATED_RESIDUAL_RISK",),
    )

    assert (
        build_response_event_key(changed_response)
        != decision.response_event_key
    )

    with pytest.raises(StaleResponseExecution):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=changed_response,
        )


def test_same_approved_decision_cannot_execute_twice(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    first = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert first.id is not None

    with pytest.raises(ResponseAlreadyExecuted):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 1
    )


def test_execution_does_not_modify_risk(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original_score = risk.risk_score
    original_status = risk.status

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    db.refresh(risk)

    assert risk.risk_score == original_score
    assert risk.status == original_status


def test_execution_event_key_matches_approved_event(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert (
        execution.response_event_key
        == decision.response_event_key
    )

    assert (
        execution.response_event_key
        == build_response_event_key(response)
    )


def test_execution_records_approval_and_event_verification(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.human_approval_verified is True
    assert execution.response_event_verified is True

def test_execution_rejects_missing_human_approval_flag(
    db,
    resource_data,
    users,
):
    risk = resource_data["risks"]["manager"]

    decision = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision="REVIEW",
        priority="MEDIUM",
        governance_level="GOVERNED_ACTION",
        status="APPROVED",
        human_approval_required=False,
        response_event_key="valid-event-key",
        reason_codes=["TEST"],
        risk_state="DEGRADED",
        treatment_state="CURRENT",
        reassessment_required=False,
        response_required=True,
        requested_by_id=users["manager"].id,
        resolution_reason="Approved for testing.",
    )

    db.add(decision)
    db.flush()

    with pytest.raises(ResponseExecutionValidationError):
        execute_approved_response(
            db,
            decision,
            actor=users["manager"],
        )


def test_execution_rejects_missing_approval_reason(
    db,
    resource_data,
    users,
):
    risk = resource_data["risks"]["manager"]

    decision = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision="REVIEW",
        priority="MEDIUM",
        governance_level="GOVERNED_ACTION",
        status="APPROVED",
        human_approval_required=True,
        response_event_key="valid-event-key",
        reason_codes=["TEST"],
        risk_state="DEGRADED",
        treatment_state="CURRENT",
        reassessment_required=False,
        response_required=True,
        requested_by_id=users["manager"].id,
        resolution_reason=None,
    )

    db.add(decision)
    db.flush()

    with pytest.raises(ResponseExecutionValidationError):
        execute_approved_response(
            db,
            decision,
            actor=users["manager"],
        )


def test_execution_rejects_missing_response_event_key(
    db,
    resource_data,
    users,
):
    risk = resource_data["risks"]["manager"]

    decision = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision="REVIEW",
        priority="MEDIUM",
        governance_level="GOVERNED_ACTION",
        status="APPROVED",
        human_approval_required=True,
        response_event_key="",
        reason_codes=["TEST"],
        risk_state="DEGRADED",
        treatment_state="CURRENT",
        reassessment_required=False,
        response_required=True,
        requested_by_id=users["manager"].id,
        resolution_reason="Approved for testing.",
    )

    db.add(decision)
    db.flush()

    with pytest.raises(ResponseExecutionValidationError):
        execute_approved_response(
            db,
            decision,
            actor=users["manager"],
        )


def test_execution_rejects_missing_governance_level(
    db,
    resource_data,
    users,
):
    risk = resource_data["risks"]["manager"]

    decision = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision="REVIEW",
        priority="MEDIUM",
        governance_level="",
        status="APPROVED",
        human_approval_required=True,
        response_event_key="valid-event-key",
        reason_codes=["TEST"],
        risk_state="DEGRADED",
        treatment_state="CURRENT",
        reassessment_required=False,
        response_required=True,
        requested_by_id=users["manager"].id,
        resolution_reason="Approved for testing.",
    )

    db.add(decision)
    db.flush()

    with pytest.raises(ResponseExecutionValidationError):
        execute_approved_response(
            db,
            decision,
            actor=users["manager"],
        )


def test_execution_preserves_approved_reason_in_execution_record(
    db,
    resource_data,
    users,
):
    risk = resource_data["risks"]["manager"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    reason = decision.resolution_reason

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.execution_reason == reason.strip()
    assert execution.human_approval_verified is True
    assert execution.response_event_verified is True

def test_execution_preserves_governance_snapshot(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    original_decision = decision.decision
    original_risk_id = decision.risk_id
    original_event_key = decision.response_event_key
    original_priority = decision.priority
    original_governance_level = decision.governance_level
    original_approval = decision.human_approval_required
    original_reason = decision.resolution_reason

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.decision_id == decision.id
    assert execution.risk_id == original_risk_id
    assert execution.decision == original_decision
    assert execution.execution_action == original_decision
    assert execution.response_event_key == original_event_key
    assert execution.human_approval_verified is original_approval
    assert execution.execution_reason == original_reason.strip()

    # Governance metadata is preserved by the decision record itself.
    assert decision.priority == original_priority
    assert decision.governance_level == original_governance_level


def test_execution_records_authorized_actor(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.executed_by_id == manager.id

    persisted = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.id == execution.id
        )
        .one()
    )

    assert persisted.executed_by_id == manager.id


def test_execution_has_valid_terminal_status(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.status == "EXECUTED"
    assert execution.status is not None
    assert execution.result_message
    assert execution.execution_reason


def test_execution_timestamps_are_recorded(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.created_at is not None
    assert execution.executed_at is not None


def test_execution_does_not_modify_approved_decision(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    original_status = decision.status
    original_reason = decision.resolution_reason
    original_event_key = decision.response_event_key
    original_resolved_at = decision.resolved_at

    execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    db.refresh(decision)

    assert decision.status == original_status
    assert decision.status == RiskResponseDecisionStatus.APPROVED.value
    assert decision.resolution_reason == original_reason
    assert decision.response_event_key == original_event_key
    if original_resolved_at is None:
        assert decision.resolved_at is None
    else:
        assert decision.resolved_at is not None
        assert decision.resolved_at.replace(tzinfo=None) == (
            original_resolved_at.replace(tzinfo=None)
        )


def test_execution_result_message_confirms_no_domain_mutation(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert "Governed response execution recorded successfully." in (
        execution.result_message
    )
    assert "No underlying risk-domain record was mutated." in (
        execution.result_message
    )

def test_existing_execution_blocks_reexecution_even_after_refresh(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    first = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert first.id is not None

    db.expire_all()

    refreshed_decision = (
        db.query(RiskResponseDecisionRecord)
        .filter(
            RiskResponseDecisionRecord.id == decision.id
        )
        .one()
    )

    with pytest.raises(ResponseAlreadyExecuted):
        execute_approved_response(
            db,
            refreshed_decision,
            actor=manager,
            current_response=response,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 1
    )


def test_execution_record_preserves_original_approved_event_after_refresh(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    approved_event_key = decision.response_event_key
    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    db.expire_all()

    persisted_execution = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.id == execution.id
        )
        .one()
    )

    assert persisted_execution.response_event_key == approved_event_key
    assert (
        persisted_execution.response_event_key
        == build_response_event_key(response)
    )
    assert persisted_execution.status == "EXECUTED"


def test_execution_record_cannot_be_reused_as_new_decision(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.decision_id == decision.id

    execution_status = execution.status
    execution_event_key = execution.response_event_key

    db.expire_all()

    persisted_execution = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.id == execution.id
        )
        .one()
    )

    assert persisted_execution.status == execution_status
    assert persisted_execution.response_event_key == execution_event_key

    with pytest.raises(ResponseAlreadyExecuted):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )


def test_execution_remains_bound_to_original_risk(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    other_risk = resource_data["risks"]["manager"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.risk_id == risk.id
    assert execution.risk_id != other_risk.id
    assert execution.decision_id == decision.id


def test_execution_record_is_unique_per_approved_decision(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    first = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert first.decision_id == decision.id

    with pytest.raises(ResponseAlreadyExecuted):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    executions = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .all()
    )

    assert len(executions) == 1
    assert executions[0].id == first.id

def test_execution_requires_actor(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    with pytest.raises(ResponseExecutionValidationError):
        execute_approved_response(
            db,
            decision,
            actor=None,
            current_response=response,
        )


def test_execution_requires_persisted_actor_identity(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    manager.id = None

    with pytest.raises(ResponseExecutionValidationError):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )


def test_execution_rejects_non_approved_decision_before_execution(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    assert decision.status == RiskResponseDecisionStatus.PENDING.value

    with pytest.raises(ResponseExecutionNotApproved):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )


def test_execution_rejects_rejected_decision_without_creating_execution(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    transition_response_decision(
        db,
        decision,
        RiskResponseDecisionStatus.REJECTED,
        actor=manager,
        resolution_reason="Rejected during governance review.",
        current_response=response,
    )

    with pytest.raises(ResponseExecutionNotApproved):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    assert decision.status == RiskResponseDecisionStatus.REJECTED.value

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )


def test_execution_does_not_bypass_approval_with_supported_decision(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    decision = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    assert decision.decision == RiskResponseDecision.ESCALATE.value
    assert decision.human_approval_required is True
    assert decision.status == RiskResponseDecisionStatus.PENDING.value

    with pytest.raises(ResponseExecutionNotApproved):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )

def test_stale_execution_attempt_leaves_no_execution_record(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original_response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=original_response,
    )

    changed_response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    with pytest.raises(StaleResponseExecution):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=changed_response,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )


def test_invalid_governance_attempt_leaves_no_execution_record(
    db,
    resource_data,
    users,
):
    risk = resource_data["risks"]["manager"]
    manager = users["manager"]

    decision = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision="REASSESS_RISK",
        priority="HIGH",
        governance_level="HUMAN_APPROVAL_REQUIRED",
        status="APPROVED",
        human_approval_required=False,
        response_event_key="invalid-governance-event",
        reason_codes=["TEST"],
        risk_state="REASSESSMENT_REQUIRED",
        treatment_state="REQUIRES_REASSESSMENT",
        reassessment_required=True,
        response_required=True,
        requested_by_id=manager.id,
        resolution_reason="Invalid governance test.",
    )

    db.add(decision)
    db.flush()

    with pytest.raises(ResponseExecutionValidationError):
        execute_approved_response(
            db,
            decision,
            actor=manager,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )


def test_duplicate_execution_attempt_leaves_execution_count_unchanged(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    first = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert first.id is not None

    before_count = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
    )

    with pytest.raises(ResponseAlreadyExecuted):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    after_count = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
    )

    assert before_count == 1
    assert after_count == before_count


def test_unsupported_decision_leaves_no_execution_record(
    db,
    resource_data,
    users,
):
    risk = resource_data["risks"]["manager"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.MONITOR,
        priority=RiskResponsePriority.LOW,
        risk_state="CURRENT",
        treatment_state="CURRENT",
        reason_codes=(),
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    with pytest.raises(UnsupportedResponseExecution):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )


def test_pending_execution_attempt_does_not_create_partial_record(
    db,
    resource_data,
    users,
):
    risk = resource_data["risks"]["manager"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = create_response_decision(
        db,
        risk,
        manager,
        response=response,
    )

    with pytest.raises(ResponseExecutionNotApproved):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )

def test_approved_decision_cannot_execute_after_response_changes(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=original,
    )

    changed = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    with pytest.raises(StaleResponseExecution):
        execute_approved_response(
            db,
            decision,
            actor=manager,
            current_response=changed,
        )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )


def test_approved_execution_remains_valid_when_current_response_is_unchanged(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.status == "EXECUTED"
    assert execution.decision_id == decision.id
    assert execution.response_event_key == (
        build_response_event_key(response)
    )

def test_execution_snapshot_matches_approved_decision_after_reload(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    db.expire_all()

    persisted_decision = (
        db.query(RiskResponseDecisionRecord)
        .filter(
            RiskResponseDecisionRecord.id == decision.id
        )
        .one()
    )

    persisted_execution = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.id == execution.id
        )
        .one()
    )

    assert persisted_decision.status == "APPROVED"
    assert persisted_execution.status == "EXECUTED"

    assert (
        persisted_execution.decision_id
        == persisted_decision.id
    )
    assert (
        persisted_execution.risk_id
        == persisted_decision.risk_id
    )
    assert (
        persisted_execution.decision
        == persisted_decision.decision
    )
    assert (
        persisted_execution.response_event_key
        == persisted_decision.response_event_key
    )
    assert (
        persisted_execution.execution_reason
        == persisted_decision.resolution_reason.strip()
    )


def test_execution_does_not_change_decision_event_identity(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    original_event_key = decision.response_event_key

    execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    db.refresh(decision)

    assert decision.response_event_key == original_event_key
    assert (
        decision.response_event_key
        == build_response_event_key(response)
    )