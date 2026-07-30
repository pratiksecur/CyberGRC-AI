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

def update_user_role(db: Session, user_id: int, new_role: str):
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