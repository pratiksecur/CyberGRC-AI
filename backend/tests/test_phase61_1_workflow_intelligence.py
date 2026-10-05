from datetime import datetime, timedelta, timezone

from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)

from app.services.risk_response_workflow_intelligence_service import (
    WorkflowHealth,
    WorkflowIntelligenceReason,
    WORKFLOW_AGING_DAYS,
    WORKFLOW_OVERDUE_DAYS,
    calculate_workflow_age,
    derive_workflow_health,
    get_workflow_intelligence,
)


def _workflow(
    *,
    workflow_id=1,
    risk_id=10,
    status="OPEN",
    created_at=None,
    started_at=None,
):
    created_at = created_at or datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    return RiskResponseWorkflowRecord(
        id=workflow_id,
        execution_id=100,
        decision_id=200,
        risk_id=risk_id,
        workflow_type="REASSESS_RISK",
        status=status,
        target_type="RISK",
        target_id=risk_id,
        title="Risk reassessment required",
        description="Test workflow.",
        created_by_id=1,
        created_at=created_at,
        updated_at=created_at,
        started_at=started_at,
    )


def test_current_open_workflow_is_healthy():
    now = datetime(
        2026,
        1,
        5,
        tzinfo=timezone.utc,
    )

    workflow = _workflow()

    health, reasons, attention = derive_workflow_health(
        workflow,
        now=now,
    )

    assert health == WorkflowHealth.HEALTHY
    assert reasons == (
        WorkflowIntelligenceReason.WORKFLOW_CURRENT.value,
    )
    assert attention is False


def test_workflow_reaches_aging_threshold():
    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    ) + timedelta(
        days=WORKFLOW_AGING_DAYS,
    )

    workflow = _workflow()

    health, reasons, attention = derive_workflow_health(
        workflow,
        now=now,
    )

    assert health == WorkflowHealth.AGING
    assert reasons == (
        WorkflowIntelligenceReason.WORKFLOW_AGING.value,
    )
    assert attention is True


def test_workflow_below_overdue_threshold_remains_aging():
    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    ) + timedelta(
        days=WORKFLOW_OVERDUE_DAYS - 1,
    )

    workflow = _workflow()

    health, reasons, attention = derive_workflow_health(
        workflow,
        now=now,
    )

    assert health == WorkflowHealth.AGING
    assert reasons == (
        WorkflowIntelligenceReason.WORKFLOW_AGING.value,
    )
    assert attention is True


def test_workflow_reaches_overdue_threshold():
    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    ) + timedelta(
        days=WORKFLOW_OVERDUE_DAYS,
    )

    workflow = _workflow()

    health, reasons, attention = derive_workflow_health(
        workflow,
        now=now,
    )

    assert health == WorkflowHealth.OVERDUE
    assert reasons == (
        WorkflowIntelligenceReason.WORKFLOW_OVERDUE.value,
    )
    assert attention is True


def test_in_progress_workflow_uses_started_at_for_age():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    started_at = datetime(
        2026,
        1,
        20,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        1,
        25,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="IN_PROGRESS",
        created_at=created_at,
        started_at=started_at,
    )

    age_days, age_seconds = calculate_workflow_age(
        workflow,
        now=now,
    )

    assert age_days == 5
    assert age_seconds == 5 * 86400


def test_completed_workflow_is_terminal_and_not_attention_required():
    now = datetime(
        2026,
        2,
        1,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="COMPLETED",
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=now,
    )

    assert intelligence.health == WorkflowHealth.COMPLETED
    assert intelligence.attention_required is False
    assert intelligence.terminal is True
    assert intelligence.started is False
    assert intelligence.reason_codes == (
        WorkflowIntelligenceReason.WORKFLOW_COMPLETED.value,
    )


def test_cancelled_workflow_is_terminal_and_not_attention_required():
    now = datetime(
        2026,
        2,
        1,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="CANCELLED",
        created_at=datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc,
        ),
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=now,
    )

    assert intelligence.health == WorkflowHealth.CANCELLED
    assert intelligence.attention_required is False
    assert intelligence.terminal is True
    assert intelligence.reason_codes == (
        WorkflowIntelligenceReason.WORKFLOW_CANCELLED.value,
    )


def test_workflow_intelligence_does_not_mutate_workflow():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="OPEN",
        created_at=created_at,
    )

    original_status = workflow.status
    original_started_at = workflow.started_at
    original_completed_at = workflow.completed_at
    original_cancelled_at = workflow.cancelled_at

    get_workflow_intelligence(
        workflow,
        now=datetime(
            2026,
            2,
            1,
            tzinfo=timezone.utc,
        ),
    )

    assert workflow.status == original_status
    assert workflow.started_at == original_started_at
    assert workflow.completed_at == original_completed_at
    assert workflow.cancelled_at == original_cancelled_at


def test_naive_database_timestamp_is_treated_as_utc():
    created_at = datetime(
        2026,
        1,
        1,
    )

    now = datetime(
        2026,
        1,
        8,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        created_at=created_at,
    )

    age_days, _ = calculate_workflow_age(
        workflow,
        now=now,
    )

    assert age_days == 7