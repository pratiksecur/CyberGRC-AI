from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.auth.visibility import get_visible_user_ids


# ==========================================================
# USER SCOPE VALIDATION
# ==========================================================

def ensure_user_in_scope(
    db: Session,
    current_user: User,
    target_user_id: int,
    resource: str | None = None,
) -> None:
    """
    Ensure that the target user falls within the
    current user's organizational visibility scope.

    When a resource is provided, the resource-specific
    ROLE_SCOPES configuration is used. When omitted, the
    legacy visibility behaviour is preserved for callers
    that have not yet been migrated to resource-aware scope.

    Raises:
        HTTPException(403) if the target user is
        outside the current user's scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource,
    )

    if target_user_id not in visible_user_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You cannot access or assign resources "
                "outside your organizational scope."
            )
        )


# ==========================================================
# RESOURCE OWNERSHIP VALIDATION
# ==========================================================

def ensure_resource_owner_in_scope(
    db: Session,
    current_user: User,
    owner_id: int,
    resource: str | None = None,
) -> None:
    """
    Ensure that a resource owner belongs to the
    current user's visibility scope for the resource.

    This is useful when creating or reassigning
    resources such as Risks or Controls.
    """

    ensure_user_in_scope(
        db,
        current_user,
        owner_id,
        resource,
    )