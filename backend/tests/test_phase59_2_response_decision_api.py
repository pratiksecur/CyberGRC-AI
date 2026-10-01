from datetime import datetime, timedelta, timezone

from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)
from app.services.continuous_risk_response_notification_service import (
    build_response_event_key,
)
from app.services.continuous_risk_response_service import (
    ContinuousRiskResponse,
    RiskResponseAction,
    RiskResponseDecision,
    RiskResponsePriority,
)


def _response(
    *,
    risk_id: int,
    decision=RiskResponseDecision.REASSESS_RISK,
    priority=RiskResponsePriority.HIGH,
    risk_state="REASSESSMENT_REQUIRED",
    treatment_state="REQUIRES_REASSESSMENT",
    reason_codes=("TREATMENT_MISSING_RESIDUAL",),
    human_approval_required=True,
):
    action = RiskResponseAction(
        decision=decision,
        priority=priority,
        reason_codes=reason_codes,
        human_approval_required=human_approval_required,
    )

    return ContinuousRiskResponse(
        risk_id=risk_id,
        risk_state=risk_state,
        treatment_state=treatment_state,
        reassessment_required=(
            risk_state == "REASSESSMENT_REQUIRED"
        ),
        response_required=True,
        priority=priority,
        decisions=(action,),
        human_approval_required=human_approval_required,
        reasons=(),
    )


def _set_response(
    monkeypatch,
    response,
):
    monkeypatch.setattr(
        "app.api.v1.routes.risks.get_continuous_risk_response",
        lambda *args, **kwargs: response,
    )


# ==========================================================
# CREATE
# ==========================================================

def test_create_response_decision_api(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    result = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    assert result.status_code == 201

    body = result.json()

    assert body["risk_id"] == risk.id
    assert body["decision"] == "REASSESS_RISK"
    assert body["priority"] == "HIGH"
    assert body["status"] == "PENDING"
    assert body["human_approval_required"] is True
    assert (
        body["response_event_key"]
        == build_response_event_key(response)
    )


# ==========================================================
# DUPLICATE CREATE
# ==========================================================

def test_duplicate_create_returns_same_decision(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
    db,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    first = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    second = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    assert first.status_code == 201
    assert second.status_code == 201

    assert first.json()["id"] == second.json()["id"]

    assert (
        db.query(
            RiskResponseDecisionRecord
        )
        .count()
        == 1
    )


# ==========================================================
# VISIBILITY / IDOR
# ==========================================================

def test_employee_cannot_create_decision_for_other_users_risk(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["analyst"]
    employee = users["employee"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    result = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    assert result.status_code == 404


def test_employee_cannot_read_other_users_decision(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    analyst = users["analyst"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    created = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    assert created.status_code == 201

    decision_id = created.json()["id"]

    result = client.get(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}",
        headers=auth_headers(analyst),
    )

    assert result.status_code == 404


# ==========================================================
# APPROVAL AUTHORIZATION
# ==========================================================

def test_risk_analyst_cannot_approve_decision(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    analyst = users["analyst"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    created = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    assert created.status_code == 201

    decision_id = created.json()["id"]

    result = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}/approve",
        json={
            "resolution_reason": "Unauthorized approval attempt.",
        },
        headers=auth_headers(analyst),
    )

    assert result.status_code == 403


def test_manager_can_approve_visible_decision(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    created = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    assert created.status_code == 201

    decision_id = created.json()["id"]

    result = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}/approve",
        json={
            "resolution_reason": (
                "Reviewed the response posture and approved "
                "the governed action."
            ),
        },
        headers=auth_headers(manager),
    )

    assert result.status_code == 200

    body = result.json()

    assert body["status"] == "APPROVED"
    assert body["resolved_at"] is not None


# ==========================================================
# APPROVAL REASON
# ==========================================================

def test_approval_requires_reason(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    created = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    decision_id = created.json()["id"]

    result = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}/approve",
        json={
            "resolution_reason": "   ",
        },
        headers=auth_headers(manager),
    )

    assert result.status_code == 422


# ==========================================================
# REJECTION
# ==========================================================

def test_manager_can_reject_decision(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    created = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    decision_id = created.json()["id"]

    result = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}/reject",
        json={
            "resolution_reason": (
                "Rejected because additional evidence "
                "is required."
            ),
        },
        headers=auth_headers(manager),
    )

    assert result.status_code == 200
    assert result.json()["status"] == "REJECTED"


# ==========================================================
# DEFERRAL
# ==========================================================

def test_manager_can_defer_decision(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    created = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    decision_id = created.json()["id"]

    future = (
        datetime.now(timezone.utc)
        + timedelta(days=2)
    )

    result = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}/defer",
        json={
            "resolution_reason": (
                "Deferred pending additional evidence."
            ),
            "deferred_until": future.isoformat(),
        },
        headers=auth_headers(manager),
    )

    assert result.status_code == 200

    body = result.json()

    assert body["status"] == "DEFERRED"
    assert body["deferred_until"] is not None


# ==========================================================
# STALE PROTECTION
# ==========================================================

def test_stale_decision_cannot_be_approved(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    manager = users["manager"]

    original = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        original,
    )

    created = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    assert created.status_code == 201

    decision_id = created.json()["id"]

    changed = _response(
        risk_id=risk.id,
        decision=RiskResponseDecision.ESCALATE,
        priority=RiskResponsePriority.CRITICAL,
        risk_state="DEGRADED",
        treatment_state="DEGRADED",
        reason_codes=("OPEN_CRITICAL_FINDING",),
    )

    _set_response(
        monkeypatch,
        changed,
    )

    result = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}/approve",
        json={
            "resolution_reason": (
                "Attempting to approve stale governance."
            ),
        },
        headers=auth_headers(manager),
    )

    assert result.status_code == 409

    assert (
        "stale"
        in result.json()["detail"].lower()
    )


# ==========================================================
# TERMINAL STATE
# ==========================================================

def test_approved_decision_cannot_be_approved_again(
    client,
    auth_headers,
    users,
    resource_data,
    monkeypatch,
):
    risk = resource_data["risks"]["employee"]
    employee = users["employee"]
    manager = users["manager"]

    response = _response(
        risk_id=risk.id
    )

    _set_response(
        monkeypatch,
        response,
    )

    created = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        json={},
        headers=auth_headers(employee),
    )

    decision_id = created.json()["id"]

    first = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}/approve",
        json={
            "resolution_reason": "Approved after governance review.",
        },
        headers=auth_headers(manager),
    )

    assert first.status_code == 200

    second = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions/{decision_id}/approve",
        json={
            "resolution_reason": "Attempted second approval.",
        },
        headers=auth_headers(manager),
    )

    assert second.status_code == 409