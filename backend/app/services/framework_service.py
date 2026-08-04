from sqlalchemy.orm import Session

from app.models.framework import Framework
from app.schemas.framework import (
    FrameworkCreate,
    FrameworkUpdate,
)


def create_framework(
    db: Session,
    framework_data: FrameworkCreate
):
    """
    Create a new compliance framework.
    """

    existing = (
        db.query(Framework)
        .filter(
            Framework.name == framework_data.name
        )
        .first()
    )

    if existing:
        return "FRAMEWORK_EXISTS"

    framework = Framework(
        name=framework_data.name,
        version=framework_data.version,
        description=framework_data.description,
    )

    db.add(framework)

    db.commit()

    db.refresh(framework)

    return framework


def get_all_frameworks(db: Session):
    """
    Get all compliance frameworks.
    """

    return (
        db.query(Framework)
        .all()
    )


def get_framework_by_id(
    db: Session,
    framework_id: int
):
    """
    Get a framework by ID.
    """

    return (
        db.query(Framework)
        .filter(
            Framework.id == framework_id
        )
        .first()
    )


def update_framework(
    db: Session,
    framework_id: int,
    framework_data: FrameworkUpdate
):
    """
    Update a compliance framework.
    """

    framework = (
        db.query(Framework)
        .filter(
            Framework.id == framework_id
        )
        .first()
    )

    if framework is None:
        return None

    if (
        framework_data.name is not None
        and framework_data.name != framework.name
    ):
        existing = (
            db.query(Framework)
            .filter(
                Framework.name == framework_data.name
            )
            .first()
        )

        if existing:
            return "FRAMEWORK_EXISTS"

        framework.name = framework_data.name

    if framework_data.version is not None:
        framework.version = framework_data.version

    if framework_data.description is not None:
        framework.description = framework_data.description

    db.commit()

    db.refresh(framework)

    return framework


def delete_framework(
    db: Session,
    framework_id: int
):
    """
    Delete a compliance framework.
    """

    framework = (
        db.query(Framework)
        .filter(
            Framework.id == framework_id
        )
        .first()
    )

    if framework is None:
        return None

    db.delete(framework)

    db.commit()

    return True