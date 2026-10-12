from sqlalchemy.orm import Session

from app.core.roles import UserRole
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.hashing import hash_password, verify_password
from app.auth.jwt_handler import create_access_token


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
    """

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if existing_user:
        raise ValueError("Email already registered.")

    # Create the user
    new_user = User(
        full_name=user.full_name,
        email=user.email,
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
):
    """
    Authenticate a user and return a JWT token.

    Authentication failures intentionally return the same
    message regardless of whether the email exists or the
    password is incorrect.
    """

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise ValueError(
            "Invalid email or password."
        )

    if not verify_password(
        password,
        user.hashed_password,
    ):
        raise ValueError(
            "Invalid email or password."
        )

    access_token = create_access_token(
        data={
            "sub": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }