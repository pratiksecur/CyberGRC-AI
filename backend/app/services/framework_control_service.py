from sqlalchemy.orm import Session

from app.models.framework import Framework
from app.models.framework_control import FrameworkControl

from app.schemas.framework_control import (
    FrameworkControlCreate,
    FrameworkControlUpdate,
)


def create_framework_control(
    db: Session,
    control_data: FrameworkControlCreate
):
    """
    Create a new framework control.
    """

    framework = (
        db.query(Framework)
        .filter(
            Framework.id == control_data.framework_id
        )
        .first()
    )

    if framework is None:
        return "FRAMEWORK_NOT_FOUND"

    existing = (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.framework_id == control_data.framework_id,
            FrameworkControl.control_code == control_data.control_code
        )
        .first()
    )

    if existing:
        return "CONTROL_EXISTS"

    control = FrameworkControl(
        framework_id=control_data.framework_id,
        control_code=control_data.control_code,
        title=control_data.title,
        description=control_data.description,
    )

    db.add(control)

    db.commit()

    db.refresh(control)

    return control


def get_all_framework_controls(db: Session):
    """
    Get all framework controls.
    """

    return (
        db.query(FrameworkControl)
        .all()
    )


def get_framework_control_by_id(
    db: Session,
    control_id: int
):
    """
    Get framework control by ID.
    """

    return (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.id == control_id
        )
        .first()
    )


def update_framework_control(
    db: Session,
    control_id: int,
    control_data: FrameworkControlUpdate
):
    """
    Update framework control.
    """

    control = (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.id == control_id
        )
        .first()
    )

    if control is None:
        return None

    if control_data.control_code is not None:
        control.control_code = control_data.control_code

    if control_data.title is not None:
        control.title = control_data.title

    if control_data.description is not None:
        control.description = control_data.description

    db.commit()

    db.refresh(control)

    return control


def delete_framework_control(
    db: Session,
    control_id: int
):
    """
    Delete framework control.
    """

    control = (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.id == control_id
        )
        .first()
    )

    if control is None:
        return None

    db.delete(control)

    db.commit()

    return True