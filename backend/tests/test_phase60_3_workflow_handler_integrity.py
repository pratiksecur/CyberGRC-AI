import pytest

from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)

from app.models.risk_response_execution import (
    RiskResponseExecutionRecord,
)

from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)

from app.models.risk_treatment import (
    RiskTreatment,
)

from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
    RiskResponsePriority,
)

from app.services.governed_response_execution_service import (
    UnsupportedResponseWorkflow,
    WorkflowCreationError,
    WorkflowTargetNotFound,
    create_response_workflow,
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
    reason_codes=("PHASE60_3_TEST",),
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
            "Approved for Phase 60.3 workflow integrity testing."
        ),
        current_response=response,
    )

    return decision


def _create_approved_execution(
    db,
    *,
    risk,
    manager,
    decision_type=RiskResponseDecision.REASSESS_RISK,
):
    response = _response(
        risk_id=risk.id,
        decision=decision_type,
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

    return response, decision, execution, workflow


def test_workflow_creation_is_idempotent(
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

    from app.services.risk_response_execution_service import (
        execute_approved_response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    first_workflow = create_response_workflow(
        db,
        execution,
        decision,
        risk,
        manager,
    )

    second_workflow = create_response_workflow(
        db,
        execution,
        decision,
        risk,
        manager,
    )

    assert second_workflow.id == first_workflow.id

    assert (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .count()
        == 1
    )


def test_workflow_rejects_mismatched_risk(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    other_risk = resource_data["risks"]["manager"]
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

    from app.services.risk_response_execution_service import (
        execute_approved_response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    with pytest.raises(WorkflowCreationError):
        create_response_workflow(
            db,
            execution,
            decision,
            other_risk,
            manager,
        )

    assert (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .count()
        == 0
    )


def test_workflow_rejects_mismatched_decision_risk(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    other_risk = resource_data["risks"]["manager"]
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

    from app.services.risk_response_execution_service import (
        execute_approved_response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    with pytest.raises(WorkflowCreationError):
        create_response_workflow(
            db,
            execution,
            decision,
            other_risk,
            manager,
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


def test_unsupported_persisted_decision_is_rejected(
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

    from app.services.risk_response_execution_service import (
        execute_approved_response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    decision.decision = "UNSUPPORTED_PHASE_60_ACTION"
    db.flush()

    with pytest.raises(UnsupportedResponseWorkflow):
        create_response_workflow(
            db,
            execution,
            decision,
            risk,
            manager,
        )

    assert (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .count()
        == 0
    )


def test_workflow_requires_creator_identity(
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

    from app.services.risk_response_execution_service import (
        execute_approved_response,
    )

    execution = execute_approved_response(
        db,
        decision,
        actor=manager,
        current_response=response,
    )

    class ActorWithoutIdentity:
        id = None

    with pytest.raises(WorkflowCreationError):
        create_response_workflow(
            db,
            execution,
            decision,
            risk,
            ActorWithoutIdentity(),
        )

    assert (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .count()
        == 0
    )


def test_update_treatment_workflow_does_not_mutate_treatment(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    treatment = RiskTreatment(
        risk_id=risk.id,
        strategy="Mitigate",
        status="In Progress",
        treatment_plan="Original treatment plan.",
        owner_id=manager.id,
        acceptance_status="Not Required",
        residual_likelihood=2,
        residual_impact=3,
        residual_risk_score=6,
    )

    db.add(treatment)
    db.commit()
    db.refresh(treatment)

    original_values = {
        "strategy": treatment.strategy,
        "status": treatment.status,
        "treatment_plan": treatment.treatment_plan,
        "owner_id": treatment.owner_id,
        "acceptance_status": treatment.acceptance_status,
        "residual_likelihood": treatment.residual_likelihood,
        "residual_impact": treatment.residual_impact,
        "residual_risk_score": treatment.residual_risk_score,
    }

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

    db.refresh(treatment)

    assert execution.status == "EXECUTED"

    assert {
        "strategy": treatment.strategy,
        "status": treatment.status,
        "treatment_plan": treatment.treatment_plan,
        "owner_id": treatment.owner_id,
        "acceptance_status": treatment.acceptance_status,
        "residual_likelihood": treatment.residual_likelihood,
        "residual_impact": treatment.residual_impact,
        "residual_risk_score": treatment.residual_risk_score,
    } == original_values


def test_failed_workflow_target_does_not_create_workflow(
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

    assert (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.decision_id
            == decision.id,
        )
        .count()
        == 0
    )


def test_phase59_execution_remains_intact_after_workflow_creation(
    db,
    users,
    resource_data,
):
    risk = resource_data["risks"]["employee"]
    manager = users["manager"]

    response, decision, execution, workflow = (
        _create_approved_execution(
            db,
            risk=risk,
            manager=manager,
            decision_type=RiskResponseDecision.REASSESS_RISK,
        )
    )

    persisted_execution = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.id
            == execution.id,
        )
        .one()
    )

    persisted_decision = (
        db.query(RiskResponseDecisionRecord)
        .filter(
            RiskResponseDecisionRecord.id
            == decision.id,
        )
        .one()
    )

    assert persisted_execution.id == execution.id
    assert persisted_execution.status == "EXECUTED"
    assert persisted_execution.decision_id == decision.id
    assert persisted_execution.risk_id == risk.id
    assert persisted_execution.executed_by_id == manager.id
    assert persisted_execution.human_approval_verified is True
    assert persisted_execution.response_event_verified is True

    assert persisted_decision.id == decision.id
    assert persisted_decision.status == "APPROVED"

    assert workflow.execution_id == persisted_execution.id
    assert workflow.decision_id == persisted_decision.id
    assert workflow.risk_id == risk.id
    assert workflow.status == "OPEN"