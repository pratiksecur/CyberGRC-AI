"""Create the first administrator for an organization.

Self-registration is closed: only a signed-in administrator can create
users. On a new installation there is no administrator yet, so create the
first one from the command line:

    docker compose exec backend python -m app.seed.create_admin \\
        --email you@example.com --full-name "Your Name"

The password is asked for interactively and never echoed. The organization
must already exist (a fresh database has organization 1, "Default
Organization").
"""

import argparse
import getpass
import sys

MIN_PASSWORD_LENGTH = 8


def create_admin(
    db,
    *,
    email: str,
    full_name: str,
    password: str,
    organization_id: int = 1,
):
    """Create an Admin user. Raises ValueError on bad input. Commits."""

    from app.core.roles import UserRole
    from app.auth.hashing import hash_password
    from app.models.organization import Organization
    from app.models.user import User

    email = email.strip().lower()
    full_name = full_name.strip()

    if "@" not in email:
        raise ValueError("Enter a valid email address.")

    if len(full_name) < 2:
        raise ValueError("Full name must be at least 2 characters.")

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(
            f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )

    organization = (
        db.query(Organization)
        .filter(Organization.id == organization_id)
        .first()
    )

    if organization is None:
        raise ValueError(f"Organization {organization_id} does not exist.")

    if db.query(User).filter(User.email == email).first() is not None:
        raise ValueError("A user with this email already exists.")

    user = User(
        full_name=full_name,
        email=email,
        hashed_password=hash_password(password),
        role=UserRole.ADMIN.value,
        organization_id=organization.id,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--email", required=True)
    parser.add_argument("--full-name", required=True)
    parser.add_argument("--organization-id", type=int, default=1)
    args = parser.parse_args(argv)

    password = getpass.getpass("Password: ")

    if password != getpass.getpass("Repeat password: "):
        print("The passwords do not match.")
        return 1

    from app.database.database import SessionLocal

    db = SessionLocal()

    try:
        user = create_admin(
            db,
            email=args.email,
            full_name=args.full_name,
            password=password,
            organization_id=args.organization_id,
        )
    except ValueError as error:
        db.rollback()
        print(error)
        return 1
    finally:
        db.close()

    print(
        f"Created administrator {user.email} "
        f"in organization {user.organization_id}."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())