"""
Phase 41 — Full API Authorization Matrix

This module verifies the backend authorization boundary
independently of the React frontend.

Authorization is tested across:

    Authentication
        ↓
    Permission
        ↓
    Resource scope
        ↓
    Object visibility
        ↓
    API response

The production authorization implementation is intentionally
not modified by this test module.

HTTP semantics:

    401 = unauthenticated
    403 = authenticated but lacks permission
    404 = authenticated and permitted, but requested object
         is outside the user's visibility scope / does not exist
"""

import pytest

from app.auth.permissions import (
    ROLE_PERMISSIONS,
    ROLE_SCOPES,
    has_permission,
    get_access_scope,
)

from app.auth.scopes import AccessScope
from app.core.roles import UserRole


# ==========================================================
# CONSTANTS
# ==========================================================

ROLE_KEYS = [
    "admin",
    "manager",
    "analyst",
    "auditor",
    "employee",
]


ROLE_TO_ENUM = {
    "admin": UserRole.ADMIN.value,
    "manager": UserRole.GRC_MANAGER.value,
    "analyst": UserRole.RISK_ANALYST.value,
    "auditor": UserRole.AUDITOR.value,
    "employee": UserRole.EMPLOYEE.value,
}


# ==========================================================
# 1. PERMISSION MATRIX — SOURCE OF TRUTH
# ==========================================================

EXPECTED_PERMISSIONS = {
    "admin": {
        "users": {"view", "create", "update", "delete"},
        "risks": {"view", "create", "update", "delete"},
        "controls": {"view", "create", "update", "delete"},
        "frameworks": {"view", "create", "update", "delete"},
        "framework_controls": {
            "view",
            "create",
            "update",
            "delete",
        },
        "control_framework_mappings": {
            "view",
            "create",
            "delete",
        },
        "evidence": {
            "view",
            "create",
            "update",
            "delete",
        },
        "audits": {
            "view",
            "create",
            "update",
            "delete",
        },
        "audit_findings": {
            "view",
            "create",
            "update",
            "delete",
        },
        "corrective_actions": {
            "view",
            "create",
            "update",
            "delete",
        },
        "reports": {
            "view",
            "create",
        },
        "ai": {
            "view",
            "use",
        },
    },

    "manager": {
        "users": {"view"},
        "risks": {
            "view",
            "create",
            "update",
        },
        "controls": {
            "view",
            "create",
            "update",
        },
        "frameworks": {
            "view",
            "create",
            "update",
            "delete",
        },
        "framework_controls": {
            "view",
            "create",
            "update",
            "delete",
        },
        "control_framework_mappings": {
            "view",
            "create",
            "delete",
        },
        "evidence": {
            "view",
            "create",
            "update",
        },
        "audits": {
            "view",
            "create",
            "update",
        },
        "audit_findings": {
            "view",
            "create",
            "update",
        },
        "corrective_actions": {
            "view",
            "create",
            "update",
        },
        "reports": {
            "view",
            "create",
        },
        "ai": {
            "view",
            "use",
        },
        "ai_executive_summary": {
            "view",
            "use",
        },
    },

    "analyst": {
        "risks": {
            "view",
            "create",
            "update",
        },
        "controls": {
            "view",
            "create",
            "update",
        },
        "frameworks": {"view"},
        "framework_controls": {"view"},
        "control_framework_mappings": {
            "view",
            "create",
        },
        "evidence": {
            "view",
            "create",
            "update",
        },
        "audits": {"view"},
        "audit_findings": {"view"},
        "corrective_actions": {"view"},
        "reports": {"view"},
    },

    "auditor": {
        "risks": {"view"},
        "controls": {"view"},
        "frameworks": {"view"},
        "framework_controls": {"view"},
        "control_framework_mappings": {"view"},
        "evidence": {
            "view",
            "create",
            "update",
        },
        "audits": {
            "view",
            "create",
            "update",
        },
        "audit_findings": {
            "view",
            "create",
            "update",
        },
        "corrective_actions": {
            "view",
            "create",
            "update",
        },
        "reports": {"view"},
        "ai": {
            "view",
            "use",
        },
    },

    "employee": {
        "risks": {
            "view",
            "create",
            "update",
        },
        "controls": {"view"},
        "frameworks": {"view"},
        "framework_controls": {"view"},
        "control_framework_mappings": {"view"},
        "evidence": {
            "view",
            "create",
            "update",
        },
        "audits": {"view"},
        "audit_findings": {"view"},
        "corrective_actions": {
            "view",
            "update",
        },
    },
}


