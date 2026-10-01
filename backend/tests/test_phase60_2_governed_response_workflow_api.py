from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)


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
                "Approved for governed Phase 60 workflow testing."
            )
        },
    )

    assert response.status_code == 200


def _execute_response_decision(
    client,
    users,
    auth_headers,
    risk,
    decision_id,
):
    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-decisions/{decision_id}/execute"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    return response.json()


def _create_executed_workflow(
    client,
    users,
    auth_headers,
    risk,
):
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

    return _execute_response_decision(
        client,
        users,
        auth_headers,
        risk,
        decision_id,
    )


# ==========================================================
# WORKFLOW CREATION
# ==========================================================


def test_execution_creates_governed_response_workflow(
    client,
    db,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    execution = _create_executed_workflow(
        client,
        users,
        auth_headers,
        risk,
    )

    workflow = (
        db.query(RiskResponseWorkflowRecord)
        .filter(
            RiskResponseWorkflowRecord.execution_id
            == execution["id"],
        )
        .one()
    )

    assert workflow.execution_id == execution["id"]
    assert workflow.decision_id == execution["decision_id"]
    assert workflow.risk_id == risk.id
    assert workflow.status == "OPEN"


# ==========================================================
# LIST WORKFLOWS
# ==========================================================


def test_list_response_workflows_for_visible_risk(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    execution = _create_executed_workflow(
        client,
        users,
        auth_headers,
        risk,
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    payload = response.json()

    assert isinstance(payload, list)
    assert len(payload) >= 1

    workflow = next(
        item
        for item in payload
        if item["execution_id"] == execution["id"]
    )

    assert workflow["risk_id"] == risk.id
    assert workflow["status"] == "OPEN"


# ==========================================================
# GET WORKFLOW
# ==========================================================


def test_get_single_response_workflow(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    execution = _create_executed_workflow(
        client,
        users,
        auth_headers,
        risk,
    )

    list_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert list_response.status_code == 200

    workflow = next(
        item
        for item in list_response.json()
        if item["execution_id"] == execution["id"]
    )

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow['id']}"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["id"] == workflow["id"]
    assert payload["execution_id"] == execution["id"]
    assert payload["risk_id"] == risk.id


# ==========================================================
# WRONG RISK BOUNDARY
# ==========================================================


def test_workflow_cannot_be_accessed_through_wrong_risk(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    execution = _create_executed_workflow(
        client,
        users,
        auth_headers,
        risk,
    )

    list_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert list_response.status_code == 200

    workflow = next(
        item
        for item in list_response.json()
        if item["execution_id"] == execution["id"]
    )

    wrong_risk = resource_data["risks"]["admin"]

    response = client.get(
        (
            f"/api/v1/risks/{wrong_risk.id}"
            f"/response-workflows/{workflow['id']}"
        ),
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404


# ==========================================================
# VISIBILITY
# ==========================================================


def test_non_visible_user_cannot_list_response_workflows(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    _create_executed_workflow(
        client,
        users,
        auth_headers,
        risk,
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404


def test_non_visible_user_cannot_get_response_workflow(
    client,
    users,
    auth_headers,
    resource_data,
):
    risk = _manager_risk(resource_data)

    execution = _create_executed_workflow(
        client,
        users,
        auth_headers,
        risk,
    )

    list_response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert list_response.status_code == 200

    workflow = next(
        item
        for item in list_response.json()
        if item["execution_id"] == execution["id"]
    )

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow['id']}"
        ),
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404


# ==========================================================
# AUTHENTICATION
# ==========================================================


def test_unauthenticated_user_cannot_list_response_workflows(
    client,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
    )

    assert response.status_code == 401


def test_unauthenticated_user_cannot_get_response_workflow(
    client,
    resource_data,
):
    risk = _manager_risk(resource_data)

    response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows/1",
    )

    assert response.status_code == 401