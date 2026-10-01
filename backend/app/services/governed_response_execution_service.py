"""
Governed Response Execution Service

Phase 60
--------

Converts a Phase 59 approved execution into an explicit,
auditable GRC workflow.

Important boundary:

Phase 59:
    Approval -> execution authorization -> execution audit

Phase 60:
    execution -> explicit workflow creation

The handlers do NOT silently mutate:
- Risk
- RiskTreatment
- Control
- Evidence
- AuditFinding
- CorrectiveAction

Instead they create an explicit governed workflow request
targeting the appropriate GRC resource.

This keeps execution deterministic and auditable while leaving
actual domain mutation to a later, explicitly authorized workflow
completion step.
"""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.audit_finding import AuditFinding
from app.models.corrective_action import CorrectiveAction
from app.models.evidence import Evidence
from app.models.risk import Risk
from app.models.risk_control import RiskControl
from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)
from app.models.risk_response_execution import (
    RiskResponseExecutionRecord,
)
from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)
from app.models.risk_treatment import RiskTreatment
from app.models.user import User

from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseDecision,
    get_continuous_risk_response,
)

from app.services.risk_response_execution_service import (
    execute_approved_response,
)

from app.services.risk_treatment_residual_service import (
    select_authoritative_treatment,
)


class ResponseWorkflowError(Exception):
    """Base error for governed response workflow execution."""


class UnsupportedResponseWorkflow(ResponseWorkflowError):
    """Raised when a response has no Phase 60 handler."""


class WorkflowTargetNotFound(ResponseWorkflowError):
    """Raised when a governed response target cannot be resolved."""


class WorkflowCreationError(ResponseWorkflowError):
    """Raised when a workflow cannot be created."""


@dataclass(frozen=True)
class WorkflowTarget:
    target_type: str
    target_id: int | None
    title: str
    description: str


# ============================================================
# TARGET RESOLUTION
# ============================================================


def _risk_target(
    risk: Risk,
    *,
    title: str,
    description: str,
) -> WorkflowTarget:
    return WorkflowTarget(
        target_type="RISK",
        target_id=risk.id,
        title=title,
        description=description,
    )


def _risk_control_ids(
    db: Session,
    risk_id: int,
) -> list[int]:
    return [
        row.control_id
        for row in (
            db.query(RiskControl)
            .filter(
                RiskControl.risk_id == risk_id,
            )
            .order_by(
                RiskControl.control_id.asc(),
            )
            .all()
        )
    ]


def _resolve_treatment_target(
    db: Session,
    risk: Risk,
) -> WorkflowTarget:
    treatments = (
        db.query(RiskTreatment)
        .filter(
            RiskTreatment.risk_id == risk.id,
        )
        .all()
    )

    treatment = select_authoritative_treatment(
        treatments,
    )

    if treatment is None:
        raise WorkflowTargetNotFound(
            "No authoritative risk treatment is available "
            "for the UPDATE_TREATMENT workflow."
        )

    return WorkflowTarget(
        target_type="RISK_TREATMENT",
        target_id=treatment.id,
        title="Risk treatment review required",
        description=(
            "Review the authoritative risk treatment because "
            "the governed response requires treatment follow-up."
        ),
    )


def _resolve_control_target(
    db: Session,
    risk: Risk,
) -> WorkflowTarget:
    control_id = (
        db.query(RiskControl)
        .filter(
            RiskControl.risk_id == risk.id,
        )
        .order_by(
            RiskControl.control_id.asc(),
        )
        .first()
    )

    if control_id is None:
        raise WorkflowTargetNotFound(
            "No control is associated with the risk."
        )

    return WorkflowTarget(
        target_type="CONTROL",
        target_id=control_id.control_id,
        title="Control review required",
        description=(
            "Review the control associated with the current "
            "continuous-risk response."
        ),
    )


def _resolve_evidence_target(
    db: Session,
    risk: Risk,
) -> WorkflowTarget:
    control_ids = _risk_control_ids(
        db,
        risk.id,
    )

    if not control_ids:
        raise WorkflowTargetNotFound(
            "No control is associated with the risk."
        )

    evidence = (
        db.query(Evidence)
        .filter(
            Evidence.control_id.in_(control_ids),
        )
        .order_by(
            Evidence.id.asc(),
        )
        .first()
    )

    if evidence is None:
        raise WorkflowTargetNotFound(
            "No evidence is associated with the risk controls."
        )

    return WorkflowTarget(
        target_type="EVIDENCE",
        target_id=evidence.id,
        title="Evidence review required",
        description=(
            "Review supporting evidence associated with the "
            "risk's controls."
        ),
    )


def _resolve_corrective_action_target(
    db: Session,
    risk: Risk,
) -> WorkflowTarget:
    control_ids = _risk_control_ids(
        db,
        risk.id,
    )

    if not control_ids:
        raise WorkflowTargetNotFound(
            "No control is associated with the risk."
        )

    finding_ids = [
        finding.id
        for finding in (
            db.query(AuditFinding)
            .filter(
                AuditFinding.control_id.in_(control_ids),
            )
            .order_by(
                AuditFinding.id.asc(),
            )
            .all()
        )
    ]

    if not finding_ids:
        raise WorkflowTargetNotFound(
            "No audit finding is associated with the risk controls."
        )

    action = (
        db.query(CorrectiveAction)
        .filter(
            CorrectiveAction.finding_id.in_(finding_ids),
        )
        .order_by(
            CorrectiveAction.id.asc(),
        )
        .first()
    )

    if action is None:
        raise WorkflowTargetNotFound(
            "No corrective action is associated with the "
            "risk findings."
        )

    return WorkflowTarget(
        target_type="CORRECTIVE_ACTION",
        target_id=action.id,
        title="Corrective-action review required",
        description=(
            "Review the corrective action associated with the "
            "risk's audit findings."
        ),
    )


