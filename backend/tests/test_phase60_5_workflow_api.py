from datetime import datetime, timezone

import pytest

from app.core.roles import UserRole

from app.models.risk_response_decision import (
    RiskResponseDecisionRecord,
)
from app.models.risk_response_execution import (
    RiskResponseExecutionRecord,
)
from app.models.risk_response_workflow import (
    RiskResponseWorkflowRecord,
)


def _create_workflow(
    db,
    *,
    risk,
    creator,
    decision="REASSESS_RISK",
):
    decision_record = RiskResponseDecisionRecord(
        risk_id=risk.id,
        decision=decision,
        priority="HIGH",
        governance_level="HUMAN_APPROVAL_REQUIRED",
        status="APPROVED",
        human_approval_required=True,
        response_event_key=(
            f"phase60-5-test-{risk.id}"
        ),
        reason_codes=["PHASE60_5_TEST"],
        risk_state="REASSESSMENT_REQUIRED",
        treatment_state="REQUIRES_REASSESSMENT",
        reassessment_required=True,
        response_required=True,
        requested_by_id=creator.id,
        assigned_to_id=creator.id,
        resolution_reason="Approved for Phase 60 workflow testing.",
    )

    db.add(decision_record)
    db.flush()

    execution = RiskResponseExecutionRecord(
        decision_id=decision_record.id,
        risk_id=risk.id,
        decision=decision,
        response_event_key=decision_record.response_event_key,
        status="EXECUTED",
        execution_action=decision,
        human_approval_verified=True,
        response_event_verified=True,
        executed_by_id=creator.id,
        execution_reason=(
            "Phase 60.5 API test execution."
        ),
        result_message=(
            "Phase 60.5 API test execution recorded."
        ),
        executed_at=datetime.now(timezone.utc),
    )

    db.add(execution)
    db.flush()

    workflow = RiskResponseWorkflowRecord(
        execution_id=execution.id,
        decision_id=decision_record.id,
        risk_id=risk.id,
        workflow_type=decision,
        status="OPEN",
        target_type="RISK",
        target_id=risk.id,
        title="Phase 60.5 workflow",
        description=(
            "Workflow created for Phase 60.5 API testing."
        ),
        created_by_id=creator.id,
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow


# ==========================================================
# LIST WORKFLOWS
# ==========================================================


def test_admin_can_list_response_workflows(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["risk_id"] == risk.id
    assert data[0]["status"] == "OPEN"


def test_manager_can_list_visible_response_workflows(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["risk_id"] == risk.id


def test_employee_can_list_own_visible_workflow(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["risk_id"] == risk.id


# ==========================================================
# VISIBILITY
# ==========================================================


def test_employee_cannot_access_manager_workflow(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["manager"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.get(
        f"/api/v1/risks/{risk.id}/response-workflows",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}"
        ),
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 404


def test_wrong_risk_workflow_pair_returns_404(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    employee_risk = resource_data["risks"]["employee"]
    manager_risk = resource_data["risks"]["manager"]

    workflow = _create_workflow(
        db,
        risk=employee_risk,
        creator=users["manager"],
    )

    response = client.get(
        (
            f"/api/v1/risks/{manager_risk.id}"
            f"/response-workflows/{workflow.id}"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


def test_nonexistent_workflow_returns_404(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            "/response-workflows/999999"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


# ==========================================================
# WORKFLOW DETAIL
# ==========================================================


def test_get_workflow_returns_full_lifecycle_fields(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.get(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}"
        ),
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == workflow.id
    assert data["execution_id"] == workflow.execution_id
    assert data["decision_id"] == workflow.decision_id
    assert data["risk_id"] == risk.id

    assert data["workflow_type"] == "REASSESS_RISK"
    assert data["status"] == "OPEN"
    assert data["target_type"] == "RISK"
    assert data["target_id"] == risk.id

    assert data["created_by_id"] == users["manager"].id

    assert data["updated_by_id"] is None
    assert data["resolution_reason"] is None
    assert data["started_at"] is None
    assert data["completed_at"] is None
    assert data["cancelled_at"] is None


# ==========================================================
# TRANSITION AUTHORIZATION
# ==========================================================


@pytest.mark.parametrize(
    "role_name",
    [
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_governance_roles_cannot_transition_workflow(
    client,
    db,
    users,
    resource_data,
    auth_headers,
    role_name,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "IN_PROGRESS",
        },
        headers=auth_headers(users[role_name]),
    )

    assert response.status_code == 403


def test_admin_can_transition_workflow(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "IN_PROGRESS",
        },
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "IN_PROGRESS"
    assert data["updated_by_id"] == users["admin"].id
    assert data["started_at"] is not None


def test_manager_can_transition_workflow(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "IN_PROGRESS",
        },
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "IN_PROGRESS"
    assert data["updated_by_id"] == users["manager"].id
    assert data["started_at"] is not None


# ==========================================================
# INVALID TRANSITIONS
# ==========================================================


def test_open_to_completed_is_rejected(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "COMPLETED",
            "resolution_reason": "Attempted invalid transition.",
        },
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 409


def test_completion_requires_resolution_reason(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "IN_PROGRESS",
        },
        headers=auth_headers(users["manager"]),
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "COMPLETED",
        },
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 409


def test_cancellation_requires_resolution_reason(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    response = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "CANCELLED",
        },
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 409


# ==========================================================
# TERMINAL STATE
# ==========================================================


def test_completed_workflow_cannot_be_reopened(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "IN_PROGRESS",
        },
        headers=auth_headers(users["manager"]),
    )

    completion = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "COMPLETED",
            "resolution_reason": (
                "Workflow completed for API lifecycle test."
            ),
        },
        headers=auth_headers(users["manager"]),
    )

    assert completion.status_code == 200
    assert completion.json()["status"] == "COMPLETED"

    reopen = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "IN_PROGRESS",
        },
        headers=auth_headers(users["manager"]),
    )

    assert reopen.status_code == 409


def test_cancelled_workflow_cannot_be_reopened(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    workflow = _create_workflow(
        db,
        risk=risk,
        creator=users["manager"],
    )

    cancellation = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "CANCELLED",
            "resolution_reason": (
                "Workflow cancelled for API lifecycle test."
            ),
        },
        headers=auth_headers(users["manager"]),
    )

    assert cancellation.status_code == 200
    assert cancellation.json()["status"] == "CANCELLED"

    reopen = client.post(
        (
            f"/api/v1/risks/{risk.id}"
            f"/response-workflows/{workflow.id}/transition"
        ),
        json={
            "status": "IN_PROGRESS",
        },
        headers=auth_headers(users["manager"]),
    )

    assert reopen.status_code == 409