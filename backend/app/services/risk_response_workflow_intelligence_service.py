"""
Governed Risk Response Workflow Intelligence Service

Phase 61
--------

Provides deterministic, read-only intelligence for governed
risk-response workflows.

Phase 61.1
----------
Workflow health and age intelligence.

Phase 61.2
----------
Workflow lifecycle timing intelligence.

Phase 61.3
----------
Workflow priority intelligence derived from the governed
risk-response decision.

Phase 61.4
----------
Workflow bottleneck intelligence.

Phase 61.5
----------
Escalation recommendation intelligence.

Phase 61.6
----------
Dependency intelligence derived from the governed workflow target.

Design principles:
- read-only;
- deterministic;
- no workflow mutation;
- no database writes;
- no automatic execution;
- no AI dependency;
- governed decision remains the source of workflow priority;
- escalation recommendations are recommendations only;
- workflow target remains the dependency boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from app.models.risk_response_workflow import RiskResponseWorkflowRecord
from app.services.continuous_risk_response_service import RiskResponsePriority


# ---------------------------------------------------------------------------
# Workflow health
# ---------------------------------------------------------------------------


class WorkflowHealth(str, Enum):
    HEALTHY = "HEALTHY"
    AGING = "AGING"
    OVERDUE = "OVERDUE"
    BLOCKED = "BLOCKED"
    ESCALATED = "ESCALATED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Workflow intelligence reason codes
# ---------------------------------------------------------------------------


class WorkflowIntelligenceReason(str, Enum):
    WORKFLOW_CURRENT = "WORKFLOW_CURRENT"
    WORKFLOW_AGING = "WORKFLOW_AGING"
    WORKFLOW_OVERDUE = "WORKFLOW_OVERDUE"
    WORKFLOW_COMPLETED = "WORKFLOW_COMPLETED"
    WORKFLOW_CANCELLED = "WORKFLOW_CANCELLED"


# ---------------------------------------------------------------------------
# Workflow priority reason codes
# ---------------------------------------------------------------------------


class WorkflowPriorityReason(str, Enum):
    DECISION_PRIORITY = "DECISION_PRIORITY"
    PRIORITY_REQUIRES_ATTENTION = "PRIORITY_REQUIRES_ATTENTION"


# ---------------------------------------------------------------------------
# Workflow bottleneck reason codes
# ---------------------------------------------------------------------------


class WorkflowBottleneckReason(str, Enum):
    BOTTLENECK_NONE = "BOTTLENECK_NONE"
    BOTTLENECK_NOT_STARTED = "BOTTLENECK_NOT_STARTED"
    BOTTLENECK_AGING = "BOTTLENECK_AGING"
    BOTTLENECK_OVERDUE = "BOTTLENECK_OVERDUE"
    BOTTLENECK_IN_PROGRESS = "BOTTLENECK_IN_PROGRESS"
    BOTTLENECK_TERMINAL = "BOTTLENECK_TERMINAL"


# ---------------------------------------------------------------------------
# Workflow escalation reason codes
# ---------------------------------------------------------------------------


class WorkflowEscalationReason(str, Enum):
    NO_ESCALATION = "NO_ESCALATION"
    HIGH_PRIORITY_BOTTLENECK = "HIGH_PRIORITY_BOTTLENECK"
    CRITICAL_PRIORITY = "CRITICAL_PRIORITY"
    OVERDUE_WORKFLOW = "OVERDUE_WORKFLOW"
    AGING_WORKFLOW_REQUIRES_ATTENTION = (
        "AGING_WORKFLOW_REQUIRES_ATTENTION"
    )


# ---------------------------------------------------------------------------
# Workflow escalation recommendation levels
# ---------------------------------------------------------------------------


class WorkflowEscalationRecommendation(str, Enum):
    NONE = "NONE"
    REVIEW = "REVIEW"
    ESCALATE = "ESCALATE"


# ---------------------------------------------------------------------------
# Workflow dependency states
# ---------------------------------------------------------------------------


class WorkflowDependencyState(str, Enum):
    NO_DEPENDENCY = "NO_DEPENDENCY"
    AVAILABLE = "AVAILABLE"
    MISSING = "MISSING"
    INCOMPLETE = "INCOMPLETE"
    ATTENTION_REQUIRED = "ATTENTION_REQUIRED"
    BLOCKING = "BLOCKING"


# ---------------------------------------------------------------------------
# Workflow dependency reason codes
# ---------------------------------------------------------------------------


class WorkflowDependencyReason(str, Enum):
    NO_DEPENDENCY = "NO_DEPENDENCY"
    TARGET_RESOURCE_AVAILABLE = "TARGET_RESOURCE_AVAILABLE"
    TARGET_RESOURCE_MISSING = "TARGET_RESOURCE_MISSING"
    TARGET_RESOURCE_INCOMPLETE = "TARGET_RESOURCE_INCOMPLETE"
    TARGET_RESOURCE_REQUIRES_ATTENTION = (
        "TARGET_RESOURCE_REQUIRES_ATTENTION"
    )
    TARGET_RESOURCE_BLOCKING = "TARGET_RESOURCE_BLOCKING"


# ---------------------------------------------------------------------------
# Thresholds
# ---------------------------------------------------------------------------


WORKFLOW_AGING_DAYS = 7
WORKFLOW_OVERDUE_DAYS = 30


# ---------------------------------------------------------------------------
# Priority ranking
# ---------------------------------------------------------------------------


WORKFLOW_PRIORITY_RANK: dict[RiskResponsePriority, int] = {
    RiskResponsePriority.LOW: 1,
    RiskResponsePriority.MEDIUM: 2,
    RiskResponsePriority.HIGH: 3,
    RiskResponsePriority.CRITICAL: 4,
}


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RiskResponseWorkflowIntelligence:
    workflow_id: int
    risk_id: int

    status: str

    health: WorkflowHealth

    age_days: float
    age_seconds: float

    attention_required: bool

    reason_codes: tuple[str, ...]

    started: bool
    terminal: bool

    # Phase 61.2 lifecycle timing
    time_to_start_seconds: float | None
    time_in_progress_seconds: float | None
    lifecycle_duration_seconds: float
    terminal_age_seconds: float | None

    # Phase 61.3 priority intelligence
    decision_priority: RiskResponsePriority | None
    priority_rank: int | None
    governance_level: str | None
    priority_requires_attention: bool
    priority_reason_codes: tuple[str, ...]

    # Phase 61.4 bottleneck intelligence
    bottlenecked: bool
    bottleneck_reason_codes: tuple[str, ...]

    # Phase 61.5 escalation intelligence
    escalation_recommendation: WorkflowEscalationRecommendation
    escalation_reason_codes: tuple[str, ...]
    escalation_requires_human_review: bool

    # Phase 61.6 dependency intelligence
    dependency_state: WorkflowDependencyState
    dependency_reason_codes: tuple[str, ...]
    dependency_target_type: str | None
    dependency_target_id: int | None


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------


def _ensure_aware(value: datetime) -> datetime:
    """
    Normalize a datetime to timezone-aware UTC.

    Naive datetimes are treated as UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)

    return value.astimezone(timezone.utc)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _elapsed_seconds(start: datetime, end: datetime) -> float:
    """
    Return a non-negative elapsed duration in seconds.
    """
    return max(
        0.0,
        (_ensure_aware(end) - _ensure_aware(start)).total_seconds(),
    )


