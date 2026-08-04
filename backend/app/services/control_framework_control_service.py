from sqlalchemy.orm import Session

from app.models.control import Control
from app.models.framework_control import FrameworkControl
from app.models.control_framework_control import ControlFrameworkControl


def assign_framework_control(
    db: Session,
    control_id: int,
    framework_control_id: int
):
    """
    Assign a framework control to a control.
    """

    control = (
        db.query(Control)
        .filter(Control.id == control_id)
        .first()
    )

    if control is None:
        return "CONTROL_NOT_FOUND"

    framework_control = (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.id == framework_control_id
        )
        .first()
    )

    if framework_control is None:
        return "FRAMEWORK_CONTROL_NOT_FOUND"

    existing = (
        db.query(ControlFrameworkControl)
        .filter(
            ControlFrameworkControl.control_id == control_id,
            ControlFrameworkControl.framework_control_id == framework_control_id
        )
        .first()
    )

    if existing:
        return "MAPPING_EXISTS"

    mapping = ControlFrameworkControl(
        control_id=control_id,
        framework_control_id=framework_control_id
    )

    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    return mapping


def get_framework_controls_for_control(
    db: Session,
    control_id: int
):
    """
    Get all framework controls linked to a control.
    """

    return [
        mapping.framework_control
        for mapping in (
            db.query(ControlFrameworkControl)
            .filter(
                ControlFrameworkControl.control_id == control_id
            )
            .all()
        )
    ]


def get_controls_for_framework_control(
    db: Session,
    framework_control_id: int
):
    """
    Get all controls linked to a framework control.
    """

    return [
        mapping.control
        for mapping in (
            db.query(ControlFrameworkControl)
            .filter(
                ControlFrameworkControl.framework_control_id == framework_control_id
            )
            .all()
        )
    ]


def remove_framework_control_mapping(
    db: Session,
    mapping_id: int
):
    """
    Remove framework control mapping.
    """

    mapping = (
        db.query(ControlFrameworkControl)
        .filter(
            ControlFrameworkControl.id == mapping_id
        )
        .first()
    )

    if mapping is None:
        return None

    db.delete(mapping)
    db.commit()

    return True