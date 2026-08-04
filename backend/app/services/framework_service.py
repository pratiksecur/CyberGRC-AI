from sqlalchemy.orm import Session

from app.models.framework import Framework

from app.schemas.framework import (
    FrameworkCreate,
    FrameworkUpdate,
)

from app.exceptions.exceptions import (
    ResourceNotFound,
    DuplicateResource,
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
        raise DuplicateResource("Framework")

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

    framework = (
        db.query(Framework)
        .filter(
            Framework.id == framework_id
        )
        .first()
    )

    if framework is None:
        raise ResourceNotFound("Framework")

    return framework


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
        raise ResourceNotFound("Framework")

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
            raise DuplicateResource("Framework")

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
        raise ResourceNotFound("Framework")

    db.delete(framework)

    db.commit()

    return True