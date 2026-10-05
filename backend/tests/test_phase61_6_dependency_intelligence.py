from datetime import datetime, timezone

from app.models.risk_response_workflow import RiskResponseWorkflowRecord
from app.services.risk_response_workflow_intelligence_service import (
    WorkflowDependencyReason,
    WorkflowDependencyState,
    derive_workflow_dependency,
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


def _workflow(
    *,
    target_type="RISK",
    target_id=10,
):
    return RiskResponseWorkflowRecord(
        id=1,
        execution_id=1,
        decision_id=1,
        risk_id=10,
        workflow_type="REVIEW",
        status="OPEN",
        target_type=target_type,
        target_id=target_id,
        title="Test workflow",
        description="Test workflow description",
        created_by_id=1,
        updated_by_id=None,
        resolution_reason=None,
        started_at=None,
        completed_at=None,
        cancelled_at=None,
        created_at=NOW,
        updated_at=NOW,
    )


def test_workflow_with_target_has_available_dependency():
    workflow = _workflow(
        target_type="RISK",
        target_id=10,
    )

    state, reasons, target_type, target_id = (
        derive_workflow_dependency(workflow)
    )

    assert state == WorkflowDependencyState.AVAILABLE
    assert reasons == (
        WorkflowDependencyReason.TARGET_RESOURCE_AVAILABLE.value,
    )
    assert target_type == "RISK"
    assert target_id == 10


def test_workflow_without_target_has_no_dependency():
    workflow = _workflow(
        target_type=None,
        target_id=None,
    )

    state, reasons, target_type, target_id = (
        derive_workflow_dependency(workflow)
    )

    assert state == WorkflowDependencyState.NO_DEPENDENCY
    assert reasons == (
        WorkflowDependencyReason.NO_DEPENDENCY.value,
    )
    assert target_type is None
    assert target_id is None


def test_workflow_without_target_id_has_no_dependency():
    workflow = _workflow(
        target_type="RISK",
        target_id=None,
    )

    state, reasons, target_type, target_id = (
        derive_workflow_dependency(workflow)
    )

    assert state == WorkflowDependencyState.NO_DEPENDENCY
    assert reasons == (
        WorkflowDependencyReason.NO_DEPENDENCY.value,
    )
    assert target_type == "RISK"
    assert target_id is None


def test_target_type_is_normalized():
    workflow = _workflow(
        target_type="  risk  ",
        target_id=10,
    )

    state, reasons, target_type, target_id = (
        derive_workflow_dependency(workflow)
    )

    assert state == WorkflowDependencyState.AVAILABLE
    assert target_type == "RISK"
    assert target_id == 10


def test_dependency_intelligence_is_included_in_complete_intelligence():
    workflow = _workflow(
        target_type="RISK",
        target_id=10,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.dependency_state == (
        WorkflowDependencyState.AVAILABLE
    )

    assert intelligence.dependency_reason_codes == (
        WorkflowDependencyReason.TARGET_RESOURCE_AVAILABLE.value,
    )

    assert intelligence.dependency_target_type == "RISK"
    assert intelligence.dependency_target_id == 10


def test_missing_dependency_information_does_not_create_fake_target():
    workflow = _workflow(
        target_type=None,
        target_id=None,
    )

    intelligence = get_workflow_intelligence(
        workflow,
        now=NOW,
    )

    assert intelligence.dependency_state == (
        WorkflowDependencyState.NO_DEPENDENCY
    )

    assert intelligence.dependency_target_type is None
    assert intelligence.dependency_target_id is None


def test_dependency_intelligence_does_not_mutate_workflow():
    workflow = _workflow(
        target_type="RISK",
        target_id=10,
    )

    before = (
        workflow.target_type,
        workflow.target_id,
        workflow.status,
    )

    derive_workflow_dependency(workflow)

    after = (
        workflow.target_type,
        workflow.target_id,
        workflow.status,
    )

    assert after == before


def test_dependency_intelligence_is_deterministic():
    workflow = _workflow(
        target_type="CONTROL",
        target_id=20,
    )

    first = derive_workflow_dependency(workflow)
    second = derive_workflow_dependency(workflow)

    assert first == second