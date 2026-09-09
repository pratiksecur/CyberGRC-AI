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
) -> None:
    """
    Ensure that the target user falls within the
    current user's organizational visibility scope.

    Raises:
        HTTPException(403) if the target user is
        outside the current user's scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user
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
) -> None:
    """
    Ensure that a resource owner belongs to the
    current user's organizational visibility scope.

    This is useful when creating or reassigning
    resources such as Risks, Controls, or Evidence.
    """

    ensure_user_in_scope(
        db,
        current_user,
        owner_id
    )