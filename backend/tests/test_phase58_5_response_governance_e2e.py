from __future__ import annotations

from datetime import date

from app.models.corrective_action import CorrectiveAction
from app.models.notification import Notification
from app.models.risk import Risk

from app.services.continuous_risk_response_notification_service import (
    RESPONSE_NOTIFICATION_TYPE,
    RESPONSE_SOURCE_TYPE,
    ResponseGovernanceLevel,
    build_response_event_key,
    get_response_governance_level,
    notify_continuous_risk_response,
)

from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
    RiskResponsePriority,
)

from app.services.continuous_risk_state_service import (
    RiskState,
    TreatmentState,
)


# ==========================================================
# RESPONSE FIXTURES
# ==========================================================


def _review_response(risk_id: int):
    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state=RiskState.DEGRADED.value,
        treatment_state=TreatmentState.DEGRADED.value,
        reassessment_required=False,
        response_required=True,
        priority=RiskResponsePriority.MEDIUM,
        decisions=(
            RiskResponseAction(
                decision=RiskResponseDecision.REVIEW,
                priority=RiskResponsePriority.MEDIUM,
                reason_codes=("OPEN_HIGH_FINDING",),
                human_approval_required=False,
            ),
        ),
        human_approval_required=False,
        reasons=tuple(),
    )


def _reassessment_response(risk_id: int):
    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state=RiskState.REASSESSMENT_REQUIRED.value,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT.value,
        reassessment_required=True,
        response_required=True,
        priority=RiskResponsePriority.HIGH,
        decisions=(
            RiskResponseAction(
                decision=RiskResponseDecision.REASSESS_RISK,
                priority=RiskResponsePriority.HIGH,
                reason_codes=("TREATMENT_MISSING_RESIDUAL",),
                human_approval_required=True,
            ),
        ),
        human_approval_required=True,
        reasons=tuple(),
    )


def _critical_escalation_response(risk_id: int):
    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state=RiskState.REASSESSMENT_REQUIRED.value,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT.value,
        reassessment_required=True,
        response_required=True,
        priority=RiskResponsePriority.CRITICAL,
        decisions=(
            RiskResponseAction(
                decision=RiskResponseDecision.ESCALATE,
                priority=RiskResponsePriority.CRITICAL,
                reason_codes=(
                    "OPEN_CRITICAL_FINDING",
                    "CRITICAL_CORRECTIVE_ACTION_OPEN",
                ),
                human_approval_required=True,
            ),
            RiskResponseAction(
                decision=RiskResponseDecision.REASSESS_RISK,
                priority=RiskResponsePriority.HIGH,
                reason_codes=("OPEN_CRITICAL_FINDING",),
                human_approval_required=True,
            ),
        ),
        human_approval_required=True,
        reasons=tuple(),
    )


# ==========================================================
# NOTIFICATION HELPERS
# ==========================================================


def _response_notifications(
    db,
    *,
    risk_id: int,
):
    return (
        db.query(Notification)
        .filter(
            Notification.source_type == RESPONSE_SOURCE_TYPE,
            Notification.source_id == risk_id,
            Notification.type == RESPONSE_NOTIFICATION_TYPE,
        )
        .order_by(Notification.id.asc())
        .all()
    )


# ==========================================================
# GOVERNANCE → RECIPIENT CHAIN
# ==========================================================