# ---------------------------------------------------------------------------
# Workflow reference time
# ---------------------------------------------------------------------------


def _workflow_reference_time(
    workflow: RiskResponseWorkflowRecord,
) -> datetime:
    """
    Determine the timestamp from which workflow age is calculated.

    Preference:
    1. started_at
    2. created_at
    """
    if workflow.started_at is not None:
        return _ensure_aware(workflow.started_at)

    return _ensure_aware(workflow.created_at)


# ---------------------------------------------------------------------------
# Workflow age
# ---------------------------------------------------------------------------


def calculate_workflow_age(
    workflow: RiskResponseWorkflowRecord,
    *,
    now: datetime | None = None,
) -> tuple[float, float]:
    """
    Calculate workflow age in days and seconds.

    Age is measured from:
    - started_at when available;
    - otherwise created_at.

    Terminal workflows are measured until their terminal timestamp
    when available.
    """
    current_time = _ensure_aware(now or _now_utc())

    reference_time = _workflow_reference_time(workflow)

    if workflow.completed_at is not None:
        end_time = _ensure_aware(workflow.completed_at)
    elif workflow.cancelled_at is not None:
        end_time = _ensure_aware(workflow.cancelled_at)
    else:
        end_time = current_time

    age_seconds = _elapsed_seconds(reference_time, end_time)

    return age_seconds / 86400.0, age_seconds


