from sqlalchemy.orm import Session

from app.models.control import Control
from app.models.user import User
from app.schemas.control import (
    ControlCreate,
    ControlUpdate,
)


def create_control(
    db: Session,
    control_data: ControlCreate
):
    """
    Create a new control.
    """

    owner = (
        db.query(User)
        .filter(User.id == control_data.owner_id)
        .first()
    )

    if owner is None:
        return None

    control = Control(
        title=control_data.title,
        description=control_data.description,
        control_type=control_data.control_type,
        owner_id=control_data.owner_id,
    )

    db.add(control)

    db.commit()

    db.refresh(control)

    return control


def get_all_controls(db: Session):
    """
    Get all controls.
    """

    return (
        db.query(Control)
        .all()
    )


def get_control_by_id(
    db: Session,
    control_id: int
):
    """
    Get a control by ID.
    """

    return (
        db.query(Control)
        .filter(Control.id == control_id)
        .first()
    )


def update_control(
    db: Session,
    control_id: int,
    control_data: ControlUpdate
):
    """
    Update a control.
    """

    control = (
        db.query(Control)
        .filter(Control.id == control_id)
        .first()
    )

    if control is None:
        return None

    if control_data.owner_id is not None:

        owner = (
            db.query(User)
            .filter(User.id == control_data.owner_id)
            .first()
        )

        if owner is None:
            return "OWNER_NOT_FOUND"

        control.owner_id = control_data.owner_id

    if control_data.title is not None:
        control.title = control_data.title

    if control_data.description is not None:
        control.description = control_data.description

    if control_data.control_type is not None:
        control.control_type = control_data.control_type

    if control_data.status is not None:
        control.status = control_data.status

    db.commit()

    db.refresh(control)

    return control


def delete_control(
    db: Session,
    control_id: int
):
    """
    Delete a control.
    """

    control = (
        db.query(Control)
        .filter(Control.id == control_id)
        .first()
    )

    if control is None:
        return None

    db.delete(control)

    db.commit()

    return True