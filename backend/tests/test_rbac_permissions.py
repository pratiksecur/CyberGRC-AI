import pytest

from app.auth.permissions import (
    ROLE_PERMISSIONS,
    ROLE_SCOPES,
    has_permission,
    get_access_scope,
)

from app.auth.scopes import AccessScope
from app.core.roles import UserRole


def test_all_roles_exist_in_permission_matrix():
    """
    Every supported CyberGRC-AI role must have an explicit
    permission definition.
    """

    for role in UserRole:
        assert role.value in ROLE_PERMISSIONS


def test_all_roles_exist_in_scope_matrix():
    """
    Every supported CyberGRC-AI role must have an explicit
    scope definition.
    """

    for role in UserRole:
        assert role.value in ROLE_SCOPES


def test_admin_has_full_core_permissions(users):
    admin = users["admin"]

    resources = [
        "users",
        "risks",
        "controls",
        "frameworks",
        "framework_controls",
        "control_framework_mappings",
        "evidence",
        "audits",
        "audit_findings",
        "corrective_actions",
    ]

    actions = {
        "users": {
            "view",
            "create",
            "update",
            "delete",
        },
        "risks": {
            "view",
            "create",
            "update",
            "delete",
        },
        "controls": {
            "view",
            "create",
            "update",
            "delete",
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
    }

    for resource in resources:
        for action in actions[resource]:
            assert has_permission(
                admin,
                resource,
                action,
            )


def test_grc_manager_gets_executive_summary(users):
    manager = users["manager"]

    assert has_permission(
        manager,
        "ai_executive_summary",
        "view",
    )

    assert has_permission(
        manager,
        "ai_executive_summary",
        "use",
    )


@pytest.mark.parametrize(
    "user_key",
    [
        "admin",
        "analyst",
        "auditor",
        "employee",
    ],
)
def test_only_grc_manager_gets_executive_summary(
    users,
    user_key,
):
    user = users[user_key]

    assert not has_permission(
        user,
        "ai_executive_summary",
        "view",
    )

    assert not has_permission(
        user,
        "ai_executive_summary",
        "use",
    )


def test_generic_ai_access(users):
    """
    Generic AI is available to Admin, GRC Manager and Auditor.
    It is not available to Risk Analyst or Employee.
    """

    assert has_permission(
        users["admin"],
        "ai",
        "view",
    )

    assert has_permission(
        users["admin"],
        "ai",
        "use",
    )

    assert has_permission(
        users["manager"],
        "ai",
        "view",
    )

    assert has_permission(
        users["manager"],
        "ai",
        "use",
    )

    assert has_permission(
        users["auditor"],
        "ai",
        "view",
    )

    assert has_permission(
        users["auditor"],
        "ai",
        "use",
    )

    assert not has_permission(
        users["analyst"],
        "ai",
        "view",
    )

    assert not has_permission(
        users["employee"],
        "ai",
        "view",
    )


def test_scope_matrix():
    """
    Validate the high-level scope model defined for the
    current CyberGRC-AI RBAC architecture.
    """

    assert (
        get_access_scope(
            type("UserObject", (), {
                "role": UserRole.ADMIN.value
            })(),
            "risks",
        )
        == AccessScope.ORGANIZATION
    )

    assert (
        get_access_scope(
            type("UserObject", (), {
                "role": UserRole.GRC_MANAGER.value
            })(),
            "risks",
        )
        == AccessScope.SUBORDINATES
    )

    assert (
        get_access_scope(
            type("UserObject", (), {
                "role": UserRole.RISK_ANALYST.value
            })(),
            "risks",
        )
        == AccessScope.OWN
    )

    assert (
        get_access_scope(
            type("UserObject", (), {
                "role": UserRole.AUDITOR.value
            })(),
            "risks",
        )
        == AccessScope.ORGANIZATION
    )

    assert (
        get_access_scope(
            type("UserObject", (), {
                "role": UserRole.EMPLOYEE.value
            })(),
            "risks",
        )
        == AccessScope.OWN
    )