@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_role_permission_configuration_matches_phase_41_matrix(
    role_key,
):
    """
    Verify that the implemented permission matrix matches
    the intended Phase 41 authorization contract.
    """

    role = ROLE_TO_ENUM[role_key]

    actual = ROLE_PERMISSIONS.get(role, {})

    expected = EXPECTED_PERMISSIONS[role_key]

    assert actual == expected


# ==========================================================
# 2. ACCESS SCOPE MATRIX
# ==========================================================

EXPECTED_SCOPES = {
    "admin": {
        "users": AccessScope.ORGANIZATION,
        "risks": AccessScope.ORGANIZATION,
        "controls": AccessScope.ORGANIZATION,
        "frameworks": AccessScope.ORGANIZATION,
        "framework_controls": AccessScope.ORGANIZATION,
        "control_framework_mappings": AccessScope.ORGANIZATION,
        "evidence": AccessScope.ORGANIZATION,
        "audits": AccessScope.ORGANIZATION,
        "audit_findings": AccessScope.ORGANIZATION,
        "corrective_actions": AccessScope.ORGANIZATION,
        "reports": AccessScope.ORGANIZATION,
        "ai": AccessScope.ORGANIZATION,
    },

    "manager": {
        "users": AccessScope.SUBORDINATES,
        "risks": AccessScope.SUBORDINATES,
        "controls": AccessScope.SUBORDINATES,
        "frameworks": AccessScope.ORGANIZATION,
        "framework_controls": AccessScope.ORGANIZATION,
        "control_framework_mappings": AccessScope.SUBORDINATES,
        "evidence": AccessScope.SUBORDINATES,
        "audits": AccessScope.SUBORDINATES,
        "audit_findings": AccessScope.SUBORDINATES,
        "corrective_actions": AccessScope.SUBORDINATES,
        "reports": AccessScope.SUBORDINATES,
        "ai": AccessScope.SUBORDINATES,
        "ai_executive_summary": AccessScope.SUBORDINATES,
    },

    "analyst": {
        "risks": AccessScope.OWN,
        "controls": AccessScope.OWN,
        "frameworks": AccessScope.ORGANIZATION,
        "framework_controls": AccessScope.ORGANIZATION,
        "control_framework_mappings": AccessScope.OWN,
        "evidence": AccessScope.OWN,
        "audits": AccessScope.OWN,
        "audit_findings": AccessScope.OWN,
        "corrective_actions": AccessScope.OWN,
        "reports": AccessScope.OWN,
    },

    "auditor": {
        "risks": AccessScope.ORGANIZATION,
        "controls": AccessScope.ORGANIZATION,
        "frameworks": AccessScope.ORGANIZATION,
        "framework_controls": AccessScope.ORGANIZATION,
        "control_framework_mappings": AccessScope.ORGANIZATION,
        "evidence": AccessScope.ORGANIZATION,
        "audits": AccessScope.OWN,
        "audit_findings": AccessScope.OWN,
        "corrective_actions": AccessScope.OWN,
        "reports": AccessScope.ORGANIZATION,
        "ai": AccessScope.ORGANIZATION,
    },

    "employee": {
        "risks": AccessScope.OWN,
        "controls": AccessScope.ORGANIZATION,
        "frameworks": AccessScope.ORGANIZATION,
        "framework_controls": AccessScope.ORGANIZATION,
        "control_framework_mappings": AccessScope.ORGANIZATION,
        "evidence": AccessScope.OWN,
        "audits": AccessScope.ORGANIZATION,
        "audit_findings": AccessScope.ORGANIZATION,
        "corrective_actions": AccessScope.OWN,
    },
}


