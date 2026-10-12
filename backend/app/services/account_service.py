"""Password and account-state changes.

These functions raise ValueError with a message that is safe to show the
caller; the routes turn it into a 400 response.
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.auth.hashing import hash_password, verify_password
from app.auth.password_policy import validate_password
from app.core.roles import UserRole
from app.models.user import User


def _sign_out_everywhere(user: User) -> None:
    # Every token issued so far carries the old number and stops working.
    user.token_version = (user.token_version or 0) + 1


def _set_password(user: User, new_password: str) -> None:
    validate_password(
        new_password,
        email=user.email,
        full_name=user.full_name,
    )

    user.hashed_password = hash_password(new_password)
    user.password_changed_at = datetime.now(timezone.utc)

    _sign_out_everywhere(user)


def change_own_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> User:
    """The signed-in user changes their own password."""

    if not verify_password(current_password, user.hashed_password):
        raise ValueError("Current password is incorrect.")

    if current_password == new_password:
        raise ValueError("The new password must be different.")

    _set_password(user, new_password)

    db.commit()
    db.refresh(user)

    return user


def admin_reset_password(
    db: Session,
    admin: User,
    target: User,
    new_password: str,
) -> User:
    """An administrator sets a new password for someone else."""

    if target.id == admin.id:
        raise ValueError(
            "Use the change password option for your own account."
        )

    _set_password(target, new_password)

    db.commit()
    db.refresh(target)

    return target


def _active_admin_count(db: Session, organization_id: int) -> int:
    return (
        db.query(User)
        .filter(
            User.organization_id == organization_id,
            User.role == UserRole.ADMIN.value,
            User.is_active.is_(True),
        )
        .count()
    )


def set_user_active(
    db: Session,
    admin: User,
    target: User,
    active: bool,
) -> User:
    """Deactivate (offboard) or reactivate a user."""

    if not active:
        if target.id == admin.id:
            raise ValueError("You cannot deactivate your own account.")

        if (
            target.role == UserRole.ADMIN.value
            and target.is_active
            and _active_admin_count(db, target.organization_id) <= 1
        ):
            raise ValueError(
                "The last active administrator cannot be deactivated."
            )

    target.is_active = active

    if not active:
        _sign_out_everywhere(target)

    db.commit()
    db.refresh(target)

    return target