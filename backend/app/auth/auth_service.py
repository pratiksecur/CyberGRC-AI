from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.roles import UserRole
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.emails import normalize_email
from app.auth.hashing import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.auth.login_guard import (
    check_login_allowed,
    record_login_attempt,
)
from app.auth.password_policy import validate_password


_dummy_hash: str | None = None


def _burn_password_check(password: str) -> None:
    """
    Spend the same time as a real password check when the email is unknown,
    so response time does not reveal which emails have accounts.
    """

    global _dummy_hash

    if _dummy_hash is None:
        _dummy_hash = hash_password("not-a-real-account-password")

    verify_password(password, _dummy_hash)


def create_user(
    db: Session,
    user: UserCreate,
    *,
    organization_id: int,
    role: str = UserRole.EMPLOYEE.value,
):
    """
    Create a user inside the given organization.

    The organization is always chosen by the caller (the signed-in
    administrator's own organization), never by the request body.
    Emails are stored in lowercase and are unique regardless of case.
    """

    email = normalize_email(user.email)

    validate_password(
        user.password,
        email=email,
        full_name=user.full_name,
    )

    # Check if email already exists (any capitalisation)
    existing_user = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if existing_user:
        raise ValueError("Email already registered.")

    # Create the user
    new_user = User(
        full_name=user.full_name,
        email=email,
        hashed_password=hash_password(user.password),
        role=role,
        organization_id=organization_id,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(
    db: Session,
    email: str,
    password: str,
    *,
    ip_address: str | None = None,
):
    """
    Authenticate a user and return a JWT token.

    Raises LoginBlocked when the email or IP address has failed too many
    times recently (checked before the password is looked at).

    Authentication failures intentionally return the same
    message regardless of whether the email exists, the password is
    incorrect, or the account is deactivated.
    """

    email = normalize_email(email)

    check_login_allowed(db, email, ip_address)

    user = (
        db.query(User)
        .filter(func.lower(User.email) == email)
        .first()
    )

    if not user:
        _burn_password_check(password)

        record_login_attempt(
            db,
            email,
            ip_address,
            success=False,
            reason="unknown_email",
        )

        raise ValueError(
            "Invalid email or password."
        )

    if not verify_password(
        password,
        user.hashed_password,
    ):
        record_login_attempt(
            db,
            email,
            ip_address,
            success=False,
            reason="wrong_password",
        )

        raise ValueError(
            "Invalid email or password."
        )

    if not user.is_active:
        record_login_attempt(
            db,
            email,
            ip_address,
            success=False,
            reason="account_disabled",
        )

        raise ValueError(
            "Invalid email or password."
        )

    record_login_attempt(
        db,
        email,
        ip_address,
        success=True,
    )

    access_token = create_access_token(
        data={
            "sub": user.email,
            "ver": user.token_version,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }