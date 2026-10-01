from datetime import datetime, timedelta, timezone

from app.models.risk_response_execution import (
    RiskResponseExecutionRecord,
)


# ==========================================================
# HELPERS
# ==========================================================


def _manager_risk(resource_data):
    return resource_data["risks"]["manager"]


def _admin_risk(resource_data):
    return resource_data["risks"]["admin"]


def _employee_risk(resource_data):
    return resource_data["risks"]["employee"]


def _create_response_decision(
    client,
    users,
    auth_headers,
    risk,
):
    response = client.post(
        f"/api/v1/risks/{risk.id}/response-decisions",
        headers=auth_headers(users["manager"]),
        json={},
    )

    assert response.status_code == 201

    return response.json()["id"]


def _approve_response_decision(
    client,
    users,
    auth_headers,
    risk,
    decision_id,
):
    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/approve"
        ),
        headers=auth_headers(users["manager"]),
        json={
            "resolution_reason": (
                "Approved for governed response execution."
            )
        },
    )

    assert response.status_code == 200

    return response


# ==========================================================
# 1. ADMIN CAN EXECUTE APPROVED RESPONSE
# ==========================================================


def test_admin_can_execute_approved_response(
    client,
    db,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    decision_id = _create_response_decision(
        client,
        users,
        auth_headers,
        risk,
    )

    _approve_response_decision(
        client,
        users,
        auth_headers,
        risk,
        decision_id,
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/execute"
        ),
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision_id"] == decision_id
    assert body["risk_id"] == risk.id
    assert body["status"] == "EXECUTED"
    assert body["human_approval_verified"] is True
    assert body["response_event_verified"] is True
    assert body["executed_by_id"] == users["admin"].id

    execution = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision_id
        )
        .one()
    )

    assert execution.executed_by_id == users["admin"].id


# ==========================================================
# 2. GRC MANAGER CAN EXECUTE APPROVED RESPONSE
# ==========================================================


def test_manager_can_execute_approved_response(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    decision_id = _create_response_decision(
        client,
        users,
        auth_headers,
        risk,
    )

    _approve_response_decision(
        client,
        users,
        auth_headers,
        risk,
        decision_id,
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/execute"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["decision_id"] == decision_id
    assert body["risk_id"] == risk.id
    assert body["status"] == "EXECUTED"
    assert body["human_approval_verified"] is True
    assert body["response_event_verified"] is True
    assert body["executed_by_id"] == users["manager"].id


# ==========================================================
# 3. RISK ANALYST CANNOT EXECUTE
# ==========================================================


def test_risk_analyst_cannot_execute_response(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            "/response-decisions/999999/execute"
        ),
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 403


# ==========================================================
# 4. AUDITOR CANNOT EXECUTE
# ==========================================================


def test_auditor_cannot_execute_response(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            "/response-decisions/999999/execute"
        ),
        headers=auth_headers(users["auditor"]),
    )

    assert response.status_code == 403


# ==========================================================
# 5. EMPLOYEE CANNOT EXECUTE
# ==========================================================


def test_employee_cannot_execute_response(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            "/response-decisions/999999/execute"
        ),
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403


# ==========================================================
# 6. NON-EXISTENT DECISION RETURNS 404
# ==========================================================


def test_nonexistent_response_decision_returns_404(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            "/response-decisions/999999/execute"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


# ==========================================================
# 7. DECISION FROM ANOTHER RISK RETURNS 404
# ==========================================================


def test_decision_from_another_risk_returns_404(
    client,
    users,
    auth_headers,
    resource_data,
):
    source_risk = _manager_risk(resource_data)
    target_risk = _admin_risk(resource_data)

    decision_id = _create_response_decision(
        client,
        users,
        auth_headers,
        source_risk,
    )

    _approve_response_decision(
        client,
        users,
        auth_headers,
        source_risk,
        decision_id,
    )

    response = client.post(
        (
            f"/api/v1/risks/{target_risk.id}"
            f"/response-decisions/{decision_id}/execute"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


# ==========================================================
# 8. PENDING DECISION CANNOT EXECUTE
# ==========================================================


def test_pending_response_decision_returns_409(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    decision_id = _create_response_decision(
        client,
        users,
        auth_headers,
        risk,
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/execute"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 409


# ==========================================================
# 9. REJECTED DECISION CANNOT EXECUTE
# ==========================================================


def test_rejected_response_decision_returns_409(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    decision_id = _create_response_decision(
        client,
        users,
        auth_headers,
        risk,
    )

    reject_response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/reject"
        ),
        headers=auth_headers(users["manager"]),
        json={
            "resolution_reason": (
                "Response is not approved for execution."
            )
        },
    )

    assert reject_response.status_code == 200

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/execute"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 409


# ==========================================================
# 10. DEFERRED DECISION CANNOT EXECUTE
# ==========================================================


def test_deferred_response_decision_returns_409(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    decision_id = _create_response_decision(
        client,
        users,
        auth_headers,
        risk,
    )

    deferred_until = (
        datetime.now(timezone.utc)
        + timedelta(days=1)
    ).isoformat()

    defer_response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/defer"
        ),
        headers=auth_headers(users["manager"]),
        json={
            "resolution_reason": (
                "Execution deferred pending additional review."
            ),
            "deferred_until": deferred_until,
        },
    )

    assert defer_response.status_code == 200

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/execute"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 409


# ==========================================================
# 11. DUPLICATE EXECUTION IS BLOCKED
# ==========================================================


def test_duplicate_response_execution_returns_409(
    client,
    db,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    decision_id = _create_response_decision(
        client,
        users,
        auth_headers,
        risk,
    )

    _approve_response_decision(
        client,
        users,
        auth_headers,
        risk,
        decision_id,
    )

    endpoint = (
        f"/api/v1/risks/{risk.id}"
        f"/response-decisions/{decision_id}/execute"
    )

    first_response = client.post(
        endpoint,
        headers=auth_headers(users["manager"]),
    )

    assert first_response.status_code == 200

    second_response = client.post(
        endpoint,
        headers=auth_headers(users["manager"]),
    )

    assert second_response.status_code == 409

    executions = (
        db.query(RiskResponseExecutionRecord)
        .filter(
            RiskResponseExecutionRecord.decision_id
            == decision_id
        )
        .all()
    )

    assert len(executions) == 1


# ==========================================================
# 12. EXECUTION REQUIRES AUTHENTICATION
# ==========================================================


def test_execution_requires_authentication(
    client,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            "/response-decisions/999999/execute"
        )
    )

    assert response.status_code == 401


# ==========================================================
# 13. AUTHORIZED USER CANNOT EXECUTE DECISION
#     FROM ANOTHER RISK
# ==========================================================


def test_authorized_user_cannot_execute_decision_from_other_risk(
    client,
    users,
    auth_headers,
    resource_data,
):
    source_risk = _manager_risk(resource_data)
    target_risk = _employee_risk(resource_data)

    decision_id = _create_response_decision(
        client,
        users,
        auth_headers,
        source_risk,
    )

    _approve_response_decision(
        client,
        users,
        auth_headers,
        source_risk,
        decision_id,
    )

    response = client.post(
        (
            f"/api/v1/risks/{target_risk.id}"
            f"/response-decisions/{decision_id}/execute"
        ),
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404