from sqlalchemy.orm import Session

from app.models.user import User


def get_all_users(db: Session):
    """
    Retrieve all users from the database.
    """
    return db.query(User).all()


def get_user_by_id(db: Session, user_id: int):
    """
    Retrieve a user by their ID.
    """
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def update_user_role(
    db: Session,
    user_id: int,
    new_role: str
):
    """
    Update a user's role.
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return None

    user.role = new_role

    db.commit()
    db.refresh(user)

    return user


def update_user_organization(
    db: Session,
    user_id: int,
    manager_id: int | None,
    department: str | None
):
    """
    Update a user's organizational hierarchy.

    Allows an administrator to assign:
    - Manager
    - Department
    """

    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )

    if user is None:
        return None

    # A user cannot be their own manager
    if manager_id == user_id:
        raise ValueError(
            "A user cannot be their own manager."
        )

    # Validate manager exists
    if manager_id is not None:

        manager = (
            db.query(User)
            .filter(User.id == manager_id)
            .first()
        )

        if manager is None:
            raise ValueError(
                "Manager not found."
            )

    user.manager_id = manager_id
    user.department = department

    db.commit()
    db.refresh(user)

    return user


def get_visible_users(
    db: Session,
    visible_user_ids: list[int]
):
    """
    Retrieve users that fall within the current user's
    organizational visibility scope.
    """

    if not visible_user_ids:
        return []

    return (
        db.query(User)
        .filter(User.id.in_(visible_user_ids))
        .order_by(User.full_name)
        .all()
    )