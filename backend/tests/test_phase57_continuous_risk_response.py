from types import SimpleNamespace

from app.services.continuous_risk_response_service import (
    RiskResponseDecision,
    RiskResponsePriority,
    build_continuous_risk_response,
)
from app.services.continuous_risk_state_service import (
    ContinuousRiskState,
    RiskState,
    RiskStateReason,
    RiskStateReasonDetail,
    TreatmentState,
)


def _reason(
    code: RiskStateReason,
    severity: str = "HIGH",
):
    return RiskStateReasonDetail(
        code=code,
        severity=severity,
        message=f"Test reason: {code.value}",
    )


def _state(
    *,
    risk_state: RiskState,
    treatment_state: TreatmentState = TreatmentState.CURRENT,
    reassessment_required: bool = False,
    reasons=None,
):
    return ContinuousRiskState(
        risk_id=1,
        risk_state=risk_state,
        treatment_state=treatment_state,
        reassessment_required=reassessment_required,
        residual_risk_score=None,
        selected_treatment_id=None,
        reasons=list(reasons or []),
    )


# ============================================================
# CURRENT
# ============================================================


def test_current_risk_defaults_to_monitor():
    state = _state(
        risk_state=RiskState.CURRENT,
    )

    response = build_continuous_risk_response(state)

    assert response.risk_state == "CURRENT"
    assert response.response_required is False
    assert response.priority == RiskResponsePriority.LOW
    assert response.human_approval_required is False

    assert len(response.decisions) == 1
    assert (
        response.decisions[0].decision
        == RiskResponseDecision.MONITOR
    )


# ============================================================
# DEGRADED
# ============================================================


def test_degraded_risk_defaults_to_review():
    state = _state(
        risk_state=RiskState.DEGRADED,
    )

    response = build_continuous_risk_response(state)

    assert response.risk_state == "DEGRADED"
    assert response.response_required is True
    assert response.priority == RiskResponsePriority.MEDIUM
    assert response.human_approval_required is False

    assert len(response.decisions) == 1
    assert (
        response.decisions[0].decision
        == RiskResponseDecision.REVIEW
    )


# ============================================================
# REASSESSMENT REQUIRED
# ============================================================


def test_reassessment_required_defaults_to_reassess():
    state = _state(
        risk_state=RiskState.REASSESSMENT_REQUIRED,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT,
        reassessment_required=True,
    )

    response = build_continuous_risk_response(state)

    assert response.risk_state == "REASSESSMENT_REQUIRED"
    assert response.response_required is True
    assert response.priority == RiskResponsePriority.HIGH
    assert response.human_approval_required is True

    assert len(response.decisions) == 1
    assert (
        response.decisions[0].decision
        == RiskResponseDecision.REASSESS_RISK
    )
    assert (
        response.decisions[0].human_approval_required
        is True
    )


# ============================================================
# CRITICAL FINDING
# ============================================================


def test_critical_finding_escalates():
    state = _state(
        risk_state=RiskState.REASSESSMENT_REQUIRED,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT,
        reassessment_required=True,
        reasons=[
            _reason(
                RiskStateReason.OPEN_CRITICAL_FINDING,
                "CRITICAL",
            )
        ],
    )

    response = build_continuous_risk_response(state)

    assert response.response_required is True
    assert response.priority == RiskResponsePriority.CRITICAL
    assert response.human_approval_required is True

    assert len(response.decisions) == 1

    action = response.decisions[0]

    assert action.decision == RiskResponseDecision.ESCALATE
    assert action.priority == RiskResponsePriority.CRITICAL
    assert action.human_approval_required is True
    assert action.reason_codes == (
        "OPEN_CRITICAL_FINDING",
    )


# ============================================================
# CRITICAL CORRECTIVE ACTION
# ============================================================


def test_critical_corrective_action_escalates():
    state = _state(
        risk_state=RiskState.REASSESSMENT_REQUIRED,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT,
        reassessment_required=True,
        reasons=[
            _reason(
                RiskStateReason.CRITICAL_CORRECTIVE_ACTION_OPEN,
                "CRITICAL",
            )
        ],
    )

    response = build_continuous_risk_response(state)

    assert response.priority == RiskResponsePriority.CRITICAL
    assert response.human_approval_required is True

    action = response.decisions[0]

    assert action.decision == RiskResponseDecision.ESCALATE
    assert action.reason_codes == (
        "CRITICAL_CORRECTIVE_ACTION_OPEN",
    )


# ============================================================
# CONTROL REVIEW
# ============================================================


def test_inactive_control_requires_control_review():
    state = _state(
        risk_state=RiskState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.CONTROL_INACTIVE,
            )
        ],
    )

    response = build_continuous_risk_response(state)

    assert response.priority == RiskResponsePriority.HIGH

    action = response.decisions[0]

    assert action.decision == RiskResponseDecision.CONTROL_REVIEW
    assert action.priority == RiskResponsePriority.HIGH
    assert action.human_approval_required is False


def test_low_control_effectiveness_requires_control_review():
    state = _state(
        risk_state=RiskState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.CONTROL_EFFECTIVENESS_LOW,
            )
        ],
    )

    response = build_continuous_risk_response(state)

    assert response.priority == RiskResponsePriority.HIGH

    action = response.decisions[0]

    assert action.decision == RiskResponseDecision.CONTROL_REVIEW


# ============================================================
# EVIDENCE REVIEW
# ============================================================


