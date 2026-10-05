from datetime import datetime, timedelta, timezone

from app.models.risk_response_decision import RiskResponseDecisionRecord
from app.models.risk_response_workflow import RiskResponseWorkflowRecord
from app.services.continuous_risk_response_service import RiskResponsePriority
from app.services.risk_response_workflow_intelligence_service import (
    WORKFLOW_AGING_DAYS,
    WORKFLOW_OVERDUE_DAYS,
    WorkflowEscalationReason,
    WorkflowEscalationRecommendation,
    derive_workflow_escalation,
    get_workflow_intelligence,
)


NOW = datetime(
    2026,
    1,
    31,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def _decision(
    *,
    priority=RiskResponsePriority.MEDIUM,
):
    return RiskResponseDecisionRecord(
        id=1,
        risk_id=10,
        decision="REVIEW",
        priority=priority,
        governance_level="GOVERNED_ACTION",
        status="APPROVED",
        human_approval_required=True,
        response_event_key="test-event",
        reason_codes=[],
        risk_state="CURRENT",
        treatment_state="CURRENT",
        reassessment_required=False,
        response_required=True,
        requested_by_id=1,
        assigned_to_id=2,
        resolution_reason="Approved for testing",
    )


def _workflow(
    *,
    workflow_id=1,
    risk_id=10,
    status="OPEN",
    priority=RiskResponsePriority.MEDIUM,
    created_days_ago=1,
    started_days_ago=None,
    completed_days_ago=None,
    cancelled_days_ago=None,
):
    created_at = NOW - timedelta(days=created_days_ago)

    started_at = (
        NOW - timedelta(days=started_days_ago)
        if started_days_ago is not None
        else None
    )

    completed_at = (
        NOW - timedelta(days=completed_days_ago)
        if completed_days_ago is not None
        else None
    )

    cancelled_at = (
        NOW - timedelta(days=cancelled_days_ago)
        if cancelled_days_ago is not None
        else None
    )

    workflow = RiskResponseWorkflowRecord(
        id=workflow_id,
        execution_id=workflow_id,
        decision_id=workflow_id,
        risk_id=risk_id,
        workflow_type="REVIEW",
        status=status,
        target_type="RISK",
        target_id=risk_id,
        title="Test workflow",
        description="Test workflow description",
        created_by_id=1,
        updated_by_id=None,
        resolution_reason=None,
        started_at=started_at,
        completed_at=completed_at,
        cancelled_at=cancelled_at,
        created_at=created_at,
        updated_at=created_at,
    )

    workflow.decision = _decision(priority=priority)

    return workflow


def test_current_medium_workflow_has_no_escalation():
    workflow = _workflow(
        status="OPEN",
        priority=RiskResponsePriority.MEDIUM,
        created_days_ago=1,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.escalation_recommendation == (
        WorkflowEscalationRecommendation.NONE
    )
    assert intelligence.escalation_reason_codes == (
        WorkflowEscalationReason.NO_ESCALATION.value,
    )
    assert intelligence.escalation_requires_human_review is False


def test_critical_priority_recommends_escalation():
    workflow = _workflow(
        status="OPEN",
        priority=RiskResponsePriority.CRITICAL,
        created_days_ago=1,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.escalation_recommendation == (
        WorkflowEscalationRecommendation.ESCALATE
    )
    assert intelligence.escalation_reason_codes == (
        WorkflowEscalationReason.CRITICAL_PRIORITY.value,
    )
    assert intelligence.escalation_requires_human_review is True


def test_high_priority_bottleneck_recommends_escalation():
    workflow = _workflow(
        status="IN_PROGRESS",
        priority=RiskResponsePriority.HIGH,
        created_days_ago=WORKFLOW_AGING_DAYS,
        started_days_ago=WORKFLOW_AGING_DAYS - 1,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.bottlenecked is True
    assert intelligence.escalation_recommendation == (
        WorkflowEscalationRecommendation.ESCALATE
    )
    assert intelligence.escalation_reason_codes == (
        WorkflowEscalationReason.HIGH_PRIORITY_BOTTLENECK.value,
    )
    assert intelligence.escalation_requires_human_review is True


def test_overdue_workflow_recommends_escalation():
    workflow = _workflow(
        status="OPEN",
        priority=RiskResponsePriority.MEDIUM,
        created_days_ago=WORKFLOW_OVERDUE_DAYS,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.health.value == "OVERDUE"
    assert intelligence.escalation_recommendation == (
        WorkflowEscalationRecommendation.ESCALATE
    )
    assert intelligence.escalation_reason_codes == (
        WorkflowEscalationReason.OVERDUE_WORKFLOW.value,
    )
    assert intelligence.escalation_requires_human_review is True


def test_aging_high_priority_workflow_recommends_review():
    workflow = _workflow(
        status="OPEN",
        priority=RiskResponsePriority.HIGH,
        created_days_ago=WORKFLOW_AGING_DAYS,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.health.value == "AGING"
    assert intelligence.escalation_recommendation == (
        WorkflowEscalationRecommendation.REVIEW
    )
    assert intelligence.escalation_reason_codes == (
        WorkflowEscalationReason.AGING_WORKFLOW_REQUIRES_ATTENTION.value,
    )
    assert intelligence.escalation_requires_human_review is True


def test_completed_workflow_never_recommends_escalation():
    workflow = _workflow(
        status="COMPLETED",
        priority=RiskResponsePriority.CRITICAL,
        created_days_ago=WORKFLOW_OVERDUE_DAYS + 10,
        completed_days_ago=1,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.escalation_recommendation == (
        WorkflowEscalationRecommendation.NONE
    )
    assert intelligence.escalation_reason_codes == (
        WorkflowEscalationReason.NO_ESCALATION.value,
    )
    assert intelligence.escalation_requires_human_review is False


def test_cancelled_workflow_never_recommends_escalation():
    workflow = _workflow(
        status="CANCELLED",
        priority=RiskResponsePriority.CRITICAL,
        created_days_ago=WORKFLOW_OVERDUE_DAYS + 10,
        cancelled_days_ago=1,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.escalation_recommendation == (
        WorkflowEscalationRecommendation.NONE
    )
    assert intelligence.escalation_reason_codes == (
        WorkflowEscalationReason.NO_ESCALATION.value,
    )
    assert intelligence.escalation_requires_human_review is False


def test_escalation_function_is_deterministic():
    workflow = _workflow(
        status="IN_PROGRESS",
        priority=RiskResponsePriority.HIGH,
        created_days_ago=WORKFLOW_AGING_DAYS,
        started_days_ago=WORKFLOW_AGING_DAYS - 1,
    )

    first = derive_workflow_escalation(
        workflow,
        health=workflow.status,
        attention_required=True,
        decision_priority=RiskResponsePriority.HIGH,
        priority_requires_attention=True,
        bottlenecked=True,
    )

    second = derive_workflow_escalation(
        workflow,
        health=workflow.status,
        attention_required=True,
        decision_priority=RiskResponsePriority.HIGH,
        priority_requires_attention=True,
        bottlenecked=True,
    )

    assert first == second


def test_escalation_intelligence_does_not_mutate_workflow():
    workflow = _workflow(
        status="IN_PROGRESS",
        priority=RiskResponsePriority.HIGH,
        created_days_ago=WORKFLOW_AGING_DAYS,
        started_days_ago=WORKFLOW_AGING_DAYS - 1,
    )

    before = (
        workflow.status,
        workflow.resolution_reason,
        workflow.started_at,
        workflow.completed_at,
        workflow.cancelled_at,
    )

    get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    after = (
        workflow.status,
        workflow.resolution_reason,
        workflow.started_at,
        workflow.completed_at,
        workflow.cancelled_at,
    )

    assert after == before


def test_escalation_requires_human_review_for_escalate():
    workflow = _workflow(
        status="OPEN",
        priority=RiskResponsePriority.CRITICAL,
        created_days_ago=1,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.escalation_recommendation == (
        WorkflowEscalationRecommendation.ESCALATE
    )
    assert intelligence.escalation_requires_human_review is True