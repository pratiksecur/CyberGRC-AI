from types import SimpleNamespace

import pytest

from app.services.continuous_risk_response_service import (
    RiskResponseDecision,
    RiskResponsePriority,
)
from app.services.continuous_risk_state_service import (
    RiskState,
    RiskStateReason,
    RiskStateReasonDetail,
    TreatmentState,
)


# ==========================================================
# HELPERS
# ==========================================================

def _reason(
    code: RiskStateReason,
    severity: str = "HIGH",
    resource_type=None,
    resource_id=None,
):
    return RiskStateReasonDetail(
        code=code,
        severity=severity,
        message=f"Test reason: {code.value}",
        resource_type=resource_type,
        resource_id=resource_id,
    )


def _response(
    *,
    risk_id: int,
    risk_state: str = "CURRENT",
    treatment_state: str = "CURRENT",
    reassessment_required: bool = False,
    response_required: bool = False,
    priority: RiskResponsePriority = RiskResponsePriority.LOW,
    human_approval_required: bool = False,
    decisions=(),
    reasons=(),
):
    return SimpleNamespace(
        risk_id=risk_id,
        risk_state=risk_state,
        treatment_state=treatment_state,
        reassessment_required=reassessment_required,
        response_required=response_required,
        priority=priority,
        human_approval_required=human_approval_required,
        decisions=tuple(decisions),
        reasons=tuple(reasons),
    )


def _decision(
    *,
    decision: RiskResponseDecision,
    priority: RiskResponsePriority,
    reason_codes=(),
    human_approval_required=False,
):
    return SimpleNamespace(
        decision=decision,
        priority=priority,
        reason_codes=tuple(reason_codes),
        human_approval_required=human_approval_required,
    )


# ==========================================================
# BASIC AUTHENTICATION
# ==========================================================

def test_continuous_response_requires_authentication(
    client,
    resource_data,
):
    """
    The continuous response endpoint is protected and must
    reject unauthenticated requests.
    """

    risk = resource_data["risks"]["employee"]

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
    )

    assert response.status_code == 401


def test_continuous_response_rejects_invalid_token(
    client,
    resource_data,
):
    """
    Invalid JWTs must not reach the continuous response
    service.
    """

    risk = resource_data["risks"]["employee"]

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


# ==========================================================
# OBJECT-LEVEL VISIBILITY
# ==========================================================

@pytest.mark.parametrize(
    "user_key,risk_owner_key,expected_status",
    [
        # Admin sees everything.
        ("admin", "admin", 200),
        ("admin", "manager", 200),
        ("admin", "analyst", 200),
        ("admin", "auditor", 200),
        ("admin", "employee", 200),

        # Manager sees itself and descendants.
        ("manager", "manager", 200),
        ("manager", "analyst", 200),
        ("manager", "auditor", 200),
        ("manager", "employee", 200),
        ("manager", "admin", 404),

        # Analyst sees only itself.
        ("analyst", "analyst", 200),
        ("analyst", "admin", 404),
        ("analyst", "manager", 404),
        ("analyst", "auditor", 404),
        ("analyst", "employee", 404),

        # Auditor has organization-wide visibility.
        ("auditor", "admin", 200),
        ("auditor", "manager", 200),
        ("auditor", "analyst", 200),
        ("auditor", "auditor", 200),
        ("auditor", "employee", 200),

        # Employee sees only itself.
        ("employee", "employee", 200),
        ("employee", "admin", 404),
        ("employee", "manager", 404),
        ("employee", "analyst", 404),
        ("employee", "auditor", 404),
    ],
)
def test_continuous_response_respects_risk_visibility(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
    risk_owner_key,
    expected_status,
):
    """
    The continuous response endpoint must enforce the same
    Risk object-level visibility rules as GET /risks/{risk_id}.

    A user must not be able to obtain continuous-risk state
    or response information for an out-of-scope Risk.
    """

    risk = resource_data["risks"][risk_owner_key]

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == expected_status


# ==========================================================
# CURRENT RISK
# ==========================================================

def test_continuous_response_returns_deterministic_reassessment_state(
    client,
    users,
    resource_data,
    auth_headers,
):
    """
    The employee risk fixture does not contain an authoritative
    treatment/residual assessment, so Phase 56 deterministically
    requires reassessment.
    """

    risk = resource_data["risks"]["employee"]

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_id"] == risk.id
    assert data["risk_state"] == RiskState.REASSESSMENT_REQUIRED.value
    assert data["treatment_state"] == TreatmentState.REQUIRES_REASSESSMENT.value
    assert data["reassessment_required"] is True
    assert data["response_required"] is True
    assert data["priority"] == RiskResponsePriority.HIGH.value
    assert data["human_approval_required"] is True

    assert len(data["decisions"]) == 1
    assert data["decisions"][0]["decision"] == RiskResponseDecision.REASSESS_RISK.value
    assert data["decisions"][0]["priority"] == RiskResponsePriority.HIGH.value
    assert data["decisions"][0]["human_approval_required"] is True


