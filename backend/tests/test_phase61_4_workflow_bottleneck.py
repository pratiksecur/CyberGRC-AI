from datetime import datetime, timedelta, timezone

from app.models.risk_response_workflow import RiskResponseWorkflowRecord
from app.services.risk_response_workflow_intelligence_service import (
    WORKFLOW_AGING_DAYS,
    WORKFLOW_OVERDUE_DAYS,
    WorkflowBottleneckReason,
    derive_workflow_bottleneck,
    get_workflow_intelligence,
)


NOW = datetime(2026, 1, 31, 12, 0, 0, tzinfo=timezone.utc)


def _workflow(
    *,
    workflow_id: int = 1,
    risk_id: int = 10,
    status: str = "OPEN",
    created_days_ago: float = 1,
    started_days_ago: float | None = None,
    completed_days_ago: float | None = None,
    cancelled_days_ago: float | None = None,
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

    return RiskResponseWorkflowRecord(
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


def test_open_recent_workflow_is_not_bottlenecked():
    workflow = _workflow(
        status="OPEN",
        created_days_ago=1,
    )

    bottlenecked, reasons = derive_workflow_bottleneck(
        workflow,
        age_days=1,
    )

    assert bottlenecked is False
    assert reasons == (
        WorkflowBottleneckReason.BOTTLENECK_NONE.value,
    )


def test_open_aging_workflow_is_not_started_bottleneck():
    workflow = _workflow(
        status="OPEN",
        created_days_ago=WORKFLOW_AGING_DAYS,
    )

    bottlenecked, reasons = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_AGING_DAYS,
    )

    assert bottlenecked is True
    assert reasons == (
        WorkflowBottleneckReason.BOTTLENECK_NOT_STARTED.value,
        WorkflowBottleneckReason.BOTTLENECK_AGING.value,
    )


def test_in_progress_aging_workflow_is_bottlenecked():
    workflow = _workflow(
        status="IN_PROGRESS",
        created_days_ago=WORKFLOW_AGING_DAYS,
        started_days_ago=WORKFLOW_AGING_DAYS - 1,
    )

    bottlenecked, reasons = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_AGING_DAYS,
    )

    assert bottlenecked is True
    assert reasons == (
        WorkflowBottleneckReason.BOTTLENECK_IN_PROGRESS.value,
        WorkflowBottleneckReason.BOTTLENECK_AGING.value,
    )


def test_open_overdue_workflow_has_not_started_and_overdue_reasons():
    workflow = _workflow(
        status="OPEN",
        created_days_ago=WORKFLOW_OVERDUE_DAYS,
    )

    bottlenecked, reasons = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_OVERDUE_DAYS,
    )

    assert bottlenecked is True
    assert reasons == (
        WorkflowBottleneckReason.BOTTLENECK_NOT_STARTED.value,
        WorkflowBottleneckReason.BOTTLENECK_OVERDUE.value,
    )


def test_in_progress_overdue_workflow_has_in_progress_and_overdue_reasons():
    workflow = _workflow(
        status="IN_PROGRESS",
        created_days_ago=WORKFLOW_OVERDUE_DAYS,
        started_days_ago=WORKFLOW_OVERDUE_DAYS - 2,
    )

    bottlenecked, reasons = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_OVERDUE_DAYS,
    )

    assert bottlenecked is True
    assert reasons == (
        WorkflowBottleneckReason.BOTTLENECK_IN_PROGRESS.value,
        WorkflowBottleneckReason.BOTTLENECK_OVERDUE.value,
    )


def test_completed_workflow_is_not_bottlenecked():
    workflow = _workflow(
        status="COMPLETED",
        created_days_ago=WORKFLOW_OVERDUE_DAYS + 10,
        completed_days_ago=1,
    )

    bottlenecked, reasons = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_OVERDUE_DAYS + 10,
    )

    assert bottlenecked is False
    assert reasons == (
        WorkflowBottleneckReason.BOTTLENECK_TERMINAL.value,
    )


def test_cancelled_workflow_is_not_bottlenecked():
    workflow = _workflow(
        status="CANCELLED",
        created_days_ago=WORKFLOW_OVERDUE_DAYS + 10,
        cancelled_days_ago=1,
    )

    bottlenecked, reasons = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_OVERDUE_DAYS + 10,
    )

    assert bottlenecked is False
    assert reasons == (
        WorkflowBottleneckReason.BOTTLENECK_TERMINAL.value,
    )


def test_bottleneck_intelligence_is_included_in_complete_intelligence():
    workflow = _workflow(
        status="IN_PROGRESS",
        created_days_ago=WORKFLOW_AGING_DAYS,
        started_days_ago=WORKFLOW_AGING_DAYS - 1,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.bottlenecked is True
    assert intelligence.bottleneck_reason_codes == (
        WorkflowBottleneckReason.BOTTLENECK_IN_PROGRESS.value,
        WorkflowBottleneckReason.BOTTLENECK_AGING.value,
    )


def test_bottleneck_detection_does_not_mutate_workflow():
    workflow = _workflow(
        status="IN_PROGRESS",
        created_days_ago=WORKFLOW_OVERDUE_DAYS,
        started_days_ago=WORKFLOW_OVERDUE_DAYS - 2,
    )

    before = (
        workflow.status,
        workflow.started_at,
        workflow.completed_at,
        workflow.cancelled_at,
    )

    derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_OVERDUE_DAYS,
    )

    after = (
        workflow.status,
        workflow.started_at,
        workflow.completed_at,
        workflow.cancelled_at,
    )

    assert after == before


def test_bottleneck_threshold_is_exactly_respected():
    workflow = _workflow(
        status="OPEN",
        created_days_ago=WORKFLOW_AGING_DAYS,
    )

    bottlenecked, _ = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_AGING_DAYS - 0.0001,
    )

    assert bottlenecked is False

    bottlenecked, _ = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_AGING_DAYS,
    )

    assert bottlenecked is True


def test_overdue_threshold_is_exactly_respected():
    workflow = _workflow(
        status="IN_PROGRESS",
        created_days_ago=WORKFLOW_OVERDUE_DAYS,
        started_days_ago=WORKFLOW_OVERDUE_DAYS - 1,
    )

    bottlenecked, reasons = derive_workflow_bottleneck(
        workflow,
        age_days=WORKFLOW_OVERDUE_DAYS,
    )

    assert bottlenecked is True
    assert (
        WorkflowBottleneckReason.BOTTLENECK_OVERDUE.value
        in reasons
    )