# ---------------------------------------------------------------------------
# Lifecycle timing
# ---------------------------------------------------------------------------


def calculate_workflow_lifecycle_timing(
    workflow: RiskResponseWorkflowRecord,
    *,
    now: datetime | None = None,
) -> tuple[
    float | None,
    float | None,
    float,
    float | None,
]:
    """
    Calculate workflow lifecycle timing.

    Returns:
        (
            time_to_start_seconds,
            time_in_progress_seconds,
            lifecycle_duration_seconds,
            terminal_age_seconds,
        )

    Semantics:

    time_to_start_seconds
        None when the workflow has not started.

    time_in_progress_seconds
        None when the workflow has not started.

    lifecycle_duration_seconds
        Total lifecycle duration from creation to terminal/current time.

    terminal_age_seconds
        None for non-terminal workflows.
    """
    current_time = _ensure_aware(now or _now_utc())

    created_at = _ensure_aware(workflow.created_at)

    terminal_timestamp: datetime | None = None

    if workflow.completed_at is not None:
        terminal_timestamp = _ensure_aware(workflow.completed_at)
    elif workflow.cancelled_at is not None:
        terminal_timestamp = _ensure_aware(workflow.cancelled_at)

    lifecycle_end = terminal_timestamp or current_time

    lifecycle_duration_seconds = _elapsed_seconds(
        created_at,
        lifecycle_end,
    )

    if workflow.started_at is None:
        time_to_start_seconds = None
        time_in_progress_seconds = None
    else:
        started_at = _ensure_aware(workflow.started_at)

        time_to_start_seconds = _elapsed_seconds(
            created_at,
            started_at,
        )

        time_in_progress_seconds = _elapsed_seconds(
            started_at,
            lifecycle_end,
        )

    if terminal_timestamp is None:
        terminal_age_seconds = None
    else:
        terminal_age_seconds = _elapsed_seconds(
            terminal_timestamp,
            current_time,
        )

    return (
        time_to_start_seconds,
        time_in_progress_seconds,
        lifecycle_duration_seconds,
        terminal_age_seconds,
    )


# ---------------------------------------------------------------------------
# Workflow health
# ---------------------------------------------------------------------------


def derive_workflow_health(
    workflow: RiskResponseWorkflowRecord,
    *,
    now: datetime | None = None,
    age_days: float | None = None,
) -> tuple[WorkflowHealth, tuple[str, ...], bool]:
    """
    Derive deterministic workflow health.

    Terminal states take precedence over ageing/overdue states.

    The return order intentionally preserves the Phase 61.1 contract:

        health, reason_codes, attention_required
    """
    status = str(workflow.status).upper()

    if status == "COMPLETED":
        return (
            WorkflowHealth.COMPLETED,
            (WorkflowIntelligenceReason.WORKFLOW_COMPLETED.value,),
            False,
        )

    if status == "CANCELLED":
        return (
            WorkflowHealth.CANCELLED,
            (WorkflowIntelligenceReason.WORKFLOW_CANCELLED.value,),
            False,
        )

    if age_days is None:
        age_days, _ = calculate_workflow_age(
            workflow,
            now=now,
        )

    if age_days >= WORKFLOW_OVERDUE_DAYS:
        return (
            WorkflowHealth.OVERDUE,
            (WorkflowIntelligenceReason.WORKFLOW_OVERDUE.value,),
            True,
        )

    if age_days >= WORKFLOW_AGING_DAYS:
        return (
            WorkflowHealth.AGING,
            (WorkflowIntelligenceReason.WORKFLOW_AGING.value,),
            True,
        )

    return (
        WorkflowHealth.HEALTHY,
        (WorkflowIntelligenceReason.WORKFLOW_CURRENT.value,),
        False,
    )


# ---------------------------------------------------------------------------
# Priority normalization
# ---------------------------------------------------------------------------


def normalize_workflow_priority(
    workflow: RiskResponseWorkflowRecord,
) -> RiskResponsePriority:
    """
    Resolve the canonical priority from the associated governed decision.

    The governed decision remains the authoritative source of workflow
    priority.

    This helper intentionally raises when decision information is missing
    because callers explicitly requesting priority intelligence must have
    the governed decision available.
    """
    decision = workflow.decision

    if decision is None:
        raise ValueError(
            "Workflow priority intelligence requires its associated "
            "response decision."
        )

    raw_priority = getattr(decision, "priority", None)

    if raw_priority is None:
        raise ValueError("priority cannot be null")

    if isinstance(raw_priority, RiskResponsePriority):
        return raw_priority

    try:
        return RiskResponsePriority(str(raw_priority))
    except ValueError as exc:
        raise ValueError(
            f"Unsupported workflow decision priority: {raw_priority}"
        ) from exc


# ---------------------------------------------------------------------------
# Priority intelligence
# ---------------------------------------------------------------------------


def derive_workflow_priority(
    workflow: RiskResponseWorkflowRecord,
) -> tuple[
    RiskResponsePriority,
    int,
    str,
    bool,
    tuple[str, ...],
]:
    """
    Derive deterministic workflow priority intelligence.

    Returns:
        (
            decision_priority,
            priority_rank,
            governance_level,
            priority_requires_attention,
            priority_reason_codes,
        )
    """
    decision = workflow.decision

    if decision is None:
        raise ValueError(
            "Workflow priority intelligence requires its associated "
            "response decision."
        )

    priority = normalize_workflow_priority(workflow)

    priority_rank = WORKFLOW_PRIORITY_RANK[priority]

    governance_level = str(
        getattr(decision, "governance_level", "")
    )

    priority_requires_attention = priority in {
        RiskResponsePriority.HIGH,
        RiskResponsePriority.CRITICAL,
    }

    reason_codes = [
        WorkflowPriorityReason.DECISION_PRIORITY.value,
    ]

    if priority_requires_attention:
        reason_codes.append(
            WorkflowPriorityReason.PRIORITY_REQUIRES_ATTENTION.value
        )

    return (
        priority,
        priority_rank,
        governance_level,
        priority_requires_attention,
        tuple(reason_codes),
    )


# ---------------------------------------------------------------------------
# Bottleneck intelligence
# ---------------------------------------------------------------------------


def derive_workflow_bottleneck(
    workflow: RiskResponseWorkflowRecord,
    *,
    age_days: float | None = None,
    now: datetime | None = None,
) -> tuple[bool, tuple[str, ...]]:
    """
    Derive deterministic workflow bottleneck intelligence.

    Bottleneck detection uses the supplied workflow age when available.

    Rules:

    COMPLETED / CANCELLED
        Never bottlenecked.

    OPEN
        Aged/overdue workflows are considered bottlenecked because
        they have not started.

    IN_PROGRESS
        Aged/overdue workflows are considered bottlenecked because
        active processing has remained unresolved.

    Other non-terminal states
        Use the same ageing/overdue thresholds conservatively.

    The ageing and overdue thresholds are inclusive.

    This function never mutates the workflow.
    """
    status = str(workflow.status).upper()

    if status in {"COMPLETED", "CANCELLED"}:
        return (
            False,
            (WorkflowBottleneckReason.BOTTLENECK_TERMINAL.value,),
        )

    if age_days is None:
        current_time = _ensure_aware(now or _now_utc())

        age_days = calculate_workflow_age(
            workflow,
            now=current_time,
        )[0]

    if age_days >= WORKFLOW_OVERDUE_DAYS:
        if status == "OPEN":
            return (
                True,
                (
                    WorkflowBottleneckReason.BOTTLENECK_NOT_STARTED.value,
                    WorkflowBottleneckReason.BOTTLENECK_OVERDUE.value,
                ),
            )

        if status == "IN_PROGRESS":
            return (
                True,
                (
                    WorkflowBottleneckReason.BOTTLENECK_IN_PROGRESS.value,
                    WorkflowBottleneckReason.BOTTLENECK_OVERDUE.value,
                ),
            )

        return (
            True,
            (WorkflowBottleneckReason.BOTTLENECK_OVERDUE.value,),
        )

    if age_days >= WORKFLOW_AGING_DAYS:
        if status == "OPEN":
            return (
                True,
                (
                    WorkflowBottleneckReason.BOTTLENECK_NOT_STARTED.value,
                    WorkflowBottleneckReason.BOTTLENECK_AGING.value,
                ),
            )

        if status == "IN_PROGRESS":
            return (
                True,
                (
                    WorkflowBottleneckReason.BOTTLENECK_IN_PROGRESS.value,
                    WorkflowBottleneckReason.BOTTLENECK_AGING.value,
                ),
            )

        return (
            True,
            (WorkflowBottleneckReason.BOTTLENECK_AGING.value,),
        )

    return (
        False,
        (WorkflowBottleneckReason.BOTTLENECK_NONE.value,),
    )


# ---------------------------------------------------------------------------
# Escalation intelligence
# ---------------------------------------------------------------------------


def derive_workflow_escalation(
    workflow: RiskResponseWorkflowRecord,
    *,
    health: WorkflowHealth,
    attention_required: bool,
    decision_priority: RiskResponsePriority | None,
    priority_requires_attention: bool,
    bottlenecked: bool,
) -> tuple[
    WorkflowEscalationRecommendation,
    tuple[str, ...],
    bool,
]:
    """
    Derive a deterministic escalation recommendation.

    This function does not perform escalation.

    Returns:
        (
            escalation_recommendation,
            escalation_reason_codes,
            escalation_requires_human_review,
        )

    Escalation recommendations are deliberately conservative:

    - terminal workflows receive no escalation recommendation;
    - critical priority receives an escalation recommendation;
    - high/critical priority combined with a meaningful bottleneck
      receives an escalation recommendation;
    - overdue workflows receive an escalation recommendation;
    - ageing workflows requiring attention receive a review
      recommendation.

    Any ESCALATE recommendation requires human review.
    """
    status = str(workflow.status).upper()

    if status in {"COMPLETED", "CANCELLED"}:
        return (
            WorkflowEscalationRecommendation.NONE,
            (WorkflowEscalationReason.NO_ESCALATION.value,),
            False,
        )

    if decision_priority == RiskResponsePriority.CRITICAL:
        return (
            WorkflowEscalationRecommendation.ESCALATE,
            (WorkflowEscalationReason.CRITICAL_PRIORITY.value,),
            True,
        )

    if health == WorkflowHealth.OVERDUE:
        return (
            WorkflowEscalationRecommendation.ESCALATE,
            (WorkflowEscalationReason.OVERDUE_WORKFLOW.value,),
            True,
        )

    if (
        bottlenecked
        and status == "IN_PROGRESS"
        and decision_priority == RiskResponsePriority.HIGH
    ):
        return (
            WorkflowEscalationRecommendation.ESCALATE,
            (WorkflowEscalationReason.HIGH_PRIORITY_BOTTLENECK.value,),
            True,
        )

    if (
        health == WorkflowHealth.AGING
        and attention_required
        and priority_requires_attention
    ):
        return (
            WorkflowEscalationRecommendation.REVIEW,
            (
                WorkflowEscalationReason.AGING_WORKFLOW_REQUIRES_ATTENTION.value,
            ),
            True,
        )

    return (
        WorkflowEscalationRecommendation.NONE,
        (WorkflowEscalationReason.NO_ESCALATION.value,),
        False,
    )


# ---------------------------------------------------------------------------
# Dependency intelligence
# ---------------------------------------------------------------------------


def derive_workflow_dependency(
    workflow: RiskResponseWorkflowRecord,
) -> tuple[
    WorkflowDependencyState,
    tuple[str, ...],
    str | None,
    int | None,
]:
    """
    Derive deterministic dependency intelligence from the workflow target.

    Phase 61.6 deliberately treats the governed workflow target as the
    dependency boundary.

    This function is read-only and does not query or mutate the underlying
    GRC resource.

    The workflow target is classified using the information already stored
    on the workflow record:

    - no target type/id -> NO_DEPENDENCY
    - target type + target id -> AVAILABLE

    More detailed resource-state intelligence is intentionally deferred
    until the intelligence layer has an explicit resource context.

    Returns:
        (
            dependency_state,
            dependency_reason_codes,
            dependency_target_type,
            dependency_target_id,
        )
    """
    target_type = getattr(workflow, "target_type", None)
    target_id = getattr(workflow, "target_id", None)

    normalized_target_type = (
        str(target_type).strip().upper()
        if target_type is not None
        else None
    )

    if not normalized_target_type or target_id is None:
        return (
            WorkflowDependencyState.NO_DEPENDENCY,
            (
                WorkflowDependencyReason.NO_DEPENDENCY.value,
            ),
            normalized_target_type,
            target_id,
        )

    return (
        WorkflowDependencyState.AVAILABLE,
        (
            WorkflowDependencyReason.TARGET_RESOURCE_AVAILABLE.value,
        ),
        normalized_target_type,
        target_id,
    )


