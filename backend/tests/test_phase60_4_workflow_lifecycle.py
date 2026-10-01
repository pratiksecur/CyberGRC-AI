import pytest

from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)

from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
)

from app.services.governed_response_execution_service import (
    execute_governed_response,
)

from app.services.risk_response_decision_service import (
    RiskResponseDecisionStatus,
    create_response_decision,
    transition_response_decision,
)

from app.services.risk_response_workflow_service import (
    CANCELLED,
    COMPLETED,
    IN_PROGRESS,
    WorkflowLifecycleUnauthorized,
    WorkflowLifecycleValidationError,
    transition_response_workflow,
)


def _response(
    *,
    risk_id,
    decision=RiskResponseDecision.REASSESS_RISK,
):
    action = RiskResponseAction(
        decision=decision,
        priority="HIGH",
        reason_codes=("PHASE60_4_TEST",),
        human_approval_required=True,
    )

    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state="REASSESSMENT_REQUIRED",
        treatment_state="REQUIRES_REASSESSMENT",
        reassessment_required=True,
        response_required=True,
        priority="HIGH",
        decisions=(action,),
        human_approval_required=True,
        reasons=(),
    )


def _workflow(
    db,
    *,
    risk,
    manager,
):
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
        RiskResponseDecisionStatus.APPROVED,
        actor=manager,
        resolution_reason=(
            "Approved for Phase 60.4 lifecycle testing."
        ),
        current_response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    return (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .one()
    )


def test_open_to_in_progress_records_actor_and_timestamp(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    assert workflow.status == "OPEN"
    assert workflow.started_at is None

    updated = transition_response_workflow(
        db,
        workflow,
        target_status=IN_PROGRESS,
        actor=manager,
    )

    assert updated.status == IN_PROGRESS
    assert updated.updated_by_id == manager.id
    assert updated.started_at is not None
    assert updated.completed_at is None
    assert updated.cancelled_at is None


def test_open_to_cancelled_requires_reason(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    with pytest.raises(
        WorkflowLifecycleValidationError
    ):
        transition_response_workflow(
            db,
            workflow,
            target_status=CANCELLED,
            actor=manager,
        )

    assert workflow.status == "OPEN"


def test_open_to_cancelled_records_reason_and_timestamp(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    updated = transition_response_workflow(
        db,
        workflow,
        target_status=CANCELLED,
        actor=manager,
        resolution_reason=(
            "Workflow cancelled because the response "
            "requirement was withdrawn."
        ),
    )

    assert updated.status == CANCELLED
    assert updated.updated_by_id == manager.id
    assert updated.cancelled_at is not None
    assert updated.completed_at is None
    assert (
        updated.resolution_reason
        == (
            "Workflow cancelled because the response "
            "requirement was withdrawn."
        )
    )


def test_in_progress_to_completed_requires_reason(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status=IN_PROGRESS,
        actor=manager,
    )

    with pytest.raises(
        WorkflowLifecycleValidationError
    ):
        transition_response_workflow(
            db,
            workflow,
            target_status=COMPLETED,
            actor=manager,
        )

    assert workflow.status == IN_PROGRESS
    assert workflow.completed_at is None


def test_in_progress_to_completed_records_completion(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status=IN_PROGRESS,
        actor=manager,
    )

    updated = transition_response_workflow(
        db,
        workflow,
        target_status=COMPLETED,
        actor=manager,
        resolution_reason=(
            "Governed workflow review completed."
        ),
    )

    assert updated.status == COMPLETED
    assert updated.updated_by_id == manager.id
    assert updated.started_at is not None
    assert updated.completed_at is not None
    assert updated.cancelled_at is None
    assert (
        updated.resolution_reason
        == "Governed workflow review completed."
    )


def test_completed_workflow_is_terminal(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status=IN_PROGRESS,
        actor=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status=COMPLETED,
        actor=manager,
        resolution_reason="Completed.",
    )

    with pytest.raises(
        WorkflowLifecycleValidationError
    ):
        transition_response_workflow(
            db,
            workflow,
            target_status=IN_PROGRESS,
            actor=manager,
        )

    assert workflow.status == COMPLETED


def test_cancelled_workflow_is_terminal(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status=CANCELLED,
        actor=manager,
        resolution_reason="Cancelled.",
    )

    with pytest.raises(
        WorkflowLifecycleValidationError
    ):
        transition_response_workflow(
            db,
            workflow,
            target_status=IN_PROGRESS,
            actor=manager,
        )

    assert workflow.status == CANCELLED


def test_employee_cannot_transition_workflow(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]
    employee = users["employee"]

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    with pytest.raises(
        WorkflowLifecycleUnauthorized
    ):
        transition_response_workflow(
            db,
            workflow,
            target_status=IN_PROGRESS,
            actor=employee,
        )

    assert workflow.status == "OPEN"


def test_completion_does_not_mutate_underlying_risk(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original_title = risk.title
    original_description = risk.description

    workflow = _workflow(
        db,
        risk=risk,
        manager=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status=IN_PROGRESS,
        actor=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status=COMPLETED,
        actor=manager,
        resolution_reason=(
            "Workflow process completed without "
            "direct risk mutation."
        ),
    )

    db.refresh(risk)

    assert risk.title == original_title
    assert risk.description == original_description
