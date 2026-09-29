"""
Continuous Risk Response Service

Phase 57
--------

Deterministic response orchestration derived from the Phase 56
continuous risk state.

This service intentionally does NOT:
- modify Risk records
- modify RiskTreatment records
- create corrective actions automatically
- send notifications automatically
- make AI decisions
- bypass RBAC / visibility

It determines what response should be considered next based on the
authoritative Phase 56 risk state and reason codes.

High-impact decisions such as REASSESS_RISK and ESCALATE require
human approval.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.services.continuous_risk_state_service import (
    ContinuousRiskState,
    RiskState,
    RiskStateReason,
    RiskStateReasonDetail,
    get_continuous_risk_state,
)


# ============================================================
# Response definitions
# ============================================================


class RiskResponseDecision(str, Enum):
    MONITOR = "MONITOR"
    REVIEW = "REVIEW"
    REASSESS_RISK = "REASSESS_RISK"
    UPDATE_TREATMENT = "UPDATE_TREATMENT"
    CORRECTIVE_ACTION_REVIEW = "CORRECTIVE_ACTION_REVIEW"
    CONTROL_REVIEW = "CONTROL_REVIEW"
    EVIDENCE_REVIEW = "EVIDENCE_REVIEW"
    ESCALATE = "ESCALATE"


class RiskResponsePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class RiskResponseAction:
    decision: RiskResponseDecision
    priority: RiskResponsePriority
    reason_codes: tuple[str, ...]
    human_approval_required: bool


@dataclass(frozen=True)
class ContinuousRiskResponse:
    risk_id: int
    risk_state: str
    treatment_state: str
    reassessment_required: bool
    response_required: bool
    priority: RiskResponsePriority
    decisions: tuple[RiskResponseAction, ...]
    human_approval_required: bool
    reasons: tuple[RiskStateReasonDetail, ...]


# ============================================================
# Decision priorities
# ============================================================


_DECISION_PRIORITY = {
    RiskResponseDecision.MONITOR: RiskResponsePriority.LOW,
    RiskResponseDecision.REVIEW: RiskResponsePriority.MEDIUM,
    RiskResponseDecision.EVIDENCE_REVIEW: RiskResponsePriority.MEDIUM,
    RiskResponseDecision.UPDATE_TREATMENT: RiskResponsePriority.MEDIUM,
    RiskResponseDecision.CONTROL_REVIEW: RiskResponsePriority.HIGH,
    RiskResponseDecision.CORRECTIVE_ACTION_REVIEW: RiskResponsePriority.HIGH,
    RiskResponseDecision.REASSESS_RISK: RiskResponsePriority.HIGH,
    RiskResponseDecision.ESCALATE: RiskResponsePriority.CRITICAL,
}


# ============================================================
# Reason -> response mapping
# ============================================================


def _decision_for_reason(
    reason_code: RiskStateReason,
) -> RiskResponseDecision | None:
    mapping = {
        RiskStateReason.OPEN_CRITICAL_FINDING: (
            RiskResponseDecision.ESCALATE
        ),
        RiskStateReason.CRITICAL_CORRECTIVE_ACTION_OPEN: (
            RiskResponseDecision.ESCALATE
        ),
        RiskStateReason.OPEN_HIGH_FINDING: (
            RiskResponseDecision.REVIEW
        ),
        RiskStateReason.OVERDUE_CORRECTIVE_ACTION: (
            RiskResponseDecision.CORRECTIVE_ACTION_REVIEW
        ),
        RiskStateReason.CONTROL_INACTIVE: (
            RiskResponseDecision.CONTROL_REVIEW
        ),
        RiskStateReason.CONTROL_EFFECTIVENESS_LOW: (
            RiskResponseDecision.CONTROL_REVIEW
        ),
        RiskStateReason.STALE_EVIDENCE: (
            RiskResponseDecision.EVIDENCE_REVIEW
        ),
        RiskStateReason.MISSING_SUPPORTING_EVIDENCE: (
            RiskResponseDecision.EVIDENCE_REVIEW
        ),
        RiskStateReason.OVERDUE_TREATMENT: (
            RiskResponseDecision.UPDATE_TREATMENT
        ),
        RiskStateReason.TREATMENT_CANCELLED: (
            RiskResponseDecision.REASSESS_RISK
        ),
        RiskStateReason.TREATMENT_MISSING_RESIDUAL: (
            RiskResponseDecision.REASSESS_RISK
        ),
        RiskStateReason.ELEVATED_RESIDUAL_RISK: (
            RiskResponseDecision.REASSESS_RISK
        ),
    }

    return mapping.get(reason_code)


# ============================================================
# State-based fallback
# ============================================================


def _priority_for_state(
    state: ContinuousRiskState,
) -> RiskResponsePriority:
    if state.risk_state == RiskState.REASSESSMENT_REQUIRED:
        return RiskResponsePriority.HIGH

    if state.risk_state == RiskState.DEGRADED:
        return RiskResponsePriority.MEDIUM

    return RiskResponsePriority.LOW


def _priority_rank(
    priority: RiskResponsePriority,
) -> int:
    return {
        RiskResponsePriority.LOW: 1,
        RiskResponsePriority.MEDIUM: 2,
        RiskResponsePriority.HIGH: 3,
        RiskResponsePriority.CRITICAL: 4,
    }[priority]


def _max_priority(
    priorities: list[RiskResponsePriority],
) -> RiskResponsePriority:
    if not priorities:
        return RiskResponsePriority.LOW

    return max(
        priorities,
        key=_priority_rank,
    )


# ============================================================
# Action construction
# ============================================================


def _build_actions(
    state: ContinuousRiskState,
) -> tuple[RiskResponseAction, ...]:
    grouped: dict[RiskResponseDecision, list[str]] = {}

    for reason in state.reasons:
        decision = _decision_for_reason(reason.code)

        if decision is None:
            continue

        grouped.setdefault(decision, []).append(
            reason.code.value
        )

    # --------------------------------------------------------
    # No explicit response reason
    # --------------------------------------------------------

    if not grouped:
        if state.risk_state == RiskState.CURRENT:
            return (
                RiskResponseAction(
                    decision=RiskResponseDecision.MONITOR,
                    priority=RiskResponsePriority.LOW,
                    reason_codes=(),
                    human_approval_required=False,
                ),
            )

        if state.risk_state == RiskState.DEGRADED:
            return (
                RiskResponseAction(
                    decision=RiskResponseDecision.REVIEW,
                    priority=RiskResponsePriority.MEDIUM,
                    reason_codes=(),
                    human_approval_required=False,
                ),
            )

        return (
            RiskResponseAction(
                decision=RiskResponseDecision.REASSESS_RISK,
                priority=RiskResponsePriority.HIGH,
                reason_codes=(),
                human_approval_required=True,
            ),
        )

    # --------------------------------------------------------
    # Build one action per decision category
    # --------------------------------------------------------

    actions: list[RiskResponseAction] = []

    for decision, reason_codes in grouped.items():
        priority = _DECISION_PRIORITY[decision]

        human_approval_required = decision in {
            RiskResponseDecision.ESCALATE,
            RiskResponseDecision.REASSESS_RISK,
        }

        actions.append(
            RiskResponseAction(
                decision=decision,
                priority=priority,
                reason_codes=tuple(
                    sorted(set(reason_codes))
                ),
                human_approval_required=(
                    human_approval_required
                ),
            )
        )

    # Highest priority first, deterministic ordering for ties.
    return tuple(
        sorted(
            actions,
            key=lambda action: (
                -_priority_rank(action.priority),
                action.decision.value,
            ),
        )
    )


# ============================================================
# Main response builder
# ============================================================


def build_continuous_risk_response(
    state: ContinuousRiskState,
) -> ContinuousRiskResponse:
    actions = _build_actions(state)

    priority = _max_priority(
        [action.priority for action in actions]
    )

    response_required = any(
        action.decision != RiskResponseDecision.MONITOR
        for action in actions
    )

    human_approval_required = any(
        action.human_approval_required
        for action in actions
    )

    # State can theoretically provide a higher priority than
    # an individual reason mapping. Preserve that state-derived
    # priority without changing the decision semantics.
    state_priority = _priority_for_state(state)

    priority = _max_priority(
        [
            priority,
            state_priority,
        ]
    )

    return ContinuousRiskResponse(
        risk_id=state.risk_id,
        risk_state=state.risk_state.value,
        treatment_state=state.treatment_state.value,
        reassessment_required=state.reassessment_required,
        response_required=response_required,
        priority=priority,
        decisions=actions,
        human_approval_required=(
            human_approval_required
        ),
        reasons=tuple(state.reasons),
    )


# ============================================================
# Database helper
# ============================================================


def get_continuous_risk_response(
    db: Session,
    risk: Risk,
    current_user=None,
) -> ContinuousRiskResponse:
    """
    Calculate the current deterministic response for a risk.

    Visibility remains owned by Phase 56 through the current_user
    passed into get_continuous_risk_state().
    """

    state = get_continuous_risk_state(
        db,
        risk,
        current_user=current_user,
    )

    return build_continuous_risk_response(state)