# ---------------------------------------------------------------------------
# Complete workflow intelligence
# ---------------------------------------------------------------------------


def get_workflow_intelligence(
    workflow: RiskResponseWorkflowRecord,
    *,
    now: datetime | None = None,
) -> RiskResponseWorkflowIntelligence:
    """
    Build complete deterministic workflow intelligence.

    Priority intelligence is included when the associated governed
    decision is loaded/present.

    Basic health and lifecycle intelligence remains available even when
    the decision relationship is unavailable.
    """
    age_days, age_seconds = calculate_workflow_age(
        workflow,
        now=now,
    )

    (
        time_to_start_seconds,
        time_in_progress_seconds,
        lifecycle_duration_seconds,
        terminal_age_seconds,
    ) = calculate_workflow_lifecycle_timing(
        workflow,
        now=now,
    )

    (
        health,
        reason_codes,
        attention_required,
    ) = derive_workflow_health(
        workflow,
        now=now,
        age_days=age_days,
    )

    decision_priority: RiskResponsePriority | None = None
    priority_rank: int | None = None
    governance_level: str | None = None
    priority_requires_attention = False
    priority_reason_codes: tuple[str, ...] = ()

    if workflow.decision is not None:
        (
            decision_priority,
            priority_rank,
            governance_level,
            priority_requires_attention,
            priority_reason_codes,
        ) = derive_workflow_priority(workflow)

    if workflow.completed_at is not None or workflow.cancelled_at is not None:
        bottleneck_age_days = age_days
    else:
        current_time = _ensure_aware(now or _now_utc())
        bottleneck_age_days = (
            _elapsed_seconds(
                _ensure_aware(workflow.created_at),
                current_time,
            )
            / 86400.0
        )

    (
        bottlenecked,
        bottleneck_reason_codes,
    ) = derive_workflow_bottleneck(
        workflow,
        age_days=bottleneck_age_days,
        now=now,
    )

    (
        escalation_recommendation,
        escalation_reason_codes,
        escalation_requires_human_review,
    ) = derive_workflow_escalation(
        workflow,
        health=health,
        attention_required=attention_required,
        decision_priority=decision_priority,
        priority_requires_attention=priority_requires_attention,
        bottlenecked=bottlenecked,
    )

    (
        dependency_state,
        dependency_reason_codes,
        dependency_target_type,
        dependency_target_id,
    ) = derive_workflow_dependency(workflow)

    status = str(workflow.status).upper()

    return RiskResponseWorkflowIntelligence(
        workflow_id=workflow.id,
        risk_id=workflow.risk_id,
        status=status,
        health=health,
        age_days=age_days,
        age_seconds=age_seconds,
        attention_required=attention_required,
        reason_codes=reason_codes,
        started=workflow.started_at is not None,
        terminal=status in {"COMPLETED", "CANCELLED"},
        time_to_start_seconds=time_to_start_seconds,
        time_in_progress_seconds=time_in_progress_seconds,
        lifecycle_duration_seconds=lifecycle_duration_seconds,
        terminal_age_seconds=terminal_age_seconds,
        decision_priority=decision_priority,
        priority_rank=priority_rank,
        governance_level=governance_level,
        priority_requires_attention=priority_requires_attention,
        priority_reason_codes=priority_reason_codes,
        bottlenecked=bottlenecked,
        bottleneck_reason_codes=bottleneck_reason_codes,
        escalation_recommendation=escalation_recommendation,
        escalation_reason_codes=escalation_reason_codes,
        escalation_requires_human_review=(
            escalation_requires_human_review
        ),
        dependency_state=dependency_state,
        dependency_reason_codes=dependency_reason_codes,
        dependency_target_type=dependency_target_type,
        dependency_target_id=dependency_target_id,
    )