# ==========================================================
# RESPONSE SERIALIZATION
# ==========================================================

def test_continuous_response_serializes_reassessment_decision(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    """
    The API must correctly expose a high-impact REASSESS_RISK
    decision and preserve the human-approval requirement.
    """

    risk = resource_data["risks"]["employee"]

    decision = _decision(
        decision=RiskResponseDecision.REASSESS_RISK,
        priority=RiskResponsePriority.HIGH,
        reason_codes=[
            RiskStateReason.TREATMENT_MISSING_RESIDUAL.value,
        ],
        human_approval_required=True,
    )

    expected_response = _response(
        risk_id=risk.id,
        risk_state=RiskState.REASSESSMENT_REQUIRED.value,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT.value,
        reassessment_required=True,
        response_required=True,
        priority=RiskResponsePriority.HIGH,
        human_approval_required=True,
        decisions=[decision],
        reasons=[
            _reason(
                RiskStateReason.TREATMENT_MISSING_RESIDUAL,
                severity="CRITICAL",
            )
        ],
    )

    monkeypatch.setattr(
        "app.api.v1.routes.risks.get_continuous_risk_response",
        lambda db, risk, current_user=None: expected_response,
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_id"] == risk.id
    assert data["risk_state"] == "REASSESSMENT_REQUIRED"
    assert data["treatment_state"] == "REQUIRES_REASSESSMENT"
    assert data["reassessment_required"] is True

    assert data["response_required"] is True
    assert data["priority"] == "HIGH"
    assert data["human_approval_required"] is True

    assert len(data["decisions"]) == 1

    action = data["decisions"][0]

    assert action["decision"] == "REASSESS_RISK"
    assert action["priority"] == "HIGH"
    assert action["reason_codes"] == [
        "TREATMENT_MISSING_RESIDUAL"
    ]
    assert action["human_approval_required"] is True


def test_continuous_response_serializes_critical_escalation(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    """
    Critical escalation must be exposed as a CRITICAL response
    and explicitly require human approval.
    """

    risk = resource_data["risks"]["employee"]

    decision = _decision(
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        reason_codes=[
            RiskStateReason.OPEN_CRITICAL_FINDING.value,
        ],
        human_approval_required=True,
    )

    expected_response = _response(
        risk_id=risk.id,
        risk_state=RiskState.REASSESSMENT_REQUIRED.value,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT.value,
        reassessment_required=True,
        response_required=True,
        priority=RiskResponsePriority.CRITICAL,
        human_approval_required=True,
        decisions=[decision],
        reasons=[
            _reason(
                RiskStateReason.OPEN_CRITICAL_FINDING,
                severity="CRITICAL",
                resource_type="audit_finding",
                resource_id=101,
            )
        ],
    )

    monkeypatch.setattr(
        "app.api.v1.routes.risks.get_continuous_risk_response",
        lambda db, risk, current_user=None: expected_response,
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["priority"] == "CRITICAL"
    assert data["human_approval_required"] is True

    assert len(data["decisions"]) == 1

    action = data["decisions"][0]

    assert action["decision"] == "ESCALATE"
    assert action["priority"] == "CRITICAL"
    assert action["reason_codes"] == [
        "OPEN_CRITICAL_FINDING"
    ]
    assert action["human_approval_required"] is True


# ==========================================================
# MULTIPLE DECISIONS
# ==========================================================

def test_continuous_response_serializes_multiple_decisions(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    """
    Multiple deterministic response decisions must be preserved
    by the API without collapsing or losing individual drivers.
    """

    risk = resource_data["risks"]["employee"]

    control_review = _decision(
        decision=RiskResponseDecision.CONTROL_REVIEW,
        priority=RiskResponsePriority.HIGH,
        reason_codes=[
            RiskStateReason.CONTROL_INACTIVE.value,
            RiskStateReason.CONTROL_EFFECTIVENESS_LOW.value,
        ],
        human_approval_required=False,
    )

    evidence_review = _decision(
        decision=RiskResponseDecision.EVIDENCE_REVIEW,
        priority=RiskResponsePriority.MEDIUM,
        reason_codes=[
            RiskStateReason.STALE_EVIDENCE.value,
        ],
        human_approval_required=False,
    )

    treatment_update = _decision(
        decision=RiskResponseDecision.UPDATE_TREATMENT,
        priority=RiskResponsePriority.MEDIUM,
        reason_codes=[
            RiskStateReason.OVERDUE_TREATMENT.value,
        ],
        human_approval_required=False,
    )

    expected_response = _response(
        risk_id=risk.id,
        risk_state=RiskState.DEGRADED.value,
        treatment_state=TreatmentState.DEGRADED.value,
        reassessment_required=False,
        response_required=True,
        priority=RiskResponsePriority.HIGH,
        human_approval_required=False,
        decisions=[
            control_review,
            evidence_review,
            treatment_update,
        ],
        reasons=[
            _reason(RiskStateReason.CONTROL_INACTIVE),
            _reason(RiskStateReason.CONTROL_EFFECTIVENESS_LOW),
            _reason(RiskStateReason.STALE_EVIDENCE),
            _reason(RiskStateReason.OVERDUE_TREATMENT),
        ],
    )

    monkeypatch.setattr(
        "app.api.v1.routes.risks.get_continuous_risk_response",
        lambda db, risk, current_user=None: expected_response,
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["risk_state"] == "DEGRADED"
    assert data["treatment_state"] == "DEGRADED"
    assert data["response_required"] is True
    assert data["priority"] == "HIGH"
    assert data["human_approval_required"] is False

    assert len(data["decisions"]) == 3

    assert [
        decision["decision"]
        for decision in data["decisions"]
    ] == [
        "CONTROL_REVIEW",
        "EVIDENCE_REVIEW",
        "UPDATE_TREATMENT",
    ]

    assert data["decisions"][0]["reason_codes"] == [
        "CONTROL_INACTIVE",
        "CONTROL_EFFECTIVENESS_LOW",
    ]

    assert data["decisions"][1]["reason_codes"] == [
        "STALE_EVIDENCE",
    ]

    assert data["decisions"][2]["reason_codes"] == [
        "OVERDUE_TREATMENT",
    ]


# ==========================================================
# REASONS
# ==========================================================

def test_continuous_response_serializes_reason_details(
    client,
    users,
    resource_data,
    auth_headers,
    monkeypatch,
):
    """
    Continuous-risk reason details must be exposed with their
    code, severity, message, resource type and resource ID.
    """

    risk = resource_data["risks"]["employee"]

    reason = _reason(
        RiskStateReason.OPEN_CRITICAL_FINDING,
        severity="CRITICAL",
        resource_type="audit_finding",
        resource_id=42,
    )

    decision = _decision(
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        reason_codes=[
            RiskStateReason.OPEN_CRITICAL_FINDING.value,
        ],
        human_approval_required=True,
    )

    expected_response = _response(
        risk_id=risk.id,
        risk_state=RiskState.REASSESSMENT_REQUIRED.value,
        treatment_state=TreatmentState.REQUIRES_REASSESSMENT.value,
        reassessment_required=True,
        response_required=True,
        priority=RiskResponsePriority.CRITICAL,
        human_approval_required=True,
        decisions=[decision],
        reasons=[reason],
    )

    monkeypatch.setattr(
        "app.api.v1.routes.risks.get_continuous_risk_response",
        lambda db, risk, current_user=None: expected_response,
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["reasons"]) == 1

    returned_reason = data["reasons"][0]

    assert returned_reason["code"] == "OPEN_CRITICAL_FINDING"
    assert returned_reason["severity"] == "CRITICAL"
    assert returned_reason["message"] == (
        "Test reason: OPEN_CRITICAL_FINDING"
    )
    assert returned_reason["resource_type"] == "audit_finding"
    assert returned_reason["resource_id"] == 42


# ==========================================================
# NO MUTATION
# ==========================================================

def test_continuous_response_is_read_only(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    """
    Reading continuous response information must not modify
    the underlying Risk.
    """

    risk = resource_data["risks"]["employee"]

    original_title = risk.title
    original_description = risk.description
    original_owner_id = risk.owner_id

    response = client.get(
        f"/api/v1/risks/{risk.id}/continuous-response",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    db.expire_all()

    refreshed_risk = (
        db.query(type(risk))
        .filter(type(risk).id == risk.id)
        .first()
    )

    assert refreshed_risk is not None
    assert refreshed_risk.title == original_title
    assert refreshed_risk.description == original_description
    assert refreshed_risk.owner_id == original_owner_id


# ==========================================================
# NON-EXISTENT RISK
# ==========================================================

def test_continuous_response_returns_404_for_missing_risk(
    client,
    users,
    auth_headers,
):
    """
    A request for a nonexistent Risk must return 404 rather
    than exposing internal service behavior.
    """

    response = client.get(
        "/api/v1/risks/999999/continuous-response",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404