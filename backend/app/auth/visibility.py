from sqlalchemy.orm import Session

from app.models.user import User
from app.core.roles import UserRole
from app.auth.scopes import AccessScope
from app.auth.permissions import get_access_scope


# ==========================================================
# ORGANIZATIONAL VISIBILITY
# ==========================================================

def get_visible_user_ids(
    db: Session,
    current_user: User,
    resource: str | None = None,
) -> list[int]:
    """
    Return the user IDs whose organizational data
    the current user is allowed to see.

    When a resource is provided, visibility is determined
    from ROLE_SCOPES for that specific resource.

    If no resource is provided, the existing role-based
    behavior is preserved for backwards compatibility.
    """

    # ------------------------------------------------------
    # RESOURCE-AWARE VISIBILITY
    # ------------------------------------------------------

    if resource is not None:

        access_scope = get_access_scope(
            current_user,
            resource,
        )

        # No configured scope means no organizational
        # resources are visible.
        if access_scope is None:
            return [current_user.id]

        # --------------------------------------------------
        # ORGANIZATION
        # --------------------------------------------------

        if access_scope == AccessScope.ORGANIZATION:

            users = (
                db.query(User.id)
                .all()
            )

            return [
                user_id
                for (user_id,) in users
            ]

        # --------------------------------------------------
        # OWN
        # --------------------------------------------------

        if access_scope == AccessScope.OWN:

            return [current_user.id]

        # --------------------------------------------------
        # SUBORDINATES
        # --------------------------------------------------

        if access_scope == AccessScope.SUBORDINATES:

            visible_ids = {current_user.id}

            def collect_subordinates(
                manager_id: int,
            ):
                subordinates = (
                    db.query(User.id)
                    .filter(
                        User.manager_id == manager_id
                    )
                    .all()
                )

                for (user_id,) in subordinates:

                    if user_id in visible_ids:
                        continue

                    visible_ids.add(user_id)

                    collect_subordinates(
                        user_id
                    )

            collect_subordinates(
                current_user.id
            )

            return list(visible_ids)

    # ------------------------------------------------------
    # BACKWARDS-COMPATIBLE ROLE VISIBILITY
    # ------------------------------------------------------

    # ADMIN
    if current_user.role == UserRole.ADMIN.value:

        users = (
            db.query(User.id)
            .all()
        )

        return [
            user_id
            for (user_id,) in users
        ]

    # GRC MANAGER / RISK ANALYST
    if current_user.role in {
        UserRole.GRC_MANAGER.value,
        UserRole.RISK_ANALYST.value,
    }:

        visible_ids = {current_user.id}

        def collect_subordinates(
            manager_id: int,
        ):
            subordinates = (
                db.query(User.id)
                .filter(
                    User.manager_id == manager_id
                )
                .all()
            )

            for (user_id,) in subordinates:

                if user_id in visible_ids:
                    continue

                visible_ids.add(user_id)

                collect_subordinates(
                    user_id
                )

        collect_subordinates(
            current_user.id
        )

        return list(visible_ids)

    # AUDITOR / EMPLOYEE
    return [current_user.id]


# ==========================================================
# SINGLE USER VISIBILITY
# ==========================================================

def can_view_user(
    db: Session,
    current_user: User,
    target_user_id: int,
    resource: str | None = None,
) -> bool:
    """
    Determine whether the current user can see
    another user's organizational data.

    When a resource is provided, the resource-specific
    ROLE_SCOPES configuration is used.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        resource,
    )

    return target_user_id in visible_user_ids