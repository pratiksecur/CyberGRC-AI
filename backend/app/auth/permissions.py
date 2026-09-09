from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.models.user import User
from app.core.roles import UserRole
from app.auth.scopes import AccessScope


# ==========================================================
# ROLE PERMISSIONS
# ==========================================================

ROLE_PERMISSIONS = {

    UserRole.ADMIN.value: {
        "users": {"view", "create", "update", "delete"},
        "risks": {"view", "create", "update", "delete"},
        "controls": {"view", "create", "update", "delete"},
        "frameworks": {"view", "create", "update", "delete"},
        "framework_controls": {"view", "create", "update", "delete"},
        "control_framework_mappings": {"view", "create", "delete"},
        "evidence": {"view", "create", "update", "delete"},
        "audits": {"view", "create", "update", "delete"},
        "audit_findings": {"view", "create", "update", "delete"},
        "corrective_actions": {"view", "create", "update", "delete"},
        "reports": {"view", "create"},
        "ai": {"view", "use"},
    },

    UserRole.GRC_MANAGER.value: {
        "users": {"view"},
        "risks": {"view", "create", "update"},
        "controls": {"view", "create", "update"},
        "frameworks": {"view", "create", "update", "delete"},
        "framework_controls": {"view", "create", "update", "delete"},
        "control_framework_mappings": {"view", "create", "delete"},
        "evidence": {"view", "create", "update"},
        "audits": {"view", "create", "update"},
        "audit_findings": {"view", "create", "update"},
        "corrective_actions": {"view", "create", "update"},
        "reports": {"view", "create"},
        "ai": {"view", "use"},

        # Dedicated management-level AI capability.
        # This is intentionally NOT granted to Admin,
        # Risk Analyst, Auditor, or Employee.
        "ai_executive_summary": {"view", "use"},
    },

    UserRole.RISK_ANALYST.value: {
        "risks": {"view", "create", "update"},
        "controls": {"view", "create", "update"},
        "frameworks": {"view"},
        "framework_controls": {"view"},
        "control_framework_mappings": {"view", "create"},
        "evidence": {"view", "create", "update"},
        "audits": {"view"},
        "audit_findings": {"view"},
        "corrective_actions": {"view"},
        "reports": {"view"},
    },

    UserRole.AUDITOR.value: {
        "risks": {"view"},
        "controls": {"view"},
        "frameworks": {"view"},
        "framework_controls": {"view"},
        "control_framework_mappings": {"view"},
        "evidence": {"view", "create", "update"},
        "audits": {"view", "create", "update"},
        "audit_findings": {"view", "create", "update"},
        "corrective_actions": {"view", "create", "update"},
        "reports": {"view"},
        "ai": {"view", "use"},
    },

    UserRole.EMPLOYEE.value: {
        "risks": {"view", "create", "update"},
        "controls": {"view"},
        "frameworks": {"view"},
        "framework_controls": {"view"},
        "control_framework_mappings": {"view"},
        "evidence": {"view", "create", "update"},
        "audits": {"view"},
        "audit_findings": {"view"},
        "corrective_actions": {"view", "update"},
    },
}


# ==========================================================
# ROLE ACCESS SCOPES
# ==========================================================

ROLE_SCOPES = {

    UserRole.ADMIN.value: {
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

    UserRole.GRC_MANAGER.value: {
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

    UserRole.RISK_ANALYST.value: {
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

    UserRole.AUDITOR.value: {
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

    UserRole.EMPLOYEE.value: {
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


# ==========================================================
# PERMISSION CHECK
# ==========================================================

def has_permission(
    user: User,
    resource: str,
    action: str,
) -> bool:

    role_permissions = ROLE_PERMISSIONS.get(
        user.role,
        {},
    )

    resource_permissions = role_permissions.get(
        resource,
        set(),
    )

    return action in resource_permissions


def get_access_scope(
    user: User,
    resource: str,
) -> AccessScope | None:

    role_scopes = ROLE_SCOPES.get(
        user.role,
        {},
    )

    return role_scopes.get(resource)


# ==========================================================
# REQUIRE PERMISSION
# ==========================================================

def require_permission(
    resource: str,
    action: str,
):

    def permission_checker(
        current_user: User = Depends(get_current_user),
    ):

        if not has_permission(
            current_user,
            resource,
            action,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission to "
                    f"{action} {resource}."
                ),
            )

        return current_user

    return permission_checker


# ==========================================================
# ROLE CHECK
# ==========================================================

def require_roles(*allowed_roles):
    """
    Legacy role-based dependency kept for compatibility.
    """

    def role_checker(
        current_user: User = Depends(get_current_user),
    ):

        allowed_values = [
            role.value
            if hasattr(role, "value")
            else role
            for role in allowed_roles
        ]

        if current_user.role not in allowed_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to perform this action."
                ),
            )

        return current_user

    return role_checker