@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_role_scope_configuration_matches_phase_41_matrix(
    role_key,
):
    """
    Verify that implemented role scopes match the intended
    resource-specific scope matrix.
    """

    role = ROLE_TO_ENUM[role_key]

    actual = ROLE_SCOPES.get(role, {})

    expected = EXPECTED_SCOPES[role_key]

    assert actual == expected


@pytest.mark.parametrize(
    "role_key,resource,expected_scope",
    [
        (
            "admin",
            "risks",
            AccessScope.ORGANIZATION,
        ),
        (
            "manager",
            "risks",
            AccessScope.SUBORDINATES,
        ),
        (
            "analyst",
            "risks",
            AccessScope.OWN,
        ),
        (
            "auditor",
            "risks",
            AccessScope.ORGANIZATION,
        ),
        (
            "employee",
            "risks",
            AccessScope.OWN,
        ),
        (
            "admin",
            "evidence",
            AccessScope.ORGANIZATION,
        ),
        (
            "manager",
            "evidence",
            AccessScope.SUBORDINATES,
        ),
        (
            "analyst",
            "evidence",
            AccessScope.OWN,
        ),
        (
            "auditor",
            "evidence",
            AccessScope.ORGANIZATION,
        ),
        (
            "employee",
            "evidence",
            AccessScope.OWN,
        ),
        (
            "admin",
            "audits",
            AccessScope.ORGANIZATION,
        ),
        (
            "manager",
            "audits",
            AccessScope.SUBORDINATES,
        ),
        (
            "analyst",
            "audits",
            AccessScope.OWN,
        ),
        (
            "auditor",
            "audits",
            AccessScope.OWN,
        ),
        (
            "employee",
            "audits",
            AccessScope.ORGANIZATION,
        ),
        (
            "admin",
            "corrective_actions",
            AccessScope.ORGANIZATION,
        ),
        (
            "manager",
            "corrective_actions",
            AccessScope.SUBORDINATES,
        ),
        (
            "analyst",
            "corrective_actions",
            AccessScope.OWN,
        ),
        (
            "auditor",
            "corrective_actions",
            AccessScope.OWN,
        ),
        (
            "employee",
            "corrective_actions",
            AccessScope.OWN,
        ),
    ],
)
def test_specific_resource_scopes(
    users,
    role_key,
    resource,
    expected_scope,
):
    """
    Verify representative resource-specific scopes directly
    against the authenticated role.
    """

    user = users[role_key]

    assert get_access_scope(
        user,
        resource,
    ) == expected_scope


# ==========================================================
# 3. READ API MATRIX
# ==========================================================

READ_ENDPOINTS = [
    (
        "risks",
        "/api/v1/risks/",
    ),
    (
        "controls",
        "/api/v1/controls/",
    ),
    (
        "frameworks",
        "/api/v1/frameworks/",
    ),
    (
        "framework_controls",
        "/api/v1/framework-controls/",
    ),
    (
        "evidence",
        "/api/v1/evidence/",
    ),
    (
        "audits",
        "/api/v1/audits/",
    ),
    (
        "audit_findings",
        "/api/v1/audit-findings/",
    ),
    (
        "corrective_actions",
        "/api/v1/corrective-actions/",
    ),
]


@pytest.mark.parametrize(
    "resource,endpoint",
    READ_ENDPOINTS,
)
@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_all_roles_with_view_permission_can_access_read_api(
    client,
    users,
    auth_headers,
    resource,
    endpoint,
    role_key,
):
    """
    Every role that has resource:view must be able to reach
    the corresponding list endpoint.

    The test database may contain no records for some resources;
    the important authorization result is that the request is not
    rejected by the permission dependency.
    """

    user = users[role_key]

    assert has_permission(
        user,
        resource,
        "view",
    )

    response = client.get(
        endpoint,
        headers=auth_headers(user),
    )

    assert response.status_code == 200


# ==========================================================
# 4. USERS API
# ==========================================================

