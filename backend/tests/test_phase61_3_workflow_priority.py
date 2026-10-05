from datetime import datetime, timezone

import pytest

from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)
from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)
from app.services.continuous_risk_response_service import (
    RiskResponsePriority,
)
from app.services.risk_response_workflow_intelligence_service import (
    WorkflowPriorityReason,
    derive_workflow_priority,
    get_workflow_intelligence,
    normalize_workflow_priority,
)


def _decision(
    *,
    priority="HIGH",
    governance_level="HUMAN_APPROVAL_REQUIRED",
):
    return RiskResponseDecisionRecord(
        id=200,
        risk_id=10,
        decision="REASSESS_RISK",
        priority=priority,
        governance_level=governance_level,
        status="APPROVED",
        human_approval_required=True,
        response_event_key="risk:10:REASSESS_RISK",
        reason_codes=[],
        risk_state="CURRENT",
        treatment_state="CURRENT",
        reassessment_required=True,
        response_required=True,
        requested_by_id=1,
        resolution_reason="Approved for governed response.",
    )


def _workflow(
    *,
    priority="HIGH",
    governance_level="HUMAN_APPROVAL_REQUIRED",
):
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    workflow = RiskResponseWorkflowRecord(
        id=1,
        execution_id=100,
        decision_id=200,
        risk_id=10,
        workflow_type="REASSESS_RISK",
        status="OPEN",
        target_type="RISK",
        target_id=10,
        title="Risk reassessment required",
        description="Test workflow.",
        created_by_id=1,
        created_at=created_at,
        updated_at=created_at,
    )

    workflow.decision = _decision(
        priority=priority,
        governance_level=governance_level,
    )

    return workflow


def test_low_priority_is_normalized():
    workflow = _workflow(
        priority="LOW",
        governance_level="INFORMATIONAL",
    )

    priority = normalize_workflow_priority(
        workflow,
    )

    assert priority == RiskResponsePriority.LOW


def test_medium_priority_is_normalized():
    workflow = _workflow(
        priority="MEDIUM",
    )

    priority = normalize_workflow_priority(
        workflow,
    )

    assert priority == RiskResponsePriority.MEDIUM


def test_high_priority_is_normalized():
    workflow = _workflow(
        priority="HIGH",
    )

    priority = normalize_workflow_priority(
        workflow,
    )

    assert priority == RiskResponsePriority.HIGH


def test_critical_priority_is_normalized():
    workflow = _workflow(
        priority="CRITICAL",
    )

    priority = normalize_workflow_priority(
        workflow,
    )

    assert priority == RiskResponsePriority.CRITICAL


def test_enum_priority_is_supported():
    workflow = _workflow(
        priority=RiskResponsePriority.HIGH,
    )

    priority = normalize_workflow_priority(
        workflow,
    )

    assert priority == RiskResponsePriority.HIGH


@pytest.mark.parametrize(
    ("priority", "expected_rank", "requires_attention"),
    [
        ("LOW", 1, False),
        ("MEDIUM", 2, False),
        ("HIGH", 3, True),
        ("CRITICAL", 4, True),
    ],
)
def test_priority_rank_and_attention(
    priority,
    expected_rank,
    requires_attention,
):
    workflow = _workflow(
        priority=priority,
    )

    (
        normalized,
        rank,
        governance_level,
        attention,
        reasons,
    ) = derive_workflow_priority(
        workflow,
    )

    assert normalized.value == priority
    assert rank == expected_rank
    assert governance_level == (
        "HUMAN_APPROVAL_REQUIRED"
    )
    assert attention is requires_attention

    assert (
        WorkflowPriorityReason.DECISION_PRIORITY.value
        in reasons
    )

    if requires_attention:
        assert (
            WorkflowPriorityReason.PRIORITY_REQUIRES_ATTENTION.value
            in reasons
        )


def test_governance_level_is_preserved():
    workflow = _workflow(
        priority="CRITICAL",
        governance_level="ESCALATION",
    )

    (
        priority,
        rank,
        governance_level,
        attention,
        reasons,
    ) = derive_workflow_priority(
        workflow,
    )

    assert priority == RiskResponsePriority.CRITICAL
    assert rank == 4
    assert governance_level == "ESCALATION"
    assert attention is True


def test_missing_decision_is_rejected():
    workflow = _workflow()

    workflow.decision = None

    with pytest.raises(
        ValueError,
        match="associated response decision",
    ):
        normalize_workflow_priority(
            workflow,
        )


def test_missing_priority_is_rejected():
    workflow = _workflow(
        priority="HIGH",
    )

    workflow.decision.priority = None

    with pytest.raises(
        ValueError,
        match="priority cannot be null",
    ):
        normalize_workflow_priority(
            workflow,
        )


def test_invalid_priority_is_rejected():
    workflow = _workflow(
        priority="URGENT",
    )

    with pytest.raises(
        ValueError,
        match="Unsupported workflow decision priority",
    ):
        normalize_workflow_priority(
            workflow,
        )


def test_priority_intelligence_does_not_mutate_decision():
    workflow = _workflow(
        priority="HIGH",
        governance_level="HUMAN_APPROVAL_REQUIRED",
    )

    original_priority = workflow.decision.priority
    original_governance = workflow.decision.governance_level

    derive_workflow_priority(
        workflow,
    )

    assert workflow.decision.priority == original_priority
    assert (
        workflow.decision.governance_level
        == original_governance
    )


def test_complete_intelligence_contains_priority_data():
    workflow = _workflow(
        priority="CRITICAL",
        governance_level="ESCALATION",
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=datetime(
            2026,
            1,
            3,
            tzinfo=timezone.utc,
        ),
    )

    assert (
        intelligence.decision_priority
        == RiskResponsePriority.CRITICAL
    )

    assert intelligence.priority_rank == 4
    assert intelligence.governance_level == "ESCALATION"
    assert intelligence.priority_requires_attention is True

    assert (
        WorkflowPriorityReason.DECISION_PRIORITY.value
        in intelligence.priority_reason_codes
    )

    assert (
        WorkflowPriorityReason.PRIORITY_REQUIRES_ATTENTION.value
        in intelligence.priority_reason_codes
    )


def test_priority_does_not_depend_on_workflow_age():
    workflow = _workflow(
        priority="MEDIUM",
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=datetime(
            2026,
            3,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert (
        intelligence.decision_priority
        == RiskResponsePriority.MEDIUM
    )

    assert intelligence.priority_rank == 2
    assert intelligence.priority_requires_attention is False


def test_priority_is_derived_from_governed_decision():
    workflow = _workflow(
        priority="HIGH",
    )

    first = get_workflow_intelligence(
        workflow,
        now=datetime(
            2026,
            1,
            2,
            tzinfo=timezone.utc,
        ),
    )

    workflow.decision.priority = "CRITICAL"

    second = get_workflow_intelligence(
        workflow,
        now=datetime(
            2026,
            1,
            2,
            tzinfo=timezone.utc,
        ),
    )

    assert (
        first.decision_priority
        == RiskResponsePriority.HIGH
    )

    assert (
        second.decision_priority
        == RiskResponsePriority.CRITICAL
    )