import pytest

from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)

from app.models.risk_control import (
    RiskControl,
)

from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
    RiskResponsePriority,
)

from app.services.governed_response_execution_service import (
    ResponseWorkflowError,
    UnsupportedResponseWorkflow,
    WorkflowTargetNotFound,
    execute_governed_response,
)

from app.services.risk_response_decision_service import (
    RiskResponseDecisionStatus,
    create_response_decision,
    transition_response_decision,
)


def _response(
    *,
    risk_id,
    decision,
    priority=RiskResponsePriority.HIGH,
    reason_codes=("TEST_REASON",),
):
    action = RiskResponseAction(
        decision=decision,
        priority=priority,
        reason_codes=reason_codes,
        human_approval_required=True,
    )

    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state="REASSESSMENT_REQUIRED",
        treatment_state="REQUIRES_REASSESSMENT",
        reassessment_required=True,
        response_required=True,
        priority=priority,
        decisions=(action,),
        human_approval_required=True,
        reasons=(),
    )


def _approved_decision(
    db,
    *,
    risk,
    manager,
    response,
):
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
            "Approved for governed Phase 60 workflow execution."
        ),
        current_response=response,
    )

    return decision


def _ensure_employee_risk_control(
    db,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    control = resource_data["controls"]["employee"]

    existing = (
        db.query(RiskControl)
        .filter(
            RiskControl.risk_id == risk.id,
            RiskControl.control_id == control.id,
        )
        .first()
    )

    if existing is not None:
        return existing

    risk_control = RiskControl(
        risk_id=risk.id,
        control_id=control.id,
    )

    db.add(risk_control)
    db.commit()
    db.refresh(risk_control)

    return risk_control


def test_reassess_risk_creates_governed_workflow(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.REASSESS_RISK,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .one()
    )

    assert workflow.workflow_type == "REASSESS_RISK"
    assert workflow.status == "OPEN"
    assert workflow.target_type == "RISK"
    assert workflow.target_id == risk.id
    assert workflow.risk_id == risk.id
    assert workflow.decision_id == decision.id
    assert workflow.created_by_id == manager.id


def test_escalate_creates_risk_workflow(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .one()
    )

    assert workflow.workflow_type == "ESCALATE"
    assert workflow.target_type == "RISK"
    assert workflow.target_id == risk.id


def test_review_creates_risk_workflow(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.REVIEW,
        priority=RiskResponsePriority.MEDIUM,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .one()
    )

    assert workflow.workflow_type == "REVIEW"
    assert workflow.target_type == "RISK"
    assert workflow.target_id == risk.id


def test_update_treatment_targets_existing_treatment(
    db,
    users,
    resource_data,
):
    from app.models.risk_treatment import RiskTreatment

    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Mitigate",
        status="In Progress",
        treatment_plan="Maintain treatment.",
        owner_id=manager.id,
        acceptance_status="Not Required",
        residual_likelihood=2,
        residual_impact=3,
        residual_risk_score=6,
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.UPDATE_TREATMENT,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .one()
    )

    assert workflow.workflow_type == "UPDATE_TREATMENT"
    assert workflow.target_type == "RISK_TREATMENT"
    assert workflow.target_id == treatment.id


def test_control_review_requires_associated_control(
    db,
    users,
    resource_data,
):
    _ensure_employee_risk_control(
        db,
        resource_data,
    )

    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.CONTROL_REVIEW,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .one()
    )

    assert workflow.workflow_type == "CONTROL_REVIEW"
    assert workflow.target_type == "CONTROL"
    assert workflow.target_id is not None


def test_evidence_review_requires_evidence_target(
    db,
    users,
    resource_data,
):
    _ensure_employee_risk_control(
        db,
        resource_data,
    )

    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.EVIDENCE_REVIEW,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .one()
    )

    assert workflow.workflow_type == "EVIDENCE_REVIEW"
    assert workflow.target_type == "EVIDENCE"
    assert workflow.target_id is not None


def test_corrective_action_review_requires_action_target(
    db,
    users,
    resource_data,
):
    _ensure_employee_risk_control(
        db,
        resource_data,
    )

    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.CORRECTIVE_ACTION_REVIEW,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .one()
    )

    assert workflow.workflow_type == (
        "CORRECTIVE_ACTION_REVIEW"
    )
    assert workflow.target_type == "CORRECTIVE_ACTION"
    assert workflow.target_id is not None


def test_workflow_creation_preserves_execution_audit(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.REASSESS_RISK,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    execution = execute_governed_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    assert execution.status == "EXECUTED"
    assert execution.decision_id == decision.id
    assert execution.risk_id == risk.id
    assert execution.executed_by_id == manager.id
    assert "Phase 60 workflow" in execution.result_message


def test_workflow_failure_does_not_leave_partial_execution(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.UPDATE_TREATMENT,
    )

    decision = _approved_decision(
        db,
        risk=risk,
        manager=manager,
        response=response,
    )

    with pytest.raises(WorkflowTargetNotFound):
        execute_governed_response(
            db,
            decision,
            actor=manager,
            current_response=response,
        )

    db.rollback()

    from app.models.risk_response_execution import (
        RiskResponseExecutionRecord,
    )

    assert (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision.id,
        )
        .count()
        == 0
    )

    assert (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.decision_id
            == decision.id,
        )
        .count()
        == 0
    )