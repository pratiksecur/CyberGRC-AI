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


def _build_phase60_chain(
    db,
    *,
    risk,
    manager,
):
    decision = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision="REASSESS_RISK",
        priority="HIGH",
        governance_level="HUMAN_APPROVAL_REQUIRED",
        status="APPROVED",
        human_approval_required=True,
        response_event_key=(
            f"phase60-7-event-{risk.id}"
        ),
        reason_codes=[
            "PHASE60_7_ACCEPTANCE",
        ],
        risk_state="REASSESSMENT_REQUIRED",
        treatment_state="REQUIRES_REASSESSMENT",
        reassessment_required=True,
        response_required=True,
        requested_by_id=manager.id,
        assigned_to_id=manager.id,
        resolution_reason=(
            "Human approval recorded for Phase 60 acceptance."
        ),
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
        executed_by_id=manager.id,
        execution_reason=(
            "Approved response execution for Phase 60 acceptance."
        ),
        result_message=(
            "Governed response execution recorded successfully."
        ),
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
            "Perform a governed reassessment of the risk."
        ),
        created_by_id=manager.id,
    )

    db.add(workflow)
    db.commit()

    db.refresh(decision)
    db.refresh(execution)
    db.refresh(workflow)

    return decision, execution, workflow


def test_phase60_end_to_end_governance_chain(
    db,
    users,
    resource_data,
):
    """
    Phase 60.7 acceptance:

        Risk
          ↓
        Decision
          ↓
        Approval
          ↓
        Execution
          ↓
        Workflow
          ↓
        Lifecycle
    """

    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    decision, execution, workflow = _build_phase60_chain(
        db,
        risk=risk,
        manager=manager,
    )

    # ------------------------------------------------------
    # Decision
    # ------------------------------------------------------

    assert decision.status == "APPROVED"
    assert decision.human_approval_required is True
    assert decision.risk_id == risk.id

    # ------------------------------------------------------
    # Execution
    # ------------------------------------------------------

    assert execution.status == "EXECUTED"
    assert execution.decision_id == decision.id
    assert execution.risk_id == risk.id
    assert execution.human_approval_verified is True
    assert execution.response_event_verified is True

    # ------------------------------------------------------
    # Workflow
    # ------------------------------------------------------

    assert workflow.status == "OPEN"
    assert workflow.execution_id == execution.id
    assert workflow.decision_id == decision.id
    assert workflow.risk_id == risk.id
    assert workflow.target_type == "RISK"
    assert workflow.target_id == risk.id

    # ------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------

    transition_response_workflow(
        db,
        workflow,
        target_status="IN_PROGRESS",
        actor=manager,
    )

    assert workflow.status == "IN_PROGRESS"
    assert workflow.started_at is not None

    transition_response_workflow(
        db,
        workflow,
        target_status="COMPLETED",
        actor=manager,
        resolution_reason=(
            "Phase 60 governed workflow completed "
            "after human review."
        ),
    )

    db.commit()
    db.refresh(workflow)

    assert workflow.status == "COMPLETED"
    assert workflow.updated_by_id == manager.id
    assert workflow.completed_at is not None
    assert workflow.resolution_reason == (
        "Phase 60 governed workflow completed "
        "after human review."
    )


def test_phase60_cancellation_path(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    decision, execution, workflow = _build_phase60_chain(
        db,
        risk=risk,
        manager=manager,
    )

    assert decision.status == "APPROVED"
    assert execution.status == "EXECUTED"
    assert workflow.status == "OPEN"

    transition_response_workflow(
        db,
        workflow,
        target_status="CANCELLED",
        actor=manager,
        resolution_reason=(
            "Human reviewer cancelled the governed workflow."
        ),
    )

    db.commit()
    db.refresh(workflow)

    assert workflow.status == "CANCELLED"
    assert workflow.cancelled_at is not None
    assert workflow.updated_by_id == manager.id
    assert workflow.resolution_reason == (
        "Human reviewer cancelled the governed workflow."
    )


def test_phase60_completion_does_not_equal_domain_remediation(
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

    _, _, workflow = _build_phase60_chain(
        db,
        risk=risk,
        manager=manager,
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
            "Workflow process completed; domain remediation "
            "remains a separate governed operation."
        ),
    )

    db.commit()
    db.refresh(risk)

    assert risk.title == original_title
    assert risk.description == original_description
    assert risk.status == original_status
    assert risk.risk_score == original_score


def test_phase60_audit_chain_remains_linked(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    decision, execution, workflow = _build_phase60_chain(
        db,
        risk=risk,
        manager=manager,
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
        resolution_reason="Acceptance completed.",
    )

    db.commit()

    db.refresh(decision)
    db.refresh(execution)
    db.refresh(workflow)

    assert workflow.decision_id == decision.id
    assert workflow.execution_id == execution.id
    assert workflow.risk_id == risk.id

    assert execution.decision_id == decision.id
    assert execution.risk_id == risk.id

    assert decision.risk_id == risk.id

    assert workflow.status == "COMPLETED"