@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_visible_users_is_available_to_every_authenticated_role(
    client,
    users,
    auth_headers,
    role_key,
):
    """
    /users/visible is an organizational visibility endpoint,
    not an administrator-only user-management endpoint.
    """

    response = client.get(
        "/api/v1/users/visible",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "role_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_admin_user_listing_is_denied_to_non_admin_roles(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.get(
        "/api/v1/users/",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


def test_admin_can_access_user_administration(
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
    "role_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_get_arbitrary_user(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.get(
        f"/api/v1/users/{users['admin'].id}",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_change_user_role(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.patch(
        f"/api/v1/users/{users['employee'].id}/role",
        headers=auth_headers(users[role_key]),
        json={
            "role": UserRole.EMPLOYEE.value,
        },
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_change_user_organization(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.patch(
        f"/api/v1/users/{users['employee'].id}/organization",
        headers=auth_headers(users[role_key]),
        json={
            "manager_id": users["manager"].id,
            "department": "Authorization Testing",
        },
    )

    assert response.status_code == 403


# ==========================================================
# 5. RISK OBJECT VISIBILITY
# ==========================================================

@pytest.mark.parametrize(
    "user_key,risk_owner_key,expected_status",
    [
        # ADMIN — organization
        ("admin", "admin", 200),
        ("admin", "manager", 200),
        ("admin", "analyst", 200),
        ("admin", "auditor", 200),
        ("admin", "employee", 200),

        # MANAGER — subordinate hierarchy
        ("manager", "manager", 200),
        ("manager", "analyst", 200),
        ("manager", "auditor", 200),
        ("manager", "employee", 200),
        ("manager", "admin", 404),

        # ANALYST — own
        ("analyst", "analyst", 200),
        ("analyst", "admin", 404),
        ("analyst", "manager", 404),
        ("analyst", "auditor", 404),
        ("analyst", "employee", 404),

        # AUDITOR — organization
        ("auditor", "admin", 200),
        ("auditor", "manager", 200),
        ("auditor", "analyst", 200),
        ("auditor", "auditor", 200),
        ("auditor", "employee", 200),

        # EMPLOYEE — own
        ("employee", "employee", 200),
        ("employee", "admin", 404),
        ("employee", "manager", 404),
        ("employee", "analyst", 404),
        ("employee", "auditor", 404),
    ],
)
def test_risk_object_authorization_matrix(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
    risk_owner_key,
    expected_status,
):
    risk = resource_data["risks"][risk_owner_key]

    response = client.get(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == expected_status


# ==========================================================
# 6. CONTROL OBJECT VISIBILITY
# ==========================================================

@pytest.mark.parametrize(
    "user_key,control_owner_key,expected_status",
    [
        # ADMIN — organization
        ("admin", "admin", 200),
        ("admin", "analyst", 200),
        ("admin", "employee", 200),

        # MANAGER — subordinate hierarchy
        ("manager", "analyst", 200),
        ("manager", "employee", 200),
        ("manager", "admin", 404),

        # ANALYST — own
        ("analyst", "analyst", 200),
        ("analyst", "admin", 404),
        ("analyst", "employee", 404),

        # AUDITOR — organization
        ("auditor", "admin", 200),
        ("auditor", "analyst", 200),
        ("auditor", "employee", 200),

        # EMPLOYEE — organization
        ("employee", "admin", 200),
        ("employee", "analyst", 200),
        ("employee", "employee", 200),
    ],
)
def test_control_object_authorization_matrix(
    client,
    users,
    resource_data,
    auth_headers,
    user_key,
    control_owner_key,
    expected_status,
):
    control = resource_data["controls"][control_owner_key]

    response = client.get(
        f"/api/v1/controls/{control.id}",
        headers=auth_headers(users[user_key]),
    )

    assert response.status_code == expected_status


# ==========================================================
# 7. REPORT AUTHORIZATION
# ==========================================================

REPORT_ENDPOINTS = [
    "/api/v1/reports/risks",
    "/api/v1/reports/audits",
    "/api/v1/reports/compliance",
    "/api/v1/reports/corrective-actions/",
]


@pytest.mark.parametrize(
    "endpoint",
    REPORT_ENDPOINTS,
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
    "role_key",
    [
        "admin",
        "manager",
        "analyst",
        "auditor",
    ],
)
@pytest.mark.parametrize(
    "endpoint",
    REPORT_ENDPOINTS,
)
def test_report_authorization_for_roles_with_reports_view(
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

    assert response.status_code == 200


# ==========================================================
# 8. RISK-CONTROL MAPPING AUTHORIZATION
# ==========================================================

def test_all_roles_have_risk_control_mapping_view_permission(
    users,
):
    """
    Every current role has control_framework_mappings:view.

    This test verifies the permission contract directly. Object-level
    mapping visibility is covered separately by the route authorization
    tests and the resource-specific scope implementation.
    """

    for role_key in ROLE_KEYS:
        assert has_permission(
            users[role_key],
            "control_framework_mappings",
            "view",
        )


# ==========================================================
# 9. CONTROL-FRAMEWORK MAPPING AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_all_roles_have_framework_mapping_view_permission(
    users,
    role_key,
):
    """
    The permission contract grants view access to all roles.
    """

    user = users[role_key]

    assert has_permission(
        user,
        "control_framework_mappings",
        "view",
    )


@pytest.mark.parametrize(
    "role_key",
    [
        "auditor",
        "employee",
    ],
)
def test_auditor_and_employee_cannot_delete_framework_mapping(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.delete(
        "/api/v1/control-framework-controls/999999",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role_key",
    [
        "analyst",
    ],
)
def test_analyst_cannot_delete_framework_mapping(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.delete(
        "/api/v1/control-framework-controls/999999",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role_key",
    [
        "admin",
        "manager",
    ],
)
def test_admin_and_manager_reach_framework_mapping_delete_gate(
    client,
    users,
    auth_headers,
    role_key,
):
    """
    Admin and Manager have delete permission.

    A nonexistent mapping therefore reaches the resource layer
    and should return 404 rather than 403.
    """

    response = client.delete(
        "/api/v1/control-framework-controls/999999",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 404


# ==========================================================
# 10. MUTATION PERMISSION MATRIX
# ==========================================================

MUTATION_PERMISSION_MATRIX = [
    # resource, action, endpoint, method, roles_without_permission
    (
        "risks",
        "delete",
        "/api/v1/risks/999999",
        "delete",
        ["manager", "analyst", "auditor", "employee"],
    ),
    (
        "controls",
        "delete",
        "/api/v1/controls/999999",
        "delete",
        ["manager", "analyst", "auditor", "employee"],
    ),
    (
        "frameworks",
        "delete",
        "/api/v1/frameworks/999999",
        "delete",
        ["analyst", "auditor", "employee"],
    ),
    (
        "framework_controls",
        "delete",
        "/api/v1/framework-controls/999999",
        "delete",
        ["analyst", "auditor", "employee"],
    ),
    (
        "control_framework_mappings",
        "delete",
        "/api/v1/control-framework-controls/999999",
        "delete",
        ["analyst", "auditor", "employee"],
    ),
    (
        "evidence",
        "delete",
        "/api/v1/evidence/999999",
        "delete",
        ["manager", "analyst", "auditor", "employee"],
    ),
    (
        "audits",
        "delete",
        "/api/v1/audits/999999",
        "delete",
        ["manager", "analyst", "auditor", "employee"],
    ),
    (
        "audit_findings",
        "delete",
        "/api/v1/audit-findings/999999",
        "delete",
        ["manager", "analyst", "auditor", "employee"],
    ),
    (
        "corrective_actions",
        "delete",
        "/api/v1/corrective-actions/999999",
        "delete",
        ["manager", "analyst", "auditor", "employee"],
    ),
]


@pytest.mark.parametrize(
    "resource,action,endpoint,method,denied_roles",
    MUTATION_PERMISSION_MATRIX,
)
def test_mutation_permission_denial_matrix(
    client,
    users,
    auth_headers,
    resource,
    action,
    endpoint,
    method,
    denied_roles,
):
    """
    Every role explicitly listed as lacking the mutation
    permission must receive 403.

    The request uses a nonexistent object so that an authorized
    role would proceed to the resource layer and return 404.
    """

    for role_key in denied_roles:

        user = users[role_key]

        assert not has_permission(
            user,
            resource,
            action,
        )

        response = client.request(
            method.upper(),
            endpoint,
            headers=auth_headers(user),
        )

        assert response.status_code == 403


# ==========================================================
# 11. CREATE / UPDATE PERMISSION GATES
# ==========================================================

CREATE_PERMISSION_MATRIX = [
    (
        "risks",
        "/api/v1/risks/",
        ["auditor"],
    ),
    (
        "controls",
        "/api/v1/controls/",
        ["auditor", "employee"],
    ),
    (
        "frameworks",
        "/api/v1/frameworks/",
        ["analyst", "auditor", "employee"],
    ),
    (
        "framework_controls",
        "/api/v1/framework-controls/",
        ["analyst", "auditor", "employee"],
    ),
    (
        "control_framework_mappings",
        "/api/v1/control-framework-controls/",
        ["auditor", "employee"],
    ),
    (
        "evidence",
        "/api/v1/evidence/",
        [],
    ),
    (
        "audits",
        "/api/v1/audits/",
        ["analyst", "employee"],
    ),
    (
        "audit_findings",
        "/api/v1/audit-findings/",
        ["analyst", "employee"],
    ),
    (
        "corrective_actions",
        "/api/v1/corrective-actions/",
        ["analyst", "employee"],
    ),
]


@pytest.mark.parametrize(
    "resource,endpoint,denied_roles",
    CREATE_PERMISSION_MATRIX,
)
def test_create_permission_denial_matrix(
    client,
    users,
    auth_headers,
    resource,
    endpoint,
    denied_roles,
):
    """
    Verify the permission layer for create endpoints.

    For denied roles the permission dependency must execute
    before the request can reach business logic.
    """

    for role_key in denied_roles:

        user = users[role_key]

        assert not has_permission(
            user,
            resource,
            "create",
        )

        response = client.post(
            endpoint,
            headers=auth_headers(user),
            json={},
        )

        assert response.status_code == 403


UPDATE_PERMISSION_MATRIX = [
    (
        "risks",
        "/api/v1/risks/999999",
        ["auditor"],
    ),
    (
        "controls",
        "/api/v1/controls/999999",
        ["auditor", "employee"],
    ),
    (
        "frameworks",
        "/api/v1/frameworks/999999",
        ["analyst", "auditor", "employee"],
    ),
    (
        "framework_controls",
        "/api/v1/framework-controls/999999",
        ["analyst", "auditor", "employee"],
    ),
    (
        "evidence",
        "/api/v1/evidence/999999",
        [],
    ),
    (
        "audits",
        "/api/v1/audits/999999",
        ["analyst", "employee"],
    ),
    (
        "audit_findings",
        "/api/v1/audit-findings/999999",
        ["analyst", "employee"],
    ),
    (
        "corrective_actions",
        "/api/v1/corrective-actions/999999",
        ["analyst"],
    ),
]


@pytest.mark.parametrize(
    "resource,endpoint,denied_roles",
    UPDATE_PERMISSION_MATRIX,
)
def test_update_permission_denial_matrix(
    client,
    users,
    auth_headers,
    resource,
    endpoint,
    denied_roles,
):
    """
    Verify that roles without update permission cannot reach
    the underlying resource layer.
    """

    for role_key in denied_roles:

        user = users[role_key]

        assert not has_permission(
            user,
            resource,
            "update",
        )

        response = client.patch(
            endpoint,
            headers=auth_headers(user),
            json={},
        )

        assert response.status_code == 403


# ==========================================================
# 12. AI AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "role_key",
    [
        "analyst",
        "employee",
    ],
)
def test_roles_without_generic_ai_cannot_use_risk_analysis(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.post(
        "/api/v1/ai/risk/999999/analyze",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role_key",
    [
        "analyst",
        "employee",
    ],
)
def test_roles_without_generic_ai_cannot_request_control_recommendations(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.post(
        "/api/v1/ai/risk/999999/recommend-controls",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role_key",
    [
        "analyst",
        "employee",
    ],
)
def test_roles_without_generic_ai_cannot_summarize_audit(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.post(
        "/api/v1/ai/audit/999999/summarize",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


@pytest.mark.parametrize(
    "role_key",
    [
        "admin",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_executive_ai_is_manager_only(
    client,
    users,
    auth_headers,
    role_key,
):
    """
    Executive AI is intentionally a dedicated management-level
    permission.

    Admin must NOT receive this capability.
    """

    response = client.get(
        "/api/v1/ai/dashboard/executive-summary",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 403


def test_executive_ai_permission_is_not_granted_to_admin(
    users,
):
    assert not has_permission(
        users["admin"],
        "ai_executive_summary",
        "use",
    )


def test_executive_ai_permission_is_granted_to_manager(
    users,
):
    assert has_permission(
        users["manager"],
        "ai_executive_summary",
        "use",
    )


# ==========================================================
# 13. DASHBOARD / ACTIVITY / RISK TREND
# ==========================================================

@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/v1/dashboard/",
        "/api/v1/dashboard/activity",
        "/api/v1/dashboard/risk-trend",
    ],
)
@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_dashboard_endpoints_respect_authenticated_access(
    client,
    users,
    auth_headers,
    endpoint,
    role_key,
):
    """
    All current roles have risks:view, which is the permission
    boundary used by the dashboard-related endpoints.
    """

    assert has_permission(
        users[role_key],
        "risks",
        "view",
    )

    response = client.get(
        endpoint,
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 200


# ==========================================================
# 14. NOTIFICATION AUTHORIZATION
# ==========================================================

@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_notifications_require_authentication_but_are_available_to_roles(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.get(
        "/api/v1/notifications/",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_notification_unread_count_requires_authentication(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.get(
        "/api/v1/notifications/unread-count",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 200


# ==========================================================
# 15. AUTHENTICATION BOUNDARY
# ==========================================================

def test_protected_api_rejects_missing_token(
    client,
):
    response = client.get(
        "/api/v1/risks/",
    )

    assert response.status_code == 401


def test_protected_api_rejects_invalid_token(
    client,
):
    response = client.get(
        "/api/v1/risks/",
        headers={
            "Authorization": "Bearer invalid-token",
        },
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_every_supported_role_can_authenticate(
    client,
    users,
    auth_headers,
    role_key,
):
    response = client.get(
        "/api/v1/auth/me",
        headers=auth_headers(users[role_key]),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == users[role_key].id
    assert data["email"] == users[role_key].email
    assert data["role"] == users[role_key].role


# ==========================================================
# 16. PERMISSION / SCOPE CONSISTENCY
# ==========================================================

@pytest.mark.parametrize(
    "role_key",
    ROLE_KEYS,
)
def test_every_permissioned_resource_has_a_defined_scope(
    users,
    role_key,
):
    """
    A role should never have a resource permission while the
    corresponding resource has no defined scope.

    Exceptions are intentionally excluded for authentication
    conveniences such as notifications, which do not currently
    use the permission system.
    """

    user = users[role_key]

    permissions = ROLE_PERMISSIONS.get(
        user.role,
        {},
    )

    scopes = ROLE_SCOPES.get(
        user.role,
        {},
    )

    for resource in permissions:

        if resource == "users":
            assert resource in scopes

        elif resource == "ai_executive_summary":
            assert resource in scopes

        else:
            assert resource in scopes


# ==========================================================
# 17. CORE RBAC INVARIANTS
# ==========================================================

def test_admin_has_organization_scope_for_core_resources(
    users,
):
    admin = users["admin"]

    for resource in [
        "risks",
        "controls",
        "evidence",
        "audits",
        "audit_findings",
        "corrective_actions",
        "reports",
    ]:
        assert get_access_scope(
            admin,
            resource,
        ) == AccessScope.ORGANIZATION


def test_manager_has_subordinate_scope_for_operational_resources(
    users,
):
    manager = users["manager"]

    for resource in [
        "risks",
        "controls",
        "evidence",
        "audits",
        "audit_findings",
        "corrective_actions",
        "reports",
    ]:
        assert get_access_scope(
            manager,
            resource,
        ) == AccessScope.SUBORDINATES


def test_analyst_has_own_scope_for_operational_resources(
    users,
):
    analyst = users["analyst"]

    for resource in [
        "risks",
        "controls",
        "evidence",
        "audits",
        "audit_findings",
        "corrective_actions",
        "reports",
    ]:
        assert get_access_scope(
            analyst,
            resource,
        ) == AccessScope.OWN


def test_auditor_has_organization_scope_for_read_resources(
    users,
):
    auditor = users["auditor"]

    for resource in [
        "risks",
        "controls",
        "evidence",
        "reports",
        "ai",
    ]:
        assert get_access_scope(
            auditor,
            resource,
        ) == AccessScope.ORGANIZATION


def test_employee_has_own_scope_for_personal_work_resources(
    users,
):
    employee = users["employee"]

    for resource in [
        "risks",
        "evidence",
        "corrective_actions",
    ]:
        assert get_access_scope(
            employee,
            resource,
        ) == AccessScope.OWN


# ==========================================================
# 18. NO PRIVILEGE ESCALATION THROUGH ROLE DATA
# ==========================================================

@pytest.mark.parametrize(
    "role_key",
    [
        "manager",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_non_admin_cannot_modify_role_even_with_existing_user_id(
    client,
    users,
    auth_headers,
    role_key,
):
    """
    Direct API access must not allow a non-admin to manipulate
    another user's role.
    """

    response = client.patch(
        f"/api/v1/users/{users['admin'].id}/role",
        headers=auth_headers(users[role_key]),
        json={
            "role": UserRole.ADMIN.value,
        },
    )

    assert response.status_code == 403


# ==========================================================
# 19. OBJECT OWNERSHIP MUST NOT BE BYPASSED
# ==========================================================

@pytest.mark.parametrize(
    "role_key,owner_key",
    [
        ("manager", "admin"),
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
def test_risk_update_outside_scope_is_hidden(
    client,
    users,
    resource_data,
    auth_headers,
    role_key,
    owner_key,
):
    risk = resource_data["risks"][owner_key]

    response = client.patch(
        f"/api/v1/risks/{risk.id}",
        headers=auth_headers(users[role_key]),
        json={
            "title": "Unauthorized update attempt",
        },
    )

    assert response.status_code == 404


# ==========================================================
# 20. RESPONSE-LEVEL VISIBILITY
# ==========================================================

def test_employee_risk_list_contains_only_own_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["employee"]),
    )

    assert response.status_code == 200

    returned_ids = {
        item["id"]
        for item in response.json()
    }

    assert returned_ids == {
        resource_data["risks"]["employee"].id,
    }


def test_analyst_risk_list_contains_only_own_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["analyst"]),
    )

    assert response.status_code == 200

    returned_ids = {
        item["id"]
        for item in response.json()
    }

    assert returned_ids == {
        resource_data["risks"]["analyst"].id,
    }


def test_manager_risk_list_excludes_admin_owned_risk(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["manager"]),
    )

    assert response.status_code == 200

    returned_ids = {
        item["id"]
        for item in response.json()
    }

    assert (
        resource_data["risks"]["admin"].id
        not in returned_ids
    )


def test_auditor_risk_list_is_organization_wide(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["auditor"]),
    )

    assert response.status_code == 200

    returned_ids = {
        item["id"]
        for item in response.json()
    }

    expected_ids = {
        resource_data["risks"]["admin"].id,
        resource_data["risks"]["manager"].id,
        resource_data["risks"]["analyst"].id,
        resource_data["risks"]["auditor"].id,
        resource_data["risks"]["employee"].id,
    }

    assert returned_ids == expected_ids


def test_admin_risk_list_is_organization_wide(
    client,
    users,
    resource_data,
    auth_headers,
):
    response = client.get(
        "/api/v1/risks/",
        headers=auth_headers(users["admin"]),
    )

    assert response.status_code == 200

    returned_ids = {
        item["id"]
        for item in response.json()
    }

    expected_ids = {
        resource_data["risks"]["admin"].id,
        resource_data["risks"]["manager"].id,
        resource_data["risks"]["analyst"].id,
        resource_data["risks"]["auditor"].id,
        resource_data["risks"]["employee"].id,
    }

    assert returned_ids == expected_ids