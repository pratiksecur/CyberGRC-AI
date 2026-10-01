"""
Continuous Risk Response Notification Service

Phase 58.4
-----------

Connects the deterministic Phase 57 continuous risk response
engine to the existing notification infrastructure and makes
the governance boundary explicit.

Governance principles:

- The Phase 57 response engine remains authoritative.
- Notifications communicate deterministic response posture.
- Human approval remains mandatory for high-impact decisions.
- ESCALATE identifies a governed escalation requirement; it
  does not execute escalation automatically.
- REASSESS_RISK identifies a governed reassessment requirement;
  it does not perform reassessment automatically.
- Existing risk-owner and management-chain recipient resolution
  is reused.
- No new persistence model is introduced.
- No notification is generated for MONITOR.
- Notification creation remains transaction-boundary neutral.
"""

from __future__ import annotations

from enum import Enum

from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
    RiskResponsePriority,
    get_continuous_risk_response,
)
from app.services.notification_recipient_service import (
    get_risk_recipients,
)
from app.services.notification_service import (
    _create_for_recipients,
)


# ============================================================
# Notification constants
# ============================================================


RESPONSE_NOTIFICATION_TYPE = (
    "continuous_risk_response"
)

RESPONSE_SOURCE_TYPE = (
    "continuous_risk_response"
)


# ============================================================
# Governance classification
# ============================================================


class ResponseGovernanceLevel(str, Enum):
    """
    Governance classification for a deterministic response.

    These values describe how the response should be governed.
    They do not execute the response.
    """

    INFORMATIONAL = "INFORMATIONAL"
    GOVERNED_ACTION = "GOVERNED_ACTION"
    HUMAN_APPROVAL_REQUIRED = "HUMAN_APPROVAL_REQUIRED"
    ESCALATION = "ESCALATION"


# High-impact decisions remain explicitly human-controlled.
_HUMAN_APPROVAL_DECISIONS = {
    RiskResponseDecision.REASSESS_RISK,
    RiskResponseDecision.ESCALATE,
}


# ============================================================
# Decision labels
# ============================================================


_DECISION_LABELS = {
    RiskResponseDecision.MONITOR: "Monitor",
    RiskResponseDecision.REVIEW: "Review",
    RiskResponseDecision.REASSESS_RISK: "Reassess Risk",
    RiskResponseDecision.UPDATE_TREATMENT: "Update Treatment",
    RiskResponseDecision.CORRECTIVE_ACTION_REVIEW: (
        "Corrective Action Review"
    ),
    RiskResponseDecision.CONTROL_REVIEW: "Control Review",
    RiskResponseDecision.EVIDENCE_REVIEW: "Evidence Review",
    RiskResponseDecision.ESCALATE: "Escalate",
}


_PRIORITY_LABELS = {
    RiskResponsePriority.LOW: "Low",
    RiskResponsePriority.MEDIUM: "Medium",
    RiskResponsePriority.HIGH: "High",
    RiskResponsePriority.CRITICAL: "Critical",
}


# ============================================================
# Internal helpers
# ============================================================


def _decision_label(
    decision: RiskResponseDecision,
) -> str:
    return _DECISION_LABELS.get(
        decision,
        decision.value.replace("_", " ").title(),
    )


def _priority_label(
    priority: RiskResponsePriority,
) -> str:
    return _PRIORITY_LABELS.get(
        priority,
        priority.value.title(),
    )


def _primary_decision(
    response: ContinuousRiskResponse,
) -> RiskResponseAction | None:
    """
    Return the highest-priority response action.

    The result is calculated from the action set rather than
    relying on list position.
    """

    if not response.decisions:
        return None

    priority_rank = {
        RiskResponsePriority.LOW: 1,
        RiskResponsePriority.MEDIUM: 2,
        RiskResponsePriority.HIGH: 3,
        RiskResponsePriority.CRITICAL: 4,
    }

    return max(
        response.decisions,
        key=lambda action: (
            priority_rank[action.priority],
            action.decision.value,
        ),
    )


# ============================================================
# Governance helpers
# ============================================================


def is_human_approval_decision(
    decision: RiskResponseDecision,
) -> bool:
    """
    Return whether a response decision is explicitly
    high-impact and therefore requires human approval.

    This is a governance classification only.

    It does not execute or approve the decision.
    """

    return decision in _HUMAN_APPROVAL_DECISIONS


def get_response_governance_level(
    response: ContinuousRiskResponse,
) -> ResponseGovernanceLevel:
    """
    Determine the governance level of the current response.

    Priority:

    1. ESCALATE
    2. Human approval required
    3. Governed action
    4. Informational

    The response engine remains authoritative for the actual
    decision. This helper only classifies the required governance
    boundary.
    """

    decisions = {
        action.decision
        for action in response.decisions
    }

    if RiskResponseDecision.ESCALATE in decisions:
        return ResponseGovernanceLevel.ESCALATION

    if (
        response.human_approval_required
        or any(
            is_human_approval_decision(action.decision)
            for action in response.decisions
        )
    ):
        return ResponseGovernanceLevel.HUMAN_APPROVAL_REQUIRED

    if response.response_required:
        return ResponseGovernanceLevel.GOVERNED_ACTION

    return ResponseGovernanceLevel.INFORMATIONAL


