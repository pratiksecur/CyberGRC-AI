from datetime import datetime, timedelta, timezone

from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)

from app.services.risk_response_workflow_intelligence_service import (
    WORKFLOW_AGING_DAYS,
    WORKFLOW_OVERDUE_DAYS,
    WorkflowHealth,
    calculate_workflow_age,
    calculate_workflow_lifecycle_timing,
    get_workflow_intelligence,
)


def _workflow(
    *,
    workflow_id=1,
    risk_id=10,
    status="OPEN",
    created_at=None,
    started_at=None,
    completed_at=None,
    cancelled_at=None,
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
        completed_at=completed_at,
        cancelled_at=cancelled_at,
    )


def test_open_workflow_age_is_creation_based():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        1,
        11,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        created_at=created_at,
    )

    age_days, age_seconds = calculate_workflow_age(
        workflow,
        now=now,
    )

    assert age_days == 10
    assert age_seconds == 10 * 86400


def test_in_progress_workflow_age_uses_started_at():
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


def test_completed_workflow_has_full_lifecycle_duration():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    started_at = datetime(
        2026,
        1,
        3,
        tzinfo=timezone.utc,
    )

    completed_at = datetime(
        2026,
        1,
        10,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        1,
        20,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="COMPLETED",
        created_at=created_at,
        started_at=started_at,
        completed_at=completed_at,
    )

    (
        time_to_start,
        time_in_progress,
        lifecycle_duration,
        terminal_age,
    ) = calculate_workflow_lifecycle_timing(
        workflow,
        now=now,
    )

    assert time_to_start == 2 * 86400
    assert time_in_progress == 7 * 86400
    assert lifecycle_duration == 9 * 86400
    assert terminal_age == 10 * 86400


def test_cancelled_workflow_has_full_lifecycle_duration():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    started_at = datetime(
        2026,
        1,
        5,
        tzinfo=timezone.utc,
    )

    cancelled_at = datetime(
        2026,
        1,
        12,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        1,
        20,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="CANCELLED",
        created_at=created_at,
        started_at=started_at,
        cancelled_at=cancelled_at,
    )

    (
        time_to_start,
        time_in_progress,
        lifecycle_duration,
        terminal_age,
    ) = calculate_workflow_lifecycle_timing(
        workflow,
        now=now,
    )

    assert time_to_start == 4 * 86400
    assert time_in_progress == 7 * 86400
    assert lifecycle_duration == 11 * 86400
    assert terminal_age == 8 * 86400


def test_open_workflow_has_no_start_or_progress_duration():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        1,
        5,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        created_at=created_at,
    )

    (
        time_to_start,
        time_in_progress,
        lifecycle_duration,
        terminal_age,
    ) = calculate_workflow_lifecycle_timing(
        workflow,
        now=now,
    )

    assert time_to_start is None
    assert time_in_progress is None
    assert lifecycle_duration == 4 * 86400
    assert terminal_age is None


def test_in_progress_workflow_has_live_progress_duration():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    started_at = datetime(
        2026,
        1,
        5,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        1,
        12,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="IN_PROGRESS",
        created_at=created_at,
        started_at=started_at,
    )

    (
        time_to_start,
        time_in_progress,
        lifecycle_duration,
        terminal_age,
    ) = calculate_workflow_lifecycle_timing(
        workflow,
        now=now,
    )

    assert time_to_start == 4 * 86400
    assert time_in_progress == 7 * 86400
    assert lifecycle_duration == 11 * 86400
    assert terminal_age is None


def test_ageing_threshold_is_exactly_respected():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = created_at + timedelta(
        days=WORKFLOW_AGING_DAYS,
    )

    workflow = _workflow(
        created_at=created_at,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=now,
    )

    assert intelligence.health == WorkflowHealth.AGING
    assert intelligence.age_days == WORKFLOW_AGING_DAYS
    assert intelligence.attention_required is True


def test_overdue_threshold_is_exactly_respected():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    now = created_at + timedelta(
        days=WORKFLOW_OVERDUE_DAYS,
    )

    workflow = _workflow(
        created_at=created_at,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=now,
    )

    assert intelligence.health == WorkflowHealth.OVERDUE
    assert intelligence.age_days == WORKFLOW_OVERDUE_DAYS
    assert intelligence.attention_required is True


def test_future_timestamp_never_produces_negative_age():
    created_at = datetime(
        2026,
        2,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        created_at=created_at,
    )

    age_days, age_seconds = calculate_workflow_age(
        workflow,
        now=now,
    )

    assert age_days == 0
    assert age_seconds == 0


def test_future_started_at_never_produces_negative_lifecycle_values():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    started_at = datetime(
        2026,
        2,
        1,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        1,
        15,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="IN_PROGRESS",
        created_at=created_at,
        started_at=started_at,
    )

    (
        time_to_start,
        time_in_progress,
        lifecycle_duration,
        terminal_age,
    ) = calculate_workflow_lifecycle_timing(
        workflow,
        now=now,
    )

    assert time_to_start == 31 * 86400
    assert time_in_progress == 0
    assert lifecycle_duration == 14 * 86400
    assert terminal_age is None


def test_completed_workflow_is_not_marked_overdue():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    completed_at = datetime(
        2026,
        1,
        10,
        tzinfo=timezone.utc,
    )

    now = datetime(
        2026,
        3,
        1,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="COMPLETED",
        created_at=created_at,
        completed_at=completed_at,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=now,
    )

    assert intelligence.health == WorkflowHealth.COMPLETED
    assert intelligence.attention_required is False
    assert intelligence.terminal_age_seconds == (
        now - completed_at
    ).total_seconds()


def test_ageing_calculation_does_not_mutate_workflow():
    created_at = datetime(
        2026,
        1,
        1,
        tzinfo=timezone.utc,
    )

    started_at = datetime(
        2026,
        1,
        5,
        tzinfo=timezone.utc,
    )

    workflow = _workflow(
        status="IN_PROGRESS",
        created_at=created_at,
        started_at=started_at,
    )

    original_status = workflow.status
    original_created_at = workflow.created_at
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
    assert workflow.created_at == original_created_at
    assert workflow.started_at == original_started_at
    assert workflow.completed_at == original_completed_at
    assert workflow.cancelled_at == original_cancelled_at