def test_stale_evidence_requires_evidence_review():
    state = _state(
        risk_state=RiskState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.STALE_EVIDENCE,
            )
        ],
    )

    response = build_continuous_risk_response(state)

    assert response.priority == RiskResponsePriority.MEDIUM

    action = response.decisions[0]

    assert action.decision == RiskResponseDecision.EVIDENCE_REVIEW


def test_missing_evidence_requires_evidence_review():
    state = _state(
        risk_state=RiskState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.MISSING_SUPPORTING_EVIDENCE,
            )
        ],
    )

    response = build_continuous_risk_response(state)

    action = response.decisions[0]

    assert action.decision == RiskResponseDecision.EVIDENCE_REVIEW


# ============================================================
# CORRECTIVE ACTION REVIEW
# ============================================================


def test_overdue_corrective_action_requires_review():
    state = _state(
        risk_state=RiskState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.OVERDUE_CORRECTIVE_ACTION,
            )
        ],
    )

    response = build_continuous_risk_response(state)

    action = response.decisions[0]

    assert (
        action.decision
        == RiskResponseDecision.CORRECTIVE_ACTION_REVIEW
    )
    assert action.priority == RiskResponsePriority.HIGH


# ============================================================
# TREATMENT
# ============================================================


def test_overdue_treatment_requires_treatment_update():
    state = _state(
        risk_state=RiskState.DEGRADED,
        treatment_state=TreatmentState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.OVERDUE_TREATMENT,
            )
        ],
    )

    response = build_continuous_risk_response(state)

    action = response.decisions[0]

    assert (
        action.decision
        == RiskResponseDecision.UPDATE_TREATMENT
    )
    assert action.priority == RiskResponsePriority.MEDIUM
    assert action.human_approval_required is False


def test_cancelled_treatment_requires_reassessment():
    state = _state(
        risk_state=RiskState.REASSESSMENT_REQUIRED,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT,
        reassessment_required=True,
        reasons=[
            _reason(
                RiskStateReason.TREATMENT_CANCELLED,
            )
        ],
    )

    response = build_continuous_risk_response(state)

    action = response.decisions[0]

    assert (
        action.decision
        == RiskResponseDecision.REASSESS_RISK
    )
    assert action.priority == RiskResponsePriority.HIGH
    assert action.human_approval_required is True


def test_missing_residual_requires_reassessment():
    state = _state(
        risk_state=RiskState.REASSESSMENT_REQUIRED,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT,
        reassessment_required=True,
        reasons=[
            _reason(
                RiskStateReason.TREATMENT_MISSING_RESIDUAL,
            )
        ],
    )

    response = build_continuous_risk_response(state)

    action = response.decisions[0]

    assert (
        action.decision
        == RiskResponseDecision.REASSESS_RISK
    )
    assert action.human_approval_required is True


def test_elevated_residual_risk_requires_reassessment():
    state = _state(
        risk_state=RiskState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.ELEVATED_RESIDUAL_RISK,
                "CRITICAL",
            )
        ],
    )

    response = build_continuous_risk_response(state)

    action = response.decisions[0]

    assert (
        action.decision
        == RiskResponseDecision.REASSESS_RISK
    )
    assert action.priority == RiskResponsePriority.HIGH
    assert action.human_approval_required is True


# ============================================================
# MULTIPLE DRIVERS
# ============================================================


def test_multiple_drivers_are_grouped_by_decision():
    state = _state(
        risk_state=RiskState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.CONTROL_INACTIVE,
            ),
            _reason(
                RiskStateReason.CONTROL_EFFECTIVENESS_LOW,
            ),
            _reason(
                RiskStateReason.STALE_EVIDENCE,
            ),
            _reason(
                RiskStateReason.OVERDUE_TREATMENT,
            ),
        ],
    )

    response = build_continuous_risk_response(state)

    decisions = {
        action.decision
        for action in response.decisions
    }

    assert decisions == {
        RiskResponseDecision.CONTROL_REVIEW,
        RiskResponseDecision.EVIDENCE_REVIEW,
        RiskResponseDecision.UPDATE_TREATMENT,
    }

    assert response.priority == RiskResponsePriority.HIGH
    assert response.human_approval_required is False


def test_critical_escalation_takes_highest_priority():
    state = _state(
        risk_state=RiskState.REASSESSMENT_REQUIRED,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT,
        reassessment_required=True,
        reasons=[
            _reason(
                RiskStateReason.CONTROL_INACTIVE,
            ),
            _reason(
                RiskStateReason.OPEN_CRITICAL_FINDING,
                "CRITICAL",
            ),
            _reason(
                RiskStateReason.STALE_EVIDENCE,
            ),
        ],
    )

    response = build_continuous_risk_response(state)

    assert response.priority == RiskResponsePriority.CRITICAL
    assert response.human_approval_required is True

    assert (
        response.decisions[0].decision
        == RiskResponseDecision.ESCALATE
    )


# ============================================================
# DETERMINISM
# ============================================================


def test_response_order_is_deterministic():
    state = _state(
        risk_state=RiskState.DEGRADED,
        reasons=[
            _reason(
                RiskStateReason.STALE_EVIDENCE,
            ),
            _reason(
                RiskStateReason.CONTROL_INACTIVE,
            ),
            _reason(
                RiskStateReason.OVERDUE_TREATMENT,
            ),
        ],
    )

    response_one = build_continuous_risk_response(state)
    response_two = build_continuous_risk_response(state)

    assert response_one == response_two

    assert [
        action.decision
        for action in response_one.decisions
    ] == [
        RiskResponseDecision.CONTROL_REVIEW,
        RiskResponseDecision.EVIDENCE_REVIEW,
        RiskResponseDecision.UPDATE_TREATMENT,
    ]