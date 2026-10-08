from sqlalchemy.orm import Session

from app.models.framework import Framework
from app.models.framework_control import FrameworkControl
from app.models.user import User

from app.schemas.framework_control import (
    FrameworkControlCreate,
    FrameworkControlUpdate,
)


def create_framework_control(
    db: Session,
    control_data: FrameworkControlCreate,
    current_user: User,
):
    framework = (
        db.query(Framework)
        .filter(
            Framework.id == control_data.framework_id,
            Framework.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if framework is None:
        return "FRAMEWORK_NOT_FOUND"

    existing = (
        db.query(FrameworkControl)
        .filter(
            FrameworkControl.framework_id
            == control_data.framework_id,
            FrameworkControl.control_code
            == control_data.control_code,
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


def get_all_framework_controls(
    db: Session,
    current_user: User,
):
    return (
        db.query(FrameworkControl)
        .join(
            Framework,
            Framework.id
            == FrameworkControl.framework_id,
        )
        .filter(
            Framework.organization_id
            == current_user.organization_id,
        )
        .order_by(
            FrameworkControl.id.asc()
        )
        .all()
    )


def get_framework_control_by_id(
    db: Session,
    control_id: int,
    current_user: User,
):
    return (
        db.query(FrameworkControl)
        .join(
            Framework,
            Framework.id
            == FrameworkControl.framework_id,
        )
        .filter(
            FrameworkControl.id == control_id,
            Framework.organization_id
            == current_user.organization_id,
        )
        .first()
    )


def update_framework_control(
    db: Session,
    control_id: int,
    control_data: FrameworkControlUpdate,
    current_user: User,
):
    control = get_framework_control_by_id(
        db,
        control_id,
        current_user,
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
    control_id: int,
    current_user: User,
):
    control = get_framework_control_by_id(
        db,
        control_id,
        current_user,
    )

    if control is None:
        return None

    db.delete(control)
    db.commit()

    return True