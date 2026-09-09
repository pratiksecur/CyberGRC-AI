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

    Authorization and scope validation are handled by
    the API route before this service is called.
    """

    control = (
        db.query(Control)
        .filter(
            Control.id == control_id
        )
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
    control_id: int,
    visible_user_ids: list[int],
):
    """
    Get all framework controls linked to a control.

    The control must belong to a user inside the
    current user's visibility scope.
    """

    control = (
        db.query(Control)
        .filter(
            Control.id == control_id,
            Control.owner_id.in_(visible_user_ids),
        )
        .first()
    )

    if control is None:
        return []

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
    framework_control_id: int,
    visible_user_ids: list[int],
):
    """
    Get all Controls linked to a framework control.

    Only Controls whose owners are inside the current
    user's visibility scope are returned.
    """

    return [
        mapping.control
        for mapping in (
            db.query(ControlFrameworkControl)
            .join(
                Control,
                Control.id == ControlFrameworkControl.control_id
            )
            .filter(
                ControlFrameworkControl.framework_control_id == framework_control_id,
                Control.owner_id.in_(visible_user_ids),
            )
            .all()
        )
    ]


def remove_framework_control_mapping(
    db: Session,
    mapping_id: int,
    visible_user_ids: list[int],
):
    """
    Remove a framework control mapping.

    The mapping can only be deleted when its Control
    owner is inside the current user's visibility scope.
    """

    mapping = (
        db.query(ControlFrameworkControl)
        .filter(
            ControlFrameworkControl.id == mapping_id
        )
        .first()
    )

    if mapping is None:
        return "MAPPING_NOT_FOUND"

    control = (
        db.query(Control)
        .filter(
            Control.id == mapping.control_id
        )
        .first()
    )

    if control is None:
        return "MAPPING_NOT_FOUND"

    if control.owner_id not in visible_user_ids:
        return "MAPPING_OUT_OF_SCOPE"

    db.delete(mapping)
    db.commit()

    return True