def _governance_message(
    response: ContinuousRiskResponse,
) -> str:
    """
    Build deterministic governance wording.
    """

    governance = get_response_governance_level(
        response
    )

    if governance == ResponseGovernanceLevel.ESCALATION:
        return (
            "Governed escalation is required. "
            "Human approval is required before escalation action."
        )

    if governance == ResponseGovernanceLevel.HUMAN_APPROVAL_REQUIRED:
        return (
            "Human approval is required before the "
            "high-impact response is executed."
        )

    if governance == ResponseGovernanceLevel.GOVERNED_ACTION:
        return (
            "The response requires governed human follow-up."
        )

    return ""


# ============================================================
# Response signature / event identity
# ============================================================


def _build_response_signature(
    response: ContinuousRiskResponse,
) -> str:
    """
    Build a deterministic signature representing the current
    response posture.

    Governance classification is deliberately NOT stored
    separately in the event key because it is derived from the
    authoritative response decisions.
    """

    decision_parts: list[str] = []

    for action in response.decisions:

        reason_codes = ",".join(
            sorted(
                set(action.reason_codes)
            )
        )

        decision_parts.append(
            "|".join(
                [
                    action.decision.value,
                    (
                        action.priority.value
                        if hasattr(action.priority, "value")
                        else action.priority
                    ),
                    reason_codes,
                    str(
                        action.human_approval_required
                    ),
                ]
            )
        )

    decisions_signature = ";".join(
        sorted(decision_parts)
    )

    return "|".join(
        [
            response.risk_state,
            response.treatment_state,
            (
                response.priority.value
                if hasattr(response.priority, "value")
                else response.priority
            ),
            str(response.reassessment_required),
            str(response.human_approval_required),
            decisions_signature,
        ]
    )


def build_response_event_key(
    response: ContinuousRiskResponse,
) -> str:
    """
    Build the stable notification event key for a continuous
    risk response.
    """

    signature = _build_response_signature(
        response
    )

    return (
        f"risk:{response.risk_id}:"
        f"continuous-response:{signature}"
    )


# ============================================================
# Notification content
# ============================================================


def _build_notification_title(
    response: ContinuousRiskResponse,
) -> str:
    """
    Build a deterministic notification title.
    """

    governance = get_response_governance_level(
        response
    )

    if governance == ResponseGovernanceLevel.ESCALATION:
        return "Risk Response Requires Escalation"

    if governance == ResponseGovernanceLevel.HUMAN_APPROVAL_REQUIRED:
        return "Risk Response Requires Human Approval"

    if response.priority == RiskResponsePriority.CRITICAL:
        return "Critical Risk Response Required"

    if response.priority == RiskResponsePriority.HIGH:
        return "High-Priority Risk Response Required"

    return "Risk Response Requires Attention"


def _build_notification_message(
    risk: Risk,
    response: ContinuousRiskResponse,
) -> str:
    """
    Build a deterministic notification message.

    No AI-generated interpretation is used here.
    """

    primary = _primary_decision(
        response
    )

    if primary is None:
        decision_text = "Review"
    else:
        decision_text = _decision_label(
            primary.decision
        )

    priority_text = _priority_label(
        response.priority
    )

    governance_text = _governance_message(
        response
    )

    governance_suffix = (
        f" {governance_text}"
        if governance_text
        else ""
    )

    return (
        f"Risk '{risk.title}' requires a "
        f"{priority_text.lower()}-priority response. "
        f"Recommended response: {decision_text}. "
        f"Risk state: {response.risk_state}. "
        f"Treatment state: {response.treatment_state}."
        f"{governance_suffix}"
    )


# ============================================================
# Notification eligibility
# ============================================================


def should_notify_response(
    response: ContinuousRiskResponse,
) -> bool:
    """
    Determine whether the current response posture requires
    a notification.

    MONITOR remains informational and does not generate a
    notification.

    Every response_required posture requires attention.
    """

    return response.response_required


# ============================================================
# Main orchestration
# ============================================================


def notify_continuous_risk_response(
    db: Session,
    risk: Risk,
    current_user=None,
) -> ContinuousRiskResponse:
    """
    Evaluate the current continuous risk response and create
    a notification when required.

    The returned response is always the deterministic Phase 57
    response.

    The notification is only a communication side effect.

    This function intentionally does NOT:

    - approve a response
    - reassess a risk
    - modify treatment
    - modify controls
    - create corrective actions
    - execute escalation

    The caller owns transaction boundaries.
    """

    response = get_continuous_risk_response(
        db,
        risk,
        current_user=current_user,
    )

    if not should_notify_response(
        response
    ):
        return response

    recipients = get_risk_recipients(
        db,
        risk,
    )

    if not recipients:
        return response

    event_key = build_response_event_key(
        response
    )

    _create_for_recipients(
        db=db,
        recipients=recipients,
        notification_type=RESPONSE_NOTIFICATION_TYPE,
        title=_build_notification_title(
            response
        ),
        message=_build_notification_message(
            risk,
            response,
        ),
        source_type=RESPONSE_SOURCE_TYPE,
        source_id=risk.id,
        event_key=event_key,
    )

    return response