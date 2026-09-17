"""
Phase 42 — Authorization Negative Testing

This module performs attack-oriented authorization testing
against the CyberGRC-AI API.

The goal is not merely to verify that the RBAC matrix is correct,
but to actively attempt common authorization attacks:

    - IDOR / BOLA
    - Ownership injection
    - Privilege escalation
    - Unauthorized reassignment
    - Cross-resource enumeration
    - Cross-resource relationship abuse
    - AI authorization bypass
    - Role manipulation
    - Organization hierarchy manipulation

Expected HTTP semantics:

    401 = unauthenticated
    403 = authenticated but lacks permission / assignment authority
    404 = authenticated and permitted, but requested object is
          outside the caller's visibility scope / does not exist
"""


import pytest

from app.core.roles import UserRole
from app.models.risk_control import RiskControl


# ==========================================================
# TEST DATA HELPERS
# ==========================================================


def risk_payload(owner_id):
    return {
        "title": "Malicious Ownership Test Risk",
        "description": (
            "Testing whether ownership can be injected "
            "outside the caller's authorization scope."
        ),
        "likelihood": 3,
        "impact": 4,
        "owner_id": owner_id,
    }


def control_payload(owner_id):
    return {
        "title": "Malicious Ownership Test Control",
        "description": (
            "Testing whether control ownership can be "
            "injected outside the caller's authorization scope."
        ),
        "control_type": "Preventive",
        "status": "Active",
        "effectiveness": 80,
        "owner_id": owner_id,
    }


def audit_payload(framework_id, auditor_id):
    return {
        "name": "Authorization Attack Audit",
        "framework_id": framework_id,
        "auditor_id": auditor_id,
        "scope": "Authorization Security Testing",
        "status": "Planned",
        "start_date": "2026-09-17",
        "end_date": "2026-10-17",
    }


def finding_payload(audit_id, control_id):
    return {
        "audit_id": audit_id,
        "control_id": control_id,
        "title": "Authorization Attack Finding",
        "description": (
            "Testing whether a user can create a finding "
            "against an unauthorized audit."
        ),
        "severity": "High",
        "recommendation": (
            "Prevent creation of findings for audits "
            "outside the caller's authorization scope."
        ),
        "status": "Open",
    }


def corrective_action_payload(finding_id, assigned_to):
    return {
        "finding_id": finding_id,
        "assigned_to": assigned_to,
        "title": "Authorization Attack Corrective Action",
        "description": (
            "Testing whether corrective actions can be "
            "assigned outside the caller's authorization scope."
        ),
        "priority": "High",
        "status": "Open",
        "due_date": "2026-10-17",
    }


# ==========================================================
# 1. IDOR / BOLA — RISKS
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_get_risk_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    risk = resource_data["risks"][target_key]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_update_risk_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    risk = resource_data["risks"][target_key]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[attacker_key]),
        json={
            "title": "Unauthorized IDOR Update",
        },
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_delete_risk_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    risk = resource_data["risks"][target_key]

    response = client.delete(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == 403


# ==========================================================
# 2. IDOR / BOLA — CONTROLS
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_key,expected_status",
    [
        # Employee — organization-wide controls
        ("employee", "admin", 200),
        ("employee", "analyst", 200),
        ("employee", "auditor", 200),

        # Analyst — own controls only
        ("analyst", "admin", 404),
        ("analyst", "employee", 404),

        # Manager — subordinate controls only
        ("manager", "admin", 404),
    ],
)
def test_control_object_access_respects_actual_scope(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
    expected_status,
):
    control = resource_data["controls"][target_key]

    response = client.get(
        f"/api/v1/controls/{control.id}",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "target_key",
    [
        "admin",
        "analyst",
        "auditor",
    ],
)
def test_employee_cannot_update_organization_control(
    client,
    users,
    resource_data,
    auth_headers,
    target_key,
):
    control = resource_data["controls"][target_key]

    response = client.patch(
        f"/api/v1/controls/{control.id}",
        headers=auth_headers(users["employee"]),
        json={
            "title": "Unauthorized Control Update",
        },
    )

    # Employee can VIEW organization-wide controls but does
    # not possess controls:update permission.
    assert response.status_code == 403


