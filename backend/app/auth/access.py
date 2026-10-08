from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.tenant import (
    ensure_resource_same_organization,
)
from app.auth.visibility import get_visible_user_ids
from app.models.user import User


# ==========================================================
# USER VISIBILITY
# ==========================================================


def ensure_user_in_scope(
    db: Session,
    current_user: User,
    target_user_id: int,
    resource: str | None = None,
) -> User:
    """
    Ensure the target user belongs to both:

    1. the authenticated user's organization
    2. the authenticated user's visibility scope
    """

    target_user = (
        db.query(User)
        .filter(
            User.id == target_user_id,
            User.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Cross-organization access is not permitted."
            ),
        )

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource=resource,
    )

    if target_user.id not in visible_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have access to this user."
            ),
        )

    return target_user


# ==========================================================
# RESOURCE OWNER VISIBILITY
# ==========================================================


def ensure_resource_owner_in_scope(
    db: Session,
    current_user: User,
    owner_id: int,
    resource: str | None = None,
) -> User:
    """
    Ensure the resource owner is inside both the tenant
    and the user's visibility scope.
    """

    return ensure_user_in_scope(
        db=db,
        current_user=current_user,
        target_user_id=owner_id,
        resource=resource,
    )


# ==========================================================
# RESOURCE TENANT ACCESS
# ==========================================================


def ensure_resource_in_tenant(
    current_user: User,
    resource,
) -> None:
    """
    Convert the tenant PermissionError into an HTTP 403.
    """

    try:
        ensure_resource_same_organization(
            current_user,
            resource,
        )
    except PermissionError as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc