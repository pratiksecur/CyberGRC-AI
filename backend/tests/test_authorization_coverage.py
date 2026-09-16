import pytest


# ==========================================================
# CONTROL ENDPOINT AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key,expected_status",
    [
        ("admin", 200),
        ("manager", 200),
        ("analyst", 200),
        ("auditor", 200),
        ("employee", 200),
    ],
)
def test_controls_list_authorization(
    client,
    users,
    auth_headers,
    expected_status,
    user_key,
):
    response = client.get(
        "/api/v1/controls/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "user_key",
    [
        "manager",
        "analyst",
        "employee",
    ],
)
def test_controls_delete_requires_delete_permission(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
):
    response = client.delete(
        f"/api/v1/controls/{resource_data['controls']['admin'].id}",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


def test_controls_delete_allowed_for_admin(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.delete(
        f"/api/v1/controls/{resource_data['controls']['admin'].id}",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "auditor",
        "employee",
    ],
)
def test_controls_create_requires_create_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/controls/",
        headers=auth_headers(users[user_key]),
        json={
            "title": "Authorization Test Control",
            "description": "Control created for authorization testing.",
            "control_type": "Preventive",
            "status": "Active",
            "effectiveness": 80,
            "owner_id": users[user_key].id,
        },
    )

    assert response.status_code == 403


