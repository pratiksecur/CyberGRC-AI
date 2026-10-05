from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)


# ==========================================================
# HELPERS
# ==========================================================

def _manager_risk(resource_data):
    return resource_data["risks"]["manager"]


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
                "Approved for Phase 61.7 workflow intelligence testing."
            )
        },
    )

    assert response.status_code == 200


def _execute_manager_response(
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

    return risk, response.json()


# ==========================================================
# PHASE 61.7
# BASIC API CONTRACT
# ==========================================================

def test_workflow_intelligence_endpoint_returns_intelligence(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk, execution_body = _execute_manager_response(
        client,
        users,
        auth_headers,
        resource_data,
    )

    workflow_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert workflow_response.status_code == 200

    workflows = workflow_response.json()

    assert len(workflows) == 1

    workflow_id = workflows[0]["id"]

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow_id}/intelligence"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["workflow_id"] == workflow_id
    assert body["risk_id"] == risk.id
    assert body["status"] == workflows[0]["status"]


# ==========================================================
# INTELLIGENCE FIELD CONTRACT
# ==========================================================

def test_workflow_intelligence_contains_all_phase61_fields(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk, _ = _execute_manager_response(
        client,
        users,
        auth_headers,
        resource_data,
    )

    workflow_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert workflow_response.status_code == 200

    workflow_id = workflow_response.json()[0]["id"]

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow_id}/intelligence"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    expected_fields = {
        "workflow_id",
        "risk_id",
        "status",
        "health",
        "age_days",
        "age_seconds",
        "attention_required",
        "reason_codes",
        "started",
        "terminal",
        "time_to_start_seconds",
        "time_in_progress_seconds",
        "lifecycle_duration_seconds",
        "terminal_age_seconds",
        "decision_priority",
        "priority_rank",
        "governance_level",
        "priority_requires_attention",
        "priority_reason_codes",
        "bottlenecked",
        "bottleneck_reason_codes",
        "escalation_recommendation",
        "escalation_reason_codes",
        "escalation_requires_human_review",
        "dependency_state",
        "dependency_reason_codes",
        "dependency_target_type",
        "dependency_target_id",
    }

    assert expected_fields.issubset(
        body.keys()
    )


# ==========================================================
# PHASE 61.6 DEPENDENCY INTELLIGENCE
# ==========================================================

def test_workflow_intelligence_exposes_dependency_target(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk, _ = _execute_manager_response(
        client,
        users,
        auth_headers,
        resource_data,
    )

    workflow_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert workflow_response.status_code == 200

    workflow = workflow_response.json()[0]

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow['id']}/intelligence"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    body = response.json()

    assert body["dependency_target_type"] == workflow["target_type"]
    assert body["dependency_target_id"] == workflow["target_id"]

    if workflow["target_id"] is not None:
        assert body["dependency_state"] == "AVAILABLE"


# ==========================================================
# READ-ONLY GUARANTEE
# ==========================================================

def test_workflow_intelligence_endpoint_is_read_only(
    client,
    users,
    auth_headers,
    resource_data,
    db,
):
    risk, _ = _execute_manager_response(
        client,
        users,
        auth_headers,
        resource_data,
    )

    workflow_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert workflow_response.status_code == 200

    workflow_id = workflow_response.json()[0]["id"]

    workflow_before = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.id == workflow_id
        )
        .first()
    )

    assert workflow_before is not None

    original_status = workflow_before.status
    original_updated_by_id = workflow_before.updated_by_id
    original_resolution_reason = (
        workflow_before.resolution_reason
    )

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow_id}/intelligence"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    db.expire_all()

    workflow_after = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.id == workflow_id
        )
        .first()
    )

    assert workflow_after is not None

    assert workflow_after.status == original_status
    assert (
        workflow_after.updated_by_id
        == original_updated_by_id
    )
    assert (
        workflow_after.resolution_reason
        == original_resolution_reason
    )


# ==========================================================
# VISIBILITY / IDOR PROTECTION
# ==========================================================

def test_workflow_intelligence_rejects_invisible_risk(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk, _ = _execute_manager_response(
        client,
        users,
        auth_headers,
        resource_data,
    )

    workflow_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert workflow_response.status_code == 200

    workflow_id = workflow_response.json()[0]["id"]

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow_id}/intelligence"
        ),
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404


# ==========================================================
# WRONG RISK / WORKFLOW BINDING
# ==========================================================

def test_workflow_intelligence_rejects_workflow_from_another_risk(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk, _ = _execute_manager_response(
        client,
        users,
        auth_headers,
        resource_data,
    )

    workflow_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert workflow_response.status_code == 200

    workflow_id = workflow_response.json()[0]["id"]

    other_risk = resource_data["risks"]["analyst"]

    response = client.get(
        (
            f"/api/v1/risks/{other_risk.id}"
            f"/response-workflows/{workflow_id}/intelligence"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


# ==========================================================
# MISSING WORKFLOW
# ==========================================================

def test_workflow_intelligence_returns_404_for_missing_workflow(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            "/response-workflows/999999/intelligence"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


# ==========================================================
# AUTHENTICATION
# ==========================================================

def test_workflow_intelligence_requires_authentication(
    client,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            "/response-workflows/1/intelligence"
        )
    )

    assert response.status_code == 401