# ============================================================
# HANDLER MAPPING
# ============================================================


def _resolve_workflow_target(
    db: Session,
    risk: Risk,
    decision: RiskResponseDecision,
) -> WorkflowTarget:
    if decision == RiskResponseDecision.REVIEW:
        return _risk_target(
            risk,
            title="Risk review required",
            description=(
                "Review the current risk posture and the "
                "governed response."
            ),
        )

    if decision == RiskResponseDecision.REASSESS_RISK:
        return _risk_target(
            risk,
            title="Risk reassessment required",
            description=(
                "Perform a governed reassessment of the risk "
                "because the continuous-risk response requires it."
            ),
        )

    if decision == RiskResponseDecision.ESCALATE:
        return _risk_target(
            risk,
            title="Risk escalation required",
            description=(
                "Escalate the governed risk response to the "
                "appropriate human decision-maker."
            ),
        )

    if decision == RiskResponseDecision.UPDATE_TREATMENT:
        return _resolve_treatment_target(
            db,
            risk,
        )

    if decision == RiskResponseDecision.CONTROL_REVIEW:
        return _resolve_control_target(
            db,
            risk,
        )

    if decision == RiskResponseDecision.EVIDENCE_REVIEW:
        return _resolve_evidence_target(
            db,
            risk,
        )

    if decision == RiskResponseDecision.CORRECTIVE_ACTION_REVIEW:
        return _resolve_corrective_action_target(
            db,
            risk,
        )

    raise UnsupportedResponseWorkflow(
        f"Response decision '{decision.value}' "
        "does not have a Phase 60 workflow handler."
    )


# ============================================================
# WORKFLOW CREATION
# ============================================================


def create_response_workflow(
    db: Session,
    execution: RiskResponseExecutionRecord,
    decision_record: RiskResponseDecisionRecord,
    risk: Risk,
    actor: User,
) -> RiskResponseWorkflowRecord:
    if execution.id is None:
        raise WorkflowCreationError(
            "Execution must be persisted before a workflow is created."
        )

    if decision_record.id is None:
        raise WorkflowCreationError(
            "Decision must be persisted before a workflow is created."
        )

    if risk.id != execution.risk_id:
        raise WorkflowCreationError(
            "Workflow risk does not match execution risk."
        )

    if decision_record.risk_id != execution.risk_id:
        raise WorkflowCreationError(
            "Decision risk does not match execution risk."
        )

    if actor.id is None:
        raise WorkflowCreationError(
            "Workflow creator identity is required."
        )

    existing = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution.id,
        )
        .first()
    )

    if existing is not None:
        return existing

    try:
        decision = RiskResponseDecision(
            decision_record.decision
        )
    except ValueError as exc:
        raise UnsupportedResponseWorkflow(
            "The persisted response decision is not supported."
        ) from exc

    target = _resolve_workflow_target(
        db,
        risk,
        decision,
    )

    workflow = RiskResponseWorkflowRecord(
        execution_id=execution.id,
        decision_id=decision_record.id,
        risk_id=execution.risk_id,
        workflow_type=decision_record.decision,
        status="OPEN",
        target_type=target.target_type,
        target_id=target.target_id,
        title=target.title,
        description=target.description,
        created_by_id=actor.id,
    )

    db.add(workflow)
    db.flush()

    return workflow


# ============================================================
# DISPATCHER
# ============================================================


def execute_governed_response(
    db: Session,
    decision: RiskResponseDecisionRecord,
    *,
    actor: User,
    current_response: ContinuousRiskResponse | None = None,
) -> RiskResponseExecutionRecord:
    """
    Execute Phase 59 governance and then dispatch the resulting
    approved response into an explicit Phase 60 workflow.

    The entire operation remains inside the caller's transaction.

    If workflow creation fails, the caller can roll back the
    transaction and the Phase 59 execution record will not remain
    partially persisted.
    """

    if current_response is None:
        risk = decision.risk

        if risk is None:
            raise WorkflowCreationError(
                "Risk associated with the response decision was not found."
            )

        current_response = get_continuous_risk_response(
            db,
            risk,
            current_user=actor,
        )

    execution = execute_approved_response(
        db,
        decision,
        actor=actor,
        current_response=current_response,
    )

    risk = decision.risk

    if risk is None:
        raise WorkflowCreationError(
            "Risk associated with the response decision was not found."
        )

    workflow = create_response_workflow(
        db,
        execution,
        decision,
        risk,
        actor,
    )

    execution.result_message = (
        "Governed response execution recorded successfully. "
        f"Phase 60 workflow #{workflow.id} created for "
        f"{workflow.workflow_type}."
    )

    db.flush()

    return execution


def get_response_workflow(
    db: Session,
    workflow_id: int,
    risk_id: int,
) -> RiskResponseWorkflowRecord | None:
    return (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.id == workflow_id,
            RiskResponseWorkflowRecord.risk_id == risk_id,
        )
        .first()
    )


def list_response_workflows(
    db: Session,
    risk_id: int,
) -> list[RiskResponseWorkflowRecord]:
    return (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.risk_id == risk_id,
        )
        .order_by(
            RiskResponseWorkflowRecord.created_at.desc(),
            RiskResponseWorkflowRecord.id.desc(),
        )
        .all()
    )