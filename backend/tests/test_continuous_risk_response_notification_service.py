from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.risk import Risk
from app.models.user import User

from app.services.continuous_risk_response_notification_service import (
    RESPONSE_NOTIFICATION_TYPE,
    RESPONSE_SOURCE_TYPE,
    build_response_event_key,
    notify_continuous_risk_response,
    should_notify_response,
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
# TEST HELPERS
# ==========================================================


def _create_user(
    db: Session,
    *,
    full_name: str,
    email: str,
    role: str,
    manager_id: int | None = None,
):
    user = User(
        full_name=full_name,
        email=email,
        hashed_password="test-password",
        role=role,
        manager_id=manager_id,
        department="Testing",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def _create_risk(
    db: Session,
    *,
    owner_id: int,
    created_by_id: int,
    title: str = "Response Notification Test Risk",
    risk_score: int = 5,
    likelihood: int = 1,
    impact: int = 5,
):
    risk = Risk(
        title=title,
        description="Risk used for continuous response notification tests.",
        likelihood=likelihood,
        impact=impact,
        risk_score=risk_score,
        status="Open",
        owner_id=owner_id,
        created_by_id=created_by_id,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    return risk


def _build_response(
    *,
    risk_id: int,
    risk_state: str,
    treatment_state: str,
    reassessment_required: bool,
    response_required: bool,
    priority: RiskResponsePriority,
    decisions: tuple[RiskResponseAction, ...],
    human_approval_required: bool,
):
    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state=risk_state,
        treatment_state=treatment_state,
        reassessment_required=reassessment_required,
        response_required=response_required,
        priority=priority,
        decisions=decisions,
        human_approval_required=human_approval_required,
        reasons=tuple(),
    )


def _response_notifications(
    db: Session,
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
        .all()
    )


# ==========================================================
# RESPONSE DECISION FIXTURES
# ==========================================================


def _monitor_response(risk_id: int):
    return _build_response(
        risk_id=risk_id,
        risk_state=RiskState.CURRENT.value,
        treatment_state=TreatmentState.CURRENT.value,
        reassessment_required=False,
        response_required=False,
        priority=RiskResponsePriority.LOW,
        decisions=(
            RiskResponseAction(
                decision=RiskResponseDecision.MONITOR,
                priority=RiskResponsePriority.LOW,
                reason_codes=tuple(),
                human_approval_required=False,
            ),
        ),
        human_approval_required=False,
    )


def _review_response(risk_id: int):
    return _build_response(
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
    )


def _reassessment_response(risk_id: int):
    return _build_response(
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
    )


def _critical_escalation_response(risk_id: int):
    return _build_response(
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
    )


# ==========================================================
# SHOULD NOTIFY
# ==========================================================


def test_monitor_response_requires_no_notification():
    response = _monitor_response(risk_id=100)

    assert response.response_required is False
    assert should_notify_response(response) is False


def test_non_monitor_response_requires_notification():
    response = _review_response(risk_id=100)

    assert response.response_required is True
    assert should_notify_response(response) is True


def test_reassessment_response_requires_notification():
    response = _reassessment_response(risk_id=100)

    assert response.response_required is True
    assert response.human_approval_required is True
    assert should_notify_response(response) is True


def test_critical_escalation_requires_notification():
    response = _critical_escalation_response(risk_id=100)

    assert response.response_required is True
    assert response.priority == RiskResponsePriority.CRITICAL
    assert response.human_approval_required is True
    assert should_notify_response(response) is True


# ==========================================================
# EVENT KEY
# ==========================================================


def test_response_event_key_is_deterministic():
    response = _review_response(risk_id=42)

    first_key = build_response_event_key(response)
    second_key = build_response_event_key(response)

    assert first_key == second_key
    assert first_key.startswith(
        "risk:42:continuous-response:"
    )


def test_response_event_key_changes_when_response_changes():
    review_response = _review_response(risk_id=42)
    reassessment_response = _reassessment_response(risk_id=42)

    review_key = build_response_event_key(
        review_response
    )

    reassessment_key = build_response_event_key(
        reassessment_response
    )

    assert review_key != reassessment_key


# ==========================================================
# CURRENT RISK
# ==========================================================


def test_current_monitoring_risk_creates_no_response_notification(
    db,
    monkeypatch,
):
    owner = _create_user(
        db,
        full_name="Response Monitor Owner",
        email="response_monitor_owner@example.com",
        role="Employee",
    )

    risk = _create_risk(
        db,
        owner_id=owner.id,
        created_by_id=owner.id,
        title="Current Monitoring Risk",
        risk_score=5,
    )

    response = _monitor_response(risk.id)

    monkeypatch.setattr(
        "app.services.continuous_risk_response_notification_service."
        "get_continuous_risk_response",
        lambda db, risk, current_user=None: response,
    )

    returned_response = notify_continuous_risk_response(
        db,
        risk,
    )

    assert returned_response is response

    notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    assert notifications == []


# ==========================================================
# RESPONSE NOTIFICATION CREATION
# ==========================================================


def test_degraded_risk_creates_response_notification(
    db,
    monkeypatch,
):
    owner = _create_user(
        db,
        full_name="Response Degraded Owner",
        email="response_degraded_owner@example.com",
        role="Risk Analyst",
    )

    risk = _create_risk(
        db,
        owner_id=owner.id,
        created_by_id=owner.id,
        title="Degraded Response Risk",
        risk_score=10,
    )

    response = _review_response(risk.id)

    monkeypatch.setattr(
        "app.services.continuous_risk_response_notification_service."
        "get_continuous_risk_response",
        lambda db, risk, current_user=None: response,
    )

    returned_response = notify_continuous_risk_response(
        db,
        risk,
    )

    assert returned_response is response

    db.flush()

    notifications = _response_notifications(
        db,
        risk_id=risk.id,
    )

    assert len(notifications) == 1

    notification = notifications[0]

    assert notification.user_id == owner.id
    assert notification.type == RESPONSE_NOTIFICATION_TYPE
    assert notification.source_type == RESPONSE_SOURCE_TYPE
    assert notification.source_id == risk.id
    assert notification.event_key == build_response_event_key(
        response
    )
    assert notification.is_read is False


# ==========================================================
# DEDUPLICATION
# ==========================================================


def test_response_notification_is_deduplicated(
    db,
    monkeypatch,
):
    owner = _create_user(
        db,
        full_name="Response Dedupe Owner",
        email="response_dedupe_owner@example.com",
        role="Risk Analyst",
    )

    risk = _create_risk(
        db,
        owner_id=owner.id,
        created_by_id=owner.id,
        title="Deduplicated Response Risk",
        risk_score=10,
    )

    response = _review_response(risk.id)

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

    first_count = len(
        _response_notifications(
            db,
            risk_id=risk.id,
        )
    )

    notify_continuous_risk_response(
        db,
        risk,
    )

    db.flush()

    second_count = len(
        _response_notifications(
            db,
            risk_id=risk.id,
        )
    )

    assert first_count == 1
    assert second_count == 1


# ==========================================================
# EVENT KEY PERSISTENCE
# ==========================================================


def test_response_notification_contains_event_key(
    db,
    monkeypatch,
):
    owner = _create_user(
        db,
        full_name="Response Event Owner",
        email="response_event_owner@example.com",
        role="Risk Analyst",
    )

    risk = _create_risk(
        db,
        owner_id=owner.id,
        created_by_id=owner.id,
        title="Event Key Response Risk",
        risk_score=10,
    )

    response = _review_response(risk.id)

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

    notifications = _response_notifications