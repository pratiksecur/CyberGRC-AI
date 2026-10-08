from sqlalchemy.orm import Session

from app.models.organization import Organization
from app.models.user import User


# ==========================================================
# CURRENT TENANT
# ==========================================================


def get_current_organization(
    db: Session,
    current_user: User,
) -> Organization:
    """
    Return the active organization belonging to the
    authenticated user.
    """

    organization = (
        db.query(Organization)
        .filter(
            Organization.id == current_user.organization_id,
            Organization.is_active.is_(True),
        )
        .first()
    )

    if organization is None:
        raise ValueError(
            "Current user's organization is unavailable."
        )

    return organization


# ==========================================================
# USER TENANT VALIDATION
# ==========================================================


def ensure_same_organization(
    current_user: User,
    target_user: User,
) -> None:
    """
    Ensure that two users belong to the same organization.
    """

    if (
        current_user.organization_id
        != target_user.organization_id
    ):
        raise PermissionError(
            "Cross-organization access is not permitted."
        )


def ensure_organization_id(
    current_user: User,
    organization_id: int,
) -> None:
    """
    Ensure that an organization ID belongs to the
    authenticated user's organization.
    """

    if (
        current_user.organization_id
        != organization_id
    ):
        raise PermissionError(
            "Cross-organization access is not permitted."
        )


# ==========================================================
# RESOURCE TENANT VALIDATION
# ==========================================================


def ensure_resource_same_organization(
    current_user: User,
    resource,
) -> None:
    """
    Ensure that a persisted resource belongs to the
    authenticated user's organization.

    The resource must expose organization_id.
    """

    resource_organization_id = getattr(
        resource,
        "organization_id",
        None,
    )

    if resource_organization_id is None:
        raise PermissionError(
            "Resource organization is unavailable."
        )

    if (
        resource_organization_id
        != current_user.organization_id
    ):
        raise PermissionError(
            "Cross-organization access is not permitted."
        )


def ensure_resource_organization_id(
    current_user: User,
    organization_id: int,
) -> None:
    """
    Ensure that a known resource organization ID belongs
    to the authenticated user's organization.
    """

    ensure_organization_id(
        current_user,
        organization_id,
    )


# ==========================================================
# RELATED RESOURCE TENANT VALIDATION
# ==========================================================


def ensure_related_resources_same_organization(
    current_user: User,
    *resources,
) -> None:
    """
    Ensure all supplied resources belong to the
    authenticated user's organization.
    """

    for resource in resources:
        if resource is None:
            raise PermissionError(
                "Related resource is unavailable."
            )

        ensure_resource_same_organization(
            current_user,
            resource,
        )


# ==========================================================
# TENANT-SAFE QUERY FILTER
# ==========================================================


def apply_tenant_filter(
    query,
    model,
    current_user: User,
):
    """
    Restrict a SQLAlchemy query to the authenticated
    user's organization.
    """

    organization_column = getattr(
        model,
        "organization_id",
        None,
    )

    if organization_column is None:
        raise ValueError(
            f"{model.__name__} does not expose "
            "organization_id."
        )

    return query.filter(
        organization_column
        == current_user.organization_id
    )


# ==========================================================
# TENANT-SAFE RESOURCE LOOKUP
# ==========================================================


def get_tenant_resource(
    db: Session,
    model,
    resource_id: int,
    current_user: User,
):
    """
    Retrieve a resource only when it belongs to the
    authenticated user's organization.

    Returns None when the resource does not exist in the
    current tenant.
    """

    query = apply_tenant_filter(
        db.query(model),
        model,
        current_user,
    )

    return (
        query
        .filter(model.id == resource_id)
        .first()
    )