def test_reassessment_notification_reaches_management_chain(
    db,
    users,
    monkeypatch,
):
    """
    REASSESS_RISK must remain human-governed and notify the
    risk owner plus the existing management chain.
    """

    employee = users["employee"]

    risk = Risk(
        title="Governed Reassessment Risk",
        description="Risk requiring human-approved reassessment.",
        likelihood=4,
        impact=5,
        risk_score=20,
        status="Open",
        owner_id=employee.id,
        created_by_id=employee.id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    response = _reassessment_response(risk.id)

    monkeypatch.setattr(
        "app.services.continuous_risk_response_notification_service."
        "get_continuous_risk_response",
        lambda db, risk, current_user=None: response,
    )

    returned = notify_continuous_risk_response(
        db,
        risk,
    )

    assert returned is response

    assert (
        get_response_governance_level(response)
        == ResponseGovernanceLevel.HUMAN_APPROVAL_REQUIRED
    )

    db.flush()

    notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    recipient_ids = {
        notification.user_id
        for notification in notifications
    }

    # Employee → GRC Manager → Admin
    assert recipient_ids == {
        users["employee"].id,
        users["manager"].id,
        users["admin"].id,
    }

    assert len(notifications) == 3

    for notification in notifications:
        assert notification.event_key == (
            build_response_event_key(response)
        )
        assert "Human approval is required" in notification.message


# ==========================================================
# ESCALATION GOVERNANCE
# ==========================================================


def test_critical_escalation_notifies_management_chain_without_execution(
    db,
    users,
    monkeypatch,
):
    """
    ESCALATE must notify the existing management chain but
    must not execute the escalation itself.
    """

    employee = users["employee"]

    risk = Risk(
        title="Critical Escalation Risk",
        description="Risk requiring governed escalation.",
        likelihood=5,
        impact=5,
        risk_score=25,
        status="Open",
        owner_id=employee.id,
        created_by_id=employee.id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    original_title = risk.title
    original_score = risk.risk_score
    original_status = risk.status

    action_count_before = (
        db.query(CorrectiveAction).count()
    )

    response = _critical_escalation_response(
        risk.id
    )

    monkeypatch.setattr(
        "app.services.continuous_risk_response_notification_service."
        "get_continuous_risk_response",
        lambda db, risk, current_user=None: response,
    )

    returned = notify_continuous_risk_response(
        db,
        risk,
    )

    assert returned is response

    assert (
        get_response_governance_level(response)
        == ResponseGovernanceLevel.ESCALATION
    )

    db.flush()

    notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    assert len(notifications) == 3

    recipient_ids = {
        notification.user_id
        for notification in notifications
    }

    assert recipient_ids == {
        users["employee"].id,
        users["manager"].id,
        users["admin"].id,
    }

    for notification in notifications:
        assert notification.title == (
            "Risk Response Requires Escalation"
        )
        assert "Governed escalation is required" in (
            notification.message
        )
        assert "Human approval is required" in (
            notification.message
        )
        assert notification.event_key == (
            build_response_event_key(response)
        )

    # No risk mutation.
    assert risk.title == original_title
    assert risk.risk_score == original_score
    assert risk.status == original_status

    # No corrective action was created by notification
    # processing.
    assert (
        db.query(CorrectiveAction).count()
        == action_count_before
    )


# ==========================================================
# SAME RESPONSE → DEDUPLICATED ACROSS MANAGEMENT CHAIN
# ==========================================================


def test_same_governed_response_is_deduplicated_per_recipient(
    db,
    users,
    monkeypatch,
):
    employee = users["employee"]

    risk = Risk(
        title="Governed Dedupe Risk",
        description="Risk used to verify governed response dedupe.",
        likelihood=4,
        impact=5,
        risk_score=20,
        status="Open",
        owner_id=employee.id,
        created_by_id=employee.id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    response = _reassessment_response(
        risk.id
    )

    monkeypatch.setattr(
        "app.services.continuous_risk_response_notification_service."
        "get_continuous_risk_response",
        lambda db, risk, current_user=None: response,
    )

    notify_continuous_risk_response(
        db,
        risk,
    )

    db.flush()

    first_notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    assert len(first_notifications) == 3

    notify_continuous_risk_response(
        db,
        risk,
    )

    db.flush()

    second_notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    assert len(second_notifications) == 3

    first_event_keys = {
        notification.event_key
        for notification in first_notifications
    }

    second_event_keys = {
        notification.event_key
        for notification in second_notifications
    }

    assert first_event_keys == second_event_keys


# ==========================================================
# CHANGED RESPONSE → NEW GOVERNED EVENT
# ==========================================================


def test_changed_response_creates_new_governed_event(
    db,
    users,
    monkeypatch,
):
    employee = users["employee"]

    risk = Risk(
        title="Changing Response Risk",
        description="Risk used to verify response transition identity.",
        likelihood=4,
        impact=5,
        risk_score=20,
        status="Open",
        owner_id=employee.id,
        created_by_id=employee.id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    review_response = _review_response(
        risk.id
    )

    reassessment_response = _reassessment_response(
        risk.id
    )

    current_response = {
        "value": review_response,
    }

    monkeypatch.setattr(
        "app.services.continuous_risk_response_notification_service."
        "get_continuous_risk_response",
        lambda db, risk, current_user=None: current_response[
            "value"
        ],
    )

    notify_continuous_risk_response(
        db,
        risk,
    )

    db.flush()

    first_notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    assert len(first_notifications) == 3

    first_event_key = first_notifications[0].event_key

    # The deterministic response changes.
    current_response["value"] = (
        reassessment_response
    )

    notify_continuous_risk_response(
        db,
        risk,
    )

    db.flush()

    second_notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    # Three recipients received the original response and
    # three received the changed response.
    assert len(second_notifications) == 6

    event_keys = {
        notification.event_key
        for notification in second_notifications
    }

    assert first_event_key in event_keys
    assert (
        build_response_event_key(
            reassessment_response
        )
        in event_keys
    )

    assert (
        build_response_event_key(
            review_response
        )
        != build_response_event_key(
            reassessment_response
        )
    )


# ==========================================================
# GOVERNED NOTIFICATION DOES NOT CREATE GRC ACTIONS
# ==========================================================


def test_reassessment_notification_is_side_effect_limited(
    db,
    users,
    monkeypatch,
):
    employee = users["employee"]

    risk = Risk(
        title="Side Effect Boundary Risk",
        description="Risk used to verify notification boundaries.",
        likelihood=4,
        impact=5,
        risk_score=20,
        status="Open",
        owner_id=employee.id,
        created_by_id=employee.id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    risk_snapshot = {
        "title": risk.title,
        "description": risk.description,
        "likelihood": risk.likelihood,
        "impact": risk.impact,
        "risk_score": risk.risk_score,
        "status": risk.status,
        "owner_id": risk.owner_id,
        "created_by_id": risk.created_by_id,
    }

    action_count_before = (
        db.query(CorrectiveAction).count()
    )

    response = _reassessment_response(
        risk.id
    )

    monkeypatch.setattr(
        "app.services.continuous_risk_response_notification_service."
        "get_continuous_risk_response",
        lambda db, risk, current_user=None: response,
    )

    notify_continuous_risk_response(
        db,
        risk,
    )

    db.flush()

    assert {
        "title": risk.title,
        "description": risk.description,
        "likelihood": risk.likelihood,
        "impact": risk.impact,
        "risk_score": risk.risk_score,
        "status": risk.status,
        "owner_id": risk.owner_id,
        "created_by_id": risk.created_by_id,
    } == risk_snapshot

    assert (
        db.query(CorrectiveAction).count()
        == action_count_before
    )

    notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    assert len(notifications) == 3