"""
Governed Risk Response Workflow Lifecycle Service

Phase 60.4
----------

Provides controlled lifecycle transitions for Phase 60
governed response workflows.

Important boundary:

Completing a workflow means that the governed workflow
process itself has been completed.

It does NOT automatically mean that the underlying:
- Risk
- RiskTreatment
- Control
- Evidence
- AuditFinding
- CorrectiveAction

has been modified or remediated.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.roles import UserRole
from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)
from app.models.user import User


class ResponseWorkflowLifecycleError(Exception):
    """Base workflow lifecycle error."""


class WorkflowNotFound(ResponseWorkflowLifecycleError):
    """Raised when the workflow cannot be found."""


class WorkflowLifecycleValidationError(
    ResponseWorkflowLifecycleError
):
    """Raised when a lifecycle transition is invalid."""


class WorkflowLifecycleUnauthorized(
    ResponseWorkflowLifecycleError
):
    """Raised when the actor cannot transition workflows."""


OPEN = "OPEN"
IN_PROGRESS = "IN_PROGRESS"
COMPLETED = "COMPLETED"
CANCELLED = "CANCELLED"

TERMINAL_STATUSES = {
    COMPLETED,
    CANCELLED,
}

ALLOWED_TRANSITIONS = {
    OPEN: {
        IN_PROGRESS,
        CANCELLED,
    },
    IN_PROGRESS: {
        COMPLETED,
        CANCELLED,
    },
}


def _validate_actor(actor: User) -> None:
    if actor is None or actor.id is None:
        raise WorkflowLifecycleUnauthorized(
            "A valid workflow transition actor is required."
        )

    if actor.role not in {
        UserRole.ADMIN.value,
        UserRole.GRC_MANAGER.value,
    }:
        raise WorkflowLifecycleUnauthorized(
            "Only Admin and GRC Manager may transition "
            "governed response workflows."
        )


def _normalize_reason(
    resolution_reason: str | None,
) -> str | None:
    if resolution_reason is None:
        return None

    normalized = resolution_reason.strip()

    if not normalized:
        return None

    return normalized


def _validate_transition(
    workflow: RiskResponseWorkflowRecord,
    target_status: str,
    resolution_reason: str | None,
) -> str | None:
    current_status = workflow.status

    if current_status in TERMINAL_STATUSES:
        raise WorkflowLifecycleValidationError(
            "A completed or cancelled workflow is terminal "
            "and cannot be transitioned."
        )

    allowed = ALLOWED_TRANSITIONS.get(
        current_status,
        set(),
    )

    if target_status not in allowed:
        raise WorkflowLifecycleValidationError(
            f"Invalid workflow transition: "
            f"{current_status} -> {target_status}."
        )

    normalized_reason = _normalize_reason(
        resolution_reason,
    )

    if target_status in {
        COMPLETED,
        CANCELLED,
    } and normalized_reason is None:
        raise WorkflowLifecycleValidationError(
            "A resolution reason is required when a workflow "
            "is completed or cancelled."
        )

    return normalized_reason


def get_workflow_for_transition(
    db: Session,
    *,
    workflow_id: int,
    risk_id: int,
) -> RiskResponseWorkflowRecord:
    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.id == workflow_id,
            RiskResponseWorkflowRecord.risk_id == risk_id,
        )
        .first()
    )

    if workflow is None:
        raise WorkflowNotFound(
            "Response workflow not found."
        )

    return workflow


def transition_response_workflow(
    db: Session,
    workflow: RiskResponseWorkflowRecord,
    *,
    target_status: str,
    actor: User,
    resolution_reason: str | None = None,
) -> RiskResponseWorkflowRecord:
    """
    Transition a governed response workflow.

    This function changes only workflow lifecycle state.
    It does not mutate the underlying GRC target.
    """

    _validate_actor(actor)

    if target_status not in {
        IN_PROGRESS,
        COMPLETED,
        CANCELLED,
    }:
        raise WorkflowLifecycleValidationError(
            f"Unsupported workflow lifecycle status: "
            f"{target_status}."
        )

    normalized_reason = _validate_transition(
        workflow,
        target_status,
        resolution_reason,
    )

    now = datetime.now(timezone.utc)

    workflow.status = target_status
    workflow.updated_by_id = actor.id

    if target_status == IN_PROGRESS:
        if workflow.started_at is None:
            workflow.started_at = now

    elif target_status == COMPLETED:
        workflow.completed_at = now
        workflow.resolution_reason = normalized_reason

    elif target_status == CANCELLED:
        workflow.cancelled_at = now
        workflow.resolution_reason = normalized_reason

    db.flush()

    return workflow