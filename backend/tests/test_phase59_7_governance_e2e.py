import pytest

from app.models.risk_response_execution import (
    RiskResponseExecutionRecord,
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
    execute_approved_response,
)


def _response(*, risk_id):
    action = RiskResponseAction(
        decision=RiskResponseDecision.REASSESS_RISK,
        priority=RiskResponsePriority.HIGH,
        reason_codes=("TREATMENT_MISSING_RESIDUAL",),
        human_approval_required=True,
    )

    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state="REASSESSMENT_REQUIRED",
        treatment_state="REQUIRES_REASSESSMENT",
        reassessment_required=True,
        response_required=True,
        priority=RiskResponsePriority.HIGH,
        decisions=(action,),
        human_approval_required=True,
        reasons=(),
    )


def test_full_governed_response_lifecycle(
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

    assert (
        decision.status
        == RiskResponseDecisionStatus.PENDING.value
    )

    transition_response_decision(
        db,
        decision,
        RiskResponseDecisionStatus.APPROVED,
        actor=manager,
        resolution_reason=(
            "Reviewed and approved governed reassessment."
        ),
        current_response=response,
    )

    assert (
        decision.status
        == RiskResponseDecisionStatus.APPROVED.value
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
    assert execution.status == "EXECUTED"
    assert execution.human_approval_verified is True
    assert execution.response_event_verified is True


def test_stale_governance_workflow_stops_before_execution(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original = _response(
        risk_id=risk.id,
    )

    changed_action = RiskResponseAction(
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        reason_codes=("OPEN_CRITICAL_FINDING",),
        human_approval_required=True,
    )

    changed = ContinuousRiskResponse(
        risk_id=risk.id,
        risk_state="DEGRADED",
        treatment_state="DEGRADED",
        reassessment_required=False,
        response_required=True,
        priority=RiskResponsePriority.CRITICAL,
        decisions=(changed_action,),
        human_approval_required=True,
        reasons=(),
    )

    decision = create_response_decision(
        db,
        risk,
        manager,
        response=original,
    )

    transition_response_decision(
        db,
        decision,
        RiskResponseDecisionStatus.APPROVED,
        actor=manager,
        resolution_reason="Approved original response.",
        current_response=original,
    )

    with pytest.raises(Exception):
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


def test_rejected_workflow_never_creates_execution(
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

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id
        )
        .count()
        == 0
    )