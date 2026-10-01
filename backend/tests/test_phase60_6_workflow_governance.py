from datetime import datetime, timezone

from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)
from app.models.risk_response_execution import (
    RiskResponseExecutionRecord,
)
from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)

from app.services.risk_response_workflow_service import (
    transition_response_workflow,
)


def _create_governed_chain(
    db,
    *,
    risk,
    actor,
):
    decision = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision="REASSESS_RISK",
        priority="HIGH",
        governance_level="HUMAN_APPROVAL_REQUIRED",
        status="APPROVED",
        human_approval_required=True,
        response_event_key=(
            f"phase60-6-event-{risk.id}"
        ),
        reason_codes=["PHASE60_6_TEST"],
        risk_state="REASSESSMENT_REQUIRED",
        treatment_state="REQUIRES_REASSESSMENT",
        reassessment_required=True,
        response_required=True,
        requested_by_id=actor.id,
        assigned_to_id=actor.id,
        resolution_reason="Approved governance decision.",
    )

    db.add(decision)
    db.flush()

    execution = RiskResponseExecutionRecord(
        decision_id=decision.id,
        risk_id=risk.id,
        decision="REASSESS_RISK",
        response_event_key=decision.response_event_key,
        status="EXECUTED",
        execution_action="REASSESS_RISK",
        human_approval_verified=True,
        response_event_verified=True,
        executed_by_id=actor.id,
        execution_reason="Approved response execution.",
        result_message="Execution recorded.",
        executed_at=datetime.now(timezone.utc),
    )

    db.add(execution)
    db.flush()

    workflow = RiskResponseWorkflowRecord(
        execution_id=execution.id,
        decision_id=decision.id,
        risk_id=risk.id,
        workflow_type="REASSESS_RISK",
        status="OPEN",
        target_type="RISK",
        target_id=risk.id,
        title="Risk reassessment required",
        description=(
            "Governed risk reassessment workflow."
        ),
        created_by_id=actor.id,
    )

    db.add(workflow)
    db.commit()

    db.refresh(decision)
    db.refresh(execution)
    db.refresh(workflow)

    return decision, execution, workflow


def test_workflow_preserves_complete_governance_chain(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    decision, execution, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    assert workflow.id is not None

    assert workflow.execution_id == execution.id
    assert workflow.decision_id == decision.id
    assert workflow.risk_id == risk.id

    assert execution.decision_id == decision.id
    assert execution.risk_id == risk.id

    assert decision.risk_id == risk.id


def test_workflow_records_creation_actor(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    _, _, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    assert workflow.created_by_id == manager.id
    assert workflow.updated_by_id is None


def test_in_progress_records_transition_actor_and_timestamp(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    _, _, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    updated = transition_response_workflow(
        db,
        workflow,
        target_status="IN_PROGRESS",
        actor=manager,
    )

    db.commit()
    db.refresh(updated)

    assert updated.status == "IN_PROGRESS"
    assert updated.updated_by_id == manager.id
    assert updated.started_at is not None


def test_completion_records_resolution_and_actor(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    _, _, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status="IN_PROGRESS",
        actor=manager,
    )

    updated = transition_response_workflow(
        db,
        workflow,
        target_status="COMPLETED",
        actor=manager,
        resolution_reason=(
            "Governed workflow completed after review."
        ),
    )

    db.commit()
    db.refresh(updated)

    assert updated.status == "COMPLETED"
    assert updated.updated_by_id == manager.id
    assert updated.completed_at is not None
    assert (
        updated.resolution_reason
        == "Governed workflow completed after review."
    )


def test_cancellation_records_resolution_and_actor(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    _, _, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    updated = transition_response_workflow(
        db,
        workflow,
        target_status="CANCELLED",
        actor=manager,
        resolution_reason=(
            "Governed workflow cancelled after review."
        ),
    )

    db.commit()
    db.refresh(updated)

    assert updated.status == "CANCELLED"
    assert updated.updated_by_id == manager.id
    assert updated.cancelled_at is not None
    assert (
        updated.resolution_reason
        == "Governed workflow cancelled after review."
    )


def test_workflow_completion_does_not_mutate_risk(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    original_title = risk.title
    original_description = risk.description
    original_status = risk.status
    original_score = risk.risk_score

    _, _, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status="IN_PROGRESS",
        actor=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status="COMPLETED",
        actor=manager,
        resolution_reason=(
            "Workflow process completed."
        ),
    )

    db.commit()
    db.refresh(risk)

    assert risk.title == original_title
    assert risk.description == original_description
    assert risk.status == original_status
    assert risk.risk_score == original_score


def test_terminal_workflow_cannot_be_reopened(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    _, _, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status="CANCELLED",
        actor=manager,
        resolution_reason="Workflow no longer required.",
    )

    db.commit()

    from app.services.risk_response_workflow_service import (
        WorkflowLifecycleValidationError,
    )

    try:
        transition_response_workflow(
            db,
            workflow,
            target_status="IN_PROGRESS",
            actor=manager,
        )
    except WorkflowLifecycleValidationError:
        pass
    else:
        raise AssertionError(
            "A cancelled workflow must remain terminal."
        )


def test_execution_remains_unchanged_after_workflow_completion(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    _, execution, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    original_status = execution.status
    original_action = execution.execution_action
    original_reason = execution.execution_reason

    transition_response_workflow(
        db,
        workflow,
        target_status="IN_PROGRESS",
        actor=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status="COMPLETED",
        actor=manager,
        resolution_reason="Workflow completed.",
    )

    db.commit()
    db.refresh(execution)

    assert execution.status == original_status
    assert execution.execution_action == original_action
    assert execution.execution_reason == original_reason


def test_decision_remains_unchanged_after_workflow_completion(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    decision, _, workflow = _create_governed_chain(
        db,
        risk=risk,
        actor=manager,
    )

    original_status = decision.status
    original_decision = decision.decision
    original_priority = decision.priority
    original_reason = decision.resolution_reason

    transition_response_workflow(
        db,
        workflow,
        target_status="IN_PROGRESS",
        actor=manager,
    )

    transition_response_workflow(
        db,
        workflow,
        target_status="COMPLETED",
        actor=manager,
        resolution_reason="Workflow completed.",
    )

    db.commit()
    db.refresh(decision)

    assert decision.status == original_status
    assert decision.decision == original_decision
    assert decision.priority == original_priority
    assert decision.resolution_reason == original_reason