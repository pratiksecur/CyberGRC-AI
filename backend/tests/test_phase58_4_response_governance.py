from types import SimpleNamespace

from app.services.continuous_risk_response_notification_service import (
    ResponseGovernanceLevel,
    get_response_governance_level,
    is_human_approval_decision,
)
from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
    RiskResponsePriority,
)


def _response(
    *,
    response_required=True,
    human_approval_required=False,
    decisions=(),
):
    return ContinuousRiskResponse(
        risk_id=1,
        risk_state="DEGRADED",
        treatment_state="CURRENT",
        reassessment_required=False,
        response_required=response_required,
        priority=RiskResponsePriority.MEDIUM,
        decisions=tuple(decisions),
        human_approval_required=human_approval_required,
        reasons=(),
    )


def _action(
    decision,
    *,
    priority=RiskResponsePriority.MEDIUM,
    approval=False,
):
    return RiskResponseAction(
        decision=decision,
        priority=priority,
        reason_codes=("TEST_REASON",),
        human_approval_required=approval,
    )


# ============================================================
# Human approval classification
# ============================================================


def test_reassess_risk_requires_human_approval():
    assert (
        is_human_approval_decision(
            RiskResponseDecision.REASSESS_RISK
        )
        is True
    )


def test_escalate_requires_human_approval():
    assert (
        is_human_approval_decision(
            RiskResponseDecision.ESCALATE
        )
        is True
    )


def test_monitor_does_not_require_human_approval():
    assert (
        is_human_approval_decision(
            RiskResponseDecision.MONITOR
        )
        is False
    )


def test_review_does_not_require_human_approval():
    assert (
        is_human_approval_decision(
            RiskResponseDecision.REVIEW
        )
        is False
    )


# ============================================================
# Governance classification
# ============================================================


def test_monitor_is_informational():
    response = _response(
        response_required=False,
        decisions=(
            _action(
                RiskResponseDecision.MONITOR,
                priority=RiskResponsePriority.LOW,
            ),
        ),
    )

    assert (
        get_response_governance_level(response)
        == ResponseGovernanceLevel.INFORMATIONAL
    )


def test_review_is_governed_action():
    response = _response(
        response_required=True,
        decisions=(
            _action(
                RiskResponseDecision.REVIEW
            ),
        ),
    )

    assert (
        get_response_governance_level(response)
        == ResponseGovernanceLevel.GOVERNED_ACTION
    )


def test_reassessment_is_human_approval_required():
    response = _response(
        response_required=True,
        human_approval_required=True,
        decisions=(
            _action(
                RiskResponseDecision.REASSESS_RISK,
                priority=RiskResponsePriority.HIGH,
                approval=True,
            ),
        ),
    )

    assert (
        get_response_governance_level(response)
        == ResponseGovernanceLevel.HUMAN_APPROVAL_REQUIRED
    )


def test_escalation_has_highest_governance_level():
    response = _response(
        response_required=True,
        human_approval_required=True,
        decisions=(
            _action(
                RiskResponseDecision.REVIEW
            ),
            _action(
                RiskResponseDecision.ESCALATE,
                priority=RiskResponsePriority.CRITICAL,
                approval=True,
            ),
        ),
    )

    assert (
        get_response_governance_level(response)
        == ResponseGovernanceLevel.ESCALATION
    )


def test_escalation_wins_over_reassessment():
    response = _response(
        response_required=True,
        human_approval_required=True,
        decisions=(
            _action(
                RiskResponseDecision.REASSESS_RISK,
                priority=RiskResponsePriority.HIGH,
                approval=True,
            ),
            _action(
                RiskResponseDecision.ESCALATE,
                priority=RiskResponsePriority.CRITICAL,
                approval=True,
            ),
        ),
    )

    assert (
        get_response_governance_level(response)
        == ResponseGovernanceLevel.ESCALATION
    )


def test_governance_classification_does_not_change_response():
    response = _response(
        response_required=True,
        human_approval_required=True,
        decisions=(
            _action(
                RiskResponseDecision.REASSESS_RISK,
                priority=RiskResponsePriority.HIGH,
                approval=True,
            ),
        ),
    )

    original_decisions = response.decisions

    get_response_governance_level(response)

    assert response.decisions == original_decisions
    assert response.response_required is True
    assert response.human_approval_required is True


# ============================================================
# Human approval cannot be silently removed
# ============================================================


def test_response_level_approval_flag_forces_governance():
    response = _response(
        response_required=True,
        human_approval_required=True,
        decisions=(
            _action(
                RiskResponseDecision.REVIEW,
                approval=False,
            ),
        ),
    )

    assert (
        get_response_governance_level(response)
        == ResponseGovernanceLevel.HUMAN_APPROVAL_REQUIRED
    )