# ==========================================================
# EVIDENCE ENDPOINT AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_evidence_list_authorization(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/evidence/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "employee",
    ],
)
def test_evidence_delete_requires_delete_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.delete(
        "/api/v1/evidence/999999",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


def test_evidence_delete_allowed_permission_reaches_resource_check(
    client,
    users,
    auth_headers,
):
    response = client.delete(
        "/api/v1/evidence/999999",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404


# ==========================================================
# AUDIT ENDPOINT AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_audits_list_authorization(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/audits/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "employee",
    ],
)
def test_audit_create_requires_create_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/audits/",
        headers=auth_headers(users[user_key]),
        json={
            "name": "Authorization Test Audit",
            "framework_id": 999999,
            "auditor_id": users[user_key].id,
            "scope": "Authorization testing scope",
            "status": "Planned",
            "start_date": "2026-09-16",
            "end_date": "2026-09-20",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "employee",
        "auditor",
    ],
)
def test_audit_delete_requires_delete_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.delete(
        "/api/v1/audits/999999",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


def test_audit_delete_admin_reaches_resource_check(
    client,
    users,
    auth_headers,
):
    response = client.delete(
        "/api/v1/audits/999999",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 404


# ==========================================================
# AUDIT FINDING AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_audit_findings_list_authorization(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/audit-findings/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "employee",
    ],
)
def test_audit_finding_create_requires_create_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/audit-findings/",
        headers=auth_headers(users[user_key]),
        json={
            "audit_id": 999999,
            "control_id": 999999,
            "title": "Authorization Test Finding",
            "description": "Finding created for authorization testing.",
            "severity": "High",
            "recommendation": "Correct the identified control weakness.",
            "status": "Open",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "employee",
    ],
)
def test_audit_finding_delete_requires_delete_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.delete(
        "/api/v1/audit-findings/999999",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


# ==========================================================
# CORRECTIVE ACTION AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_corrective_actions_list_authorization(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/corrective-actions/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
    ],
)
def test_corrective_action_create_requires_create_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    # Risk Analyst does not have corrective_actions:create.
    response = client.post(
        "/api/v1/corrective-actions/",
        headers=auth_headers(users[user_key]),
        json={
            "finding_id": 999999,
            "assigned_to": users[user_key].id,
            "title": "Authorization Test Action",
            "description": "Corrective action created for authorization testing.",
            "priority": "High",
            "status": "Open",
            "due_date": "2026-10-01",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "auditor",
    ],
)
def test_corrective_action_delete_requires_delete_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.delete(
        "/api/v1/corrective-actions/999999",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


# ==========================================================
# CORRECTIVE ACTION ASSIGNEES
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_corrective_action_assignees_authorization(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/corrective-actions/assignees",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


# ==========================================================
# USER AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_visible_users_available_to_all_authenticated_roles(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/users/visible",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_admin_user_list_requires_admin_role(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/users/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


def test_admin_can_list_users(
    client,
    users,
    auth_headers,
):
    response = client.get(
        "/api/v1/users/",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_get_user_requires_admin_role(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        f"/api/v1/users/{users['admin'].id}",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_user_role_update_requires_admin_role(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.patch(
        f"/api/v1/users/{users['employee'].id}/role",
        headers=auth_headers(users[user_key]),
        json={
            "role": "Employee",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_user_organization_update_requires_admin_role(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.patch(
        f"/api/v1/users/{users['employee'].id}/organization",
        headers=auth_headers(users[user_key]),
        json={
            "manager_id": users["manager"].id,
            "department": "Authorization Testing",
        },
    )

    assert response.status_code == 403


# ==========================================================
# REPORT AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/reports/risks",
        "/api/v1/reports/audits",
        "/api/v1/reports/compliance",
    ],
)
def test_employee_cannot_access_reports(
    client,
    users,
    auth_headers,
    endpoint,
):
    response = client.get(
        endpoint,
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
    ],
)
@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/reports/risks",
        "/api/v1/reports/audits",
        "/api/v1/reports/compliance",
    ],
)
def test_authorized_roles_can_access_reports(
    client,
    users,
    auth_headers,
    user_key,
    endpoint,
):
    response = client.get(
        endpoint,
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


# ==========================================================
# FRAMEWORK AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_framework_list_authorization(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/frameworks/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_framework_create_requires_create_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/frameworks/",
        headers=auth_headers(users[user_key]),
        json={
            "name": "Authorization Test Framework",
            "version": "1.0",
            "description": "Framework created for authorization testing.",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_framework_update_requires_update_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.patch(
        "/api/v1/frameworks/999999",
        headers=auth_headers(users[user_key]),
        json={
            "name": "Updated Framework",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_framework_delete_requires_delete_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.delete(
        "/api/v1/frameworks/999999",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


# ==========================================================
# FRAMEWORK CONTROL AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_framework_control_list_authorization(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/framework-controls/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_framework_control_create_requires_create_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/framework-controls/",
        headers=auth_headers(users[user_key]),
        json={
            "framework_id": 999999,
            "control_code": "AUTH-001",
            "title": "Authorization Test Control",
            "description": "Framework control authorization test.",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_framework_control_update_requires_update_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.patch(
        "/api/v1/framework-controls/999999",
        headers=auth_headers(users[user_key]),
        json={
            "title": "Updated Authorization Control",
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_framework_control_delete_requires_delete_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.delete(
        "/api/v1/framework-controls/999999",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


# ==========================================================
# AI AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "employee",
    ],
)
def test_generic_ai_risk_analysis_requires_ai_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/ai/risk/999999/analyze",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "employee",
    ],
)
def test_generic_ai_control_recommendation_requires_ai_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/ai/risk/999999/recommend-controls",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "analyst",
        "employee",
    ],
)
def test_generic_ai_audit_summary_requires_ai_permission(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/ai/audit/999999/summarize",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "auditor",
    ],
)
def test_generic_ai_risk_analysis_authorized_roles_reach_resource_check(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/ai/risk/999999/analyze",
        headers=auth_headers(users[user_key]),
    )

    # AI permission is valid. The nonexistent Risk should then
    # produce the endpoint's resource-level 404.
    assert response.status_code == 404


@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "auditor",
    ],
)
def test_generic_ai_control_recommendation_authorized_roles_reach_resource_check(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.post(
        "/api/v1/ai/risk/999999/recommend-controls",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_executive_ai_summary_is_restricted_to_grc_manager(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/ai/dashboard/executive-summary",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 403


# ==========================================================
# DASHBOARD AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_dashboard_authorized_for_roles_with_risk_view(
    client,
    users,
    auth_headers,
    user_key,
):
    response = client.get(
        "/api/v1/dashboard/",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == 200


# ==========================================================
# OBJECT-LEVEL PERMISSION GATES
# ==========================================================

@pytest.mark.parametrize(
    "endpoint,user_key",
    [
        ("/api/v1/controls/999999", "auditor"),
        ("/api/v1/controls/999999", "employee"),
        ("/api/v1/evidence/999999", "admin"),
        ("/api/v1/audits/999999", "employee"),
        ("/api/v1/audit-findings/999999", "employee"),
        ("/api/v1/corrective-actions/999999", "analyst"),
        ("/api/v1/frameworks/999999", "employee"),
        ("/api/v1/framework-controls/999999", "employee"),
    ],
)
def test_restricted_object_endpoints_enforce_authorization(
    client,
    users,
    auth_headers,
    endpoint,
    user_key,
):
    """
    Confirm that protected object endpoints enforce the
    configured permission before attempting resource lookup.
    """

    response = client.get(
        endpoint,
        headers=auth_headers(users[user_key]),
    )

    # All selected roles have view permission for these resources,
    # except the corrective-action case where Analyst does have view.
    # Therefore object lookup is expected to reach 404.
    assert response.status_code == 404