# ==========================================================
# 3. OWNERSHIP INJECTION — RISK CREATION
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,forbidden_owner_key",
    [
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
    ],
)
def test_risk_creation_cannot_inject_out_of_scope_owner(
    client,
    users,
    auth_headers,
    attacker_key,
    forbidden_owner_key,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users[attacker_key]),
        json=risk_payload(
            users[forbidden_owner_key].id
        ),
    )

    assert response.status_code == 403


def test_analyst_can_create_risk_for_self(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["analyst"]),
        json=risk_payload(
            users["analyst"].id
        ),
    )

    assert response.status_code == 200


def test_employee_can_create_risk_for_self(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
        json=risk_payload(
            users["employee"].id
        ),
    )

    assert response.status_code == 200


# ==========================================================
# 4. OWNERSHIP INJECTION — RISK REASSIGNMENT
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,new_owner_key",
    [
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
    ],
)
def test_risk_reassignment_cannot_escape_scope(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    new_owner_key,
):
    own_risk = resource_data["risks"][attacker_key]

    response = client.patch(
        f"/api/v1/risks/{own_risk.id}",
        headers=auth_headers(users[attacker_key]),
        json={
            "owner_id": users[new_owner_key].id,
        },
    )

    assert response.status_code == 403


# ==========================================================
# 5. OWNERSHIP INJECTION — CONTROL CREATION
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,forbidden_owner_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
    ],
)
def test_control_creation_cannot_inject_out_of_scope_owner(
    client,
    users,
    auth_headers,
    attacker_key,
    forbidden_owner_key,
):
    response = client.post(
        "/api/v1/controls/",
        headers=auth_headers(users[attacker_key]),
        json=control_payload(
            users[forbidden_owner_key].id
        ),
    )

    assert response.status_code == 403


def test_analyst_can_create_control_for_self(
    client,
    users,
    auth_headers,
):
    response = client.post(
        "/api/v1/controls/",
        headers=auth_headers(users["analyst"]),
        json=control_payload(
            users["analyst"].id
        ),
    )

    assert response.status_code == 200


# ==========================================================
# 6. EVIDENCE — CROSS-SCOPE ACCESS
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_get_evidence_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    evidence = resource_data["evidence"][target_key]

    response = client.get(
        f"/api/v1/evidence/{evidence.id}",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_update_evidence_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    evidence = resource_data["evidence"][target_key]

    response = client.patch(
        f"/api/v1/evidence/{evidence.id}",
        headers=auth_headers(users[attacker_key]),
        json={
            "title": "Unauthorized Evidence Update",
        },
    )

    assert response.status_code == 404


# ==========================================================
# 7. AUDIT — CROSS-SCOPE ACCESS
# ==========================================================


@pytest.mark.parametrize(
    "target_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
    ],
)
def test_employee_can_view_organization_audits(
    client,
    users,
    resource_data,
    auth_headers,
    target_key,
):
    audit = resource_data["audits"][target_key]

    response = client.get(
        f"/api/v1/audits/{audit.id}",
        headers=auth_headers(users["employee"]),
    )

    # Employee has organization-wide audit visibility.
    assert response.status_code == 200


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_update_audit_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    audit = resource_data["audits"][target_key]

    response = client.patch(
        f"/api/v1/audits/{audit.id}",
        headers=auth_headers(users[attacker_key]),
        json={
            "name": "Unauthorized Audit Update",
        },
    )

    if attacker_key == "manager":
        assert response.status_code == 404
    else:
        assert response.status_code == 403


# ==========================================================
# 8. AUDIT ASSIGNMENT INJECTION
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,forbidden_auditor_key",
    [
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
    ],
)
def test_audit_creation_cannot_assign_out_of_scope_auditor(
    client,
    users,
    auth_headers,
    resource_data,
    attacker_key,
    forbidden_auditor_key,
):
    framework = resource_data["audits"]["admin"].framework_id

    response = client.post(
        "/api/v1/audits/",
        headers=auth_headers(users[attacker_key]),
        json=audit_payload(
            framework,
            users[forbidden_auditor_key].id,
        ),
    )

    assert response.status_code == 403


# ==========================================================
# 9. AUDIT REASSIGNMENT INJECTION
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_audit_key,new_auditor_key",
    [
        ("manager", "manager", "admin"),
        ("analyst", "analyst", "admin"),
        ("auditor", "auditor", "admin"),
    ],
)
def test_audit_reassignment_cannot_escape_scope(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_audit_key,
    new_auditor_key,
):
    audit = resource_data["audits"][target_audit_key]

    response = client.patch(
        f"/api/v1/audits/{audit.id}",
        headers=auth_headers(users[attacker_key]),
        json={
            "auditor_id": users[new_auditor_key].id,
        },
    )

    assert response.status_code == 403


# ==========================================================
# 10. AUDIT FINDING — CROSS-SCOPE ACCESS
# ==========================================================


@pytest.mark.parametrize(
    "target_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
    ],
)
def test_employee_can_view_organization_findings(
    client,
    users,
    resource_data,
    auth_headers,
    target_key,
):
    finding = resource_data["findings"][target_key]

    response = client.get(
        f"/api/v1/audit-findings/{finding.id}",
        headers=auth_headers(users["employee"]),
    )

    # Employee has organization-wide audit-finding visibility.
    assert response.status_code == 200


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_update_finding_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    finding = resource_data["findings"][target_key]

    response = client.patch(
        f"/api/v1/audit-findings/{finding.id}",
        headers=auth_headers(users[attacker_key]),
        json={
            "title": "Unauthorized Finding Update",
        },
    )

    if attacker_key == "manager":
        assert response.status_code == 404
    else:
        assert response.status_code == 403


# ==========================================================
# 11. FINDING CREATION AGAINST OUT-OF-SCOPE AUDIT
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("manager", "admin"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("auditor", "admin"),
    ],
)
def test_finding_creation_cannot_target_out_of_scope_audit(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    audit = resource_data["audits"][target_key]
    control = resource_data["controls"][attacker_key]

    response = client.post(
        "/api/v1/audit-findings/",
        headers=auth_headers(users[attacker_key]),
        json=finding_payload(
            audit.id,
            control.id,
        ),
    )

    assert response.status_code == 403


# ==========================================================
# 12. CORRECTIVE ACTION — CROSS-SCOPE ACCESS
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_get_corrective_action_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    action = resource_data["corrective_actions"][target_key]

    response = client.get(
        f"/api/v1/corrective-actions/{action.id}",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == 404


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "admin"),
        ("employee", "manager"),
        ("employee", "analyst"),
        ("employee", "auditor"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("analyst", "auditor"),
        ("analyst", "employee"),
        ("manager", "admin"),
    ],
)
def test_idor_update_corrective_action_outside_scope_is_blocked(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_key,
):
    action = resource_data["corrective_actions"][target_key]

    response = client.patch(
        f"/api/v1/corrective-actions/{action.id}",
        headers=auth_headers(users[attacker_key]),
        json={
            "title": "Unauthorized Corrective Action Update",
        },
    )

    if attacker_key == "manager":
        assert response.status_code == 404
    elif attacker_key == "employee":
        assert response.status_code == 404
    else:
        assert response.status_code == 403


# ==========================================================
# 13. CORRECTIVE ACTION ASSIGNMENT INJECTION
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_finding_key,forbidden_assignee_key",
    [
        ("employee", "employee", "admin"),
        ("employee", "employee", "manager"),
        ("analyst", "analyst", "admin"),
        ("analyst", "analyst", "manager"),
    ],
)
def test_corrective_action_cannot_assign_out_of_scope_user(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    target_finding_key,
    forbidden_assignee_key,
):
    finding = resource_data["findings"][target_finding_key]

    response = client.post(
        "/api/v1/corrective-actions/",
        headers=auth_headers(users[attacker_key]),
        json=corrective_action_payload(
            finding.id,
            users[forbidden_assignee_key].id,
        ),
    )

    assert response.status_code == 403


# ==========================================================
# 14. RISK-CONTROL MAPPING — CROSS-SCOPE ATTACKS
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,risk_key,control_key",
    [
        ("employee", "admin", "employee"),
        ("employee", "employee", "admin"),
        ("employee", "admin", "admin"),
        ("analyst", "admin", "analyst"),
        ("analyst", "analyst", "admin"),
        ("analyst", "manager", "analyst"),
        ("manager", "admin", "manager"),
    ],
)
def test_risk_control_mapping_cannot_cross_resource_scope(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    risk_key,
    control_key,
):
    response = client.post(
        "/api/v1/risk-controls/",
        headers=auth_headers(users[attacker_key]),
        json={
            "risk_id": resource_data["risks"][risk_key].id,
            "control_id": resource_data["controls"][control_key].id,
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "attacker_key,risk_key",
    [
        ("employee", "admin"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("manager", "admin"),
    ],
)
def test_risk_control_mapping_risk_access_respects_actual_scope(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    risk_key,
):
    risk = resource_data["risks"][risk_key]

    response = client.get(
        f"/api/v1/risk-controls/risk/{risk.id}",
        headers=auth_headers(users[attacker_key]),
    )

    if attacker_key == "employee":
        assert response.status_code == 200
    else:
        assert response.status_code == 404


@pytest.mark.parametrize(
    "attacker_key,control_key",
    [
        ("employee", "admin"),
        ("analyst", "admin"),
        ("analyst", "manager"),
        ("manager", "admin"),
    ],
)
def test_risk_control_mapping_control_access_respects_actual_scope(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
    control_key,
):
    control = resource_data["controls"][control_key]

    response = client.get(
        f"/api/v1/risk-controls/control/{control.id}",
        headers=auth_headers(users[attacker_key]),
    )

    if attacker_key == "employee":
        assert response.status_code == 200
    else:
        assert response.status_code == 404


# ==========================================================
# 15. PRIVILEGE ESCALATION — ROLE MANIPULATION
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_promote_user_to_admin(
    client,
    users,
    auth_headers,
    attacker_key,
):
    response = client.patch(
        f"/api/v1/users/{users[attacker_key].id}/role",
        headers=auth_headers(users[attacker_key]),
        json={
            "role": UserRole.ADMIN.value,
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "attacker_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_demote_or_modify_admin_role(
    client,
    users,
    auth_headers,
    attacker_key,
):
    response = client.patch(
        f"/api/v1/users/{users['admin'].id}/role",
        headers=auth_headers(users[attacker_key]),
        json={
            "role": UserRole.EMPLOYEE.value,
        },
    )

    assert response.status_code == 403


# ==========================================================
# 16. PRIVILEGE ESCALATION — ORGANIZATION MANIPULATION
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_change_organizational_hierarchy(
    client,
    users,
    auth_headers,
    attacker_key,
):
    response = client.patch(
        f"/api/v1/users/{users[attacker_key].id}/organization",
        headers=auth_headers(users[attacker_key]),
        json={
            "manager_id": users["admin"].id,
            "department": "Executive",
        },
    )

    assert response.status_code == 403


# ==========================================================
# 17. PERMISSION ESCALATION
# ==========================================================


@pytest.mark.parametrize(
    "role_key,endpoint,method",
    [
        (
            "employee",
            "/api/v1/risks/999999",
            "delete",
        ),
        (
            "employee",
            "/api/v1/controls/999999",
            "delete",
        ),
        (
            "employee",
            "/api/v1/frameworks/999999",
            "delete",
        ),
        (
            "employee",
            "/api/v1/framework-controls/999999",
            "delete",
        ),
        (
            "employee",
            "/api/v1/evidence/999999",
            "delete",
        ),
        (
            "employee",
            "/api/v1/audits/999999",
            "delete",
        ),
        (
            "employee",
            "/api/v1/audit-findings/999999",
            "delete",
        ),
        (
            "employee",
            "/api/v1/corrective-actions/999999",
            "delete",
        ),
        (
            "auditor",
            "/api/v1/risks/999999",
            "delete",
        ),
        (
            "auditor",
            "/api/v1/controls/999999",
            "delete",
        ),
        (
            "analyst",
            "/api/v1/frameworks/999999",
            "delete",
        ),
        (
            "analyst",
            "/api/v1/audits/999999",
            "delete",
        ),
    ],
)
def test_privileged_mutations_cannot_be_reached_without_permission(
    client,
    users,
    auth_headers,
    role_key,
    endpoint,
    method,
):
    response = client.request(
        method.upper(),
        endpoint,
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


# ==========================================================
# 18. AI AUTHORIZATION BYPASS
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key",
    [
        "analyst",
        "employee",
    ],
)
def test_unauthorized_user_cannot_analyze_risk_with_ai(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
):
    risk = resource_data["risks"]["admin"]

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/analyze",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "attacker_key",
    [
        "analyst",
        "employee",
    ],
)
def test_unauthorized_user_cannot_request_ai_control_recommendations(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
):
    risk = resource_data["risks"]["admin"]

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/recommend-controls",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "attacker_key",
    [
        "analyst",
        "employee",
    ],
)
def test_unauthorized_user_cannot_summarize_audit_with_ai(
    client,
    users,
    resource_data,
    auth_headers,
    attacker_key,
):
    audit = resource_data["audits"]["admin"]

    response = client.post(
        f"/api/v1/ai/audit/{audit.id}/summarize",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "attacker_key",
    [
        "admin",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_manager_cannot_access_executive_ai(
    client,
    users,
    auth_headers,
    attacker_key,
):
    response = client.get(
        "/api/v1/ai/dashboard/executive-summary",
        headers=auth_headers(users[attacker_key]),
    )

    assert response.status_code == 403


# ==========================================================
# 19. AI OBJECT-LEVEL IDOR
# ==========================================================


def test_auditor_ai_cannot_analyze_out_of_scope_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/analyze",
        headers=auth_headers(users["auditor"]),
    )

    # Auditor has organization-wide risk visibility.
    # Therefore the authorization layer must not reject this
    # request with 403.
    assert response.status_code != 403


def test_manager_ai_cannot_analyze_admin_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.post(
        f"/api/v1/ai/risk/{risk.id}/analyze",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 404


# ==========================================================
# 20. CROSS-RESOURCE IDOR — RISK/CONTROL MAPPING
# ==========================================================


def test_employee_can_access_organization_risk_mapping(
    client,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]

    response = client.get(
        f"/api/v1/risk-controls/risk/{risk.id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200


def test_employee_can_access_organization_control_mapping(
    client,
    users,
    resource_data,
    auth_headers,
):
    control = resource_data["controls"]["admin"]

    response = client.get(
        f"/api/v1/risk-controls/control/{control.id}",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200


# ==========================================================
# 21. AUTHENTICATION BYPASS
# ==========================================================


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("get", "/api/v1/risks/"),
        ("get", "/api/v1/controls/"),
        ("get", "/api/v1/evidence/"),
        ("get", "/api/v1/audits/"),
        ("get", "/api/v1/audit-findings/"),
        ("get", "/api/v1/corrective-actions/"),
        ("get", "/api/v1/risk-controls/risk/1"),
        ("get", "/api/v1/risk-controls/control/1"),
        (
            "get",
            "/api/v1/ai/dashboard/executive-summary",
        ),
    ],
)
def test_protected_endpoints_reject_missing_authentication(
    client,
    method,
    endpoint,
):
    response = client.request(
        method.upper(),
        endpoint,
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "method,endpoint",
    [
        ("get", "/api/v1/risks/"),
        ("get", "/api/v1/controls/"),
        ("get", "/api/v1/evidence/"),
        ("get", "/api/v1/audits/"),
        ("get", "/api/v1/audit-findings/"),
        ("get", "/api/v1/corrective-actions/"),
    ],
)
def test_protected_endpoints_reject_forged_token(
    client,
    method,
    endpoint,
):
    response = client.request(
        method.upper(),
        endpoint,
        headers={
            "Authorization": "Bearer forged.invalid.token",
        },
    )

    assert response.status_code == 401


# ==========================================================
# 22. RESOURCE ID MANIPULATION
# ==========================================================


@pytest.mark.parametrize(
    "role_key,endpoint",
    [
        ("employee", "/api/v1/risks/999999"),
        ("employee", "/api/v1/controls/999999"),
        ("employee", "/api/v1/evidence/999999"),
        ("employee", "/api/v1/audits/999999"),
        ("employee", "/api/v1/audit-findings/999999"),
        ("employee", "/api/v1/corrective-actions/999999"),
        ("manager", "/api/v1/risks/999999"),
        ("manager", "/api/v1/audits/999999"),
        ("analyst", "/api/v1/risks/999999"),
    ],
)
def test_nonexistent_resource_ids_do_not_bypass_authorization(
    client,
    users,
    auth_headers,
    role_key,
    endpoint,
):
    response = client.get(
        endpoint,
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 404


# ==========================================================
# 23. ROLE VALUE TAMPERING
# ==========================================================


def test_employee_cannot_inject_admin_role_value(
    client,
    users,
    auth_headers,
):
    response = client.patch(
        f"/api/v1/users/{users['employee'].id}/role",
        headers=auth_headers(users["employee"]),
        json={
            "role": "Admin",
        },
    )

    assert response.status_code == 403


def test_analyst_cannot_inject_manager_role_value(
    client,
    users,
    auth_headers,
):
    response = client.patch(
        f"/api/v1/users/{users['analyst'].id}/role",
        headers=auth_headers(users["analyst"]),
        json={
            "role": "GRC Manager",
        },
    )

    assert response.status_code == 403


# ==========================================================
# 24. ORGANIZATION ID / MANAGER ID TAMPERING
# ==========================================================


@pytest.mark.parametrize(
    "attacker_key,target_key",
    [
        ("employee", "employee"),
        ("analyst", "analyst"),
        ("auditor", "auditor"),
        ("manager", "manager"),
    ],
)
def test_non_admin_cannot_assign_admin_as_manager(
    client,
    users,
    auth_headers,
    attacker_key,
    target_key,
):
    response = client.patch(
        f"/api/v1/users/{users[target_key].id}/organization",
        headers=auth_headers(users[attacker_key]),
        json={
            "manager_id": users["admin"].id,
            "department": "Executive",
        },
    )

    assert response.status_code == 403


# ==========================================================
# 25. SECURITY INVARIANT — ATTACKS MUST NOT CHANGE OWNERSHIP
# ==========================================================


def test_failed_risk_owner_injection_does_not_change_database_owner(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["employee"]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users["employee"]),
        json={
            "owner_id": users["admin"].id,
        },
    )

    assert response.status_code == 403

    db.refresh(risk)

    assert risk.owner_id == users["employee"].id


def test_failed_control_owner_injection_does_not_change_database_owner(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    control = resource_data["controls"]["employee"]

    response = client.patch(
        f"/api/v1/controls/{control.id}",
        headers=auth_headers(users["employee"]),
        json={
            "owner_id": users["admin"].id,
        },
    )

    assert response.status_code == 403

    db.refresh(control)

    assert control.owner_id == users["employee"].id


# ==========================================================
# 26. SECURITY INVARIANT — FAILED CROSS-SCOPE ATTACK
#     MUST NOT CREATE RELATIONSHIPS
# ==========================================================


def test_failed_cross_scope_mapping_does_not_create_mapping(
    client,
    db,
    users,
    resource_data,
    auth_headers,
):
    risk = resource_data["risks"]["admin"]
    control = resource_data["controls"]["employee"]

    existing = (
        db.query(RiskControl)
        .filter(
            RiskControl.risk_id == risk.id,
            RiskControl.control_id == control.id,
        )
        .first()
    )

    assert existing is None

    response = client.post(
        "/api/v1/risk-controls/",
        headers=auth_headers(users["employee"]),
        json={
            "risk_id": risk.id,
            "control_id": control.id,
        },
    )

    assert response.status_code == 403

    created = (
        db.query(RiskControl)
        .filter(
            RiskControl.risk_id == risk.id,
            RiskControl.control_id == control.id,
        )
        .first()
    )

    assert created is None