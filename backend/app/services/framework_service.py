from sqlalchemy.orm import Session

from app.models.framework import Framework
from app.models.user import User

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
    framework_data: FrameworkCreate,
    current_user: User,
):
    """
    Create a framework inside the authenticated user's organization.
    """

    organization_id = current_user.organization_id

    if organization_id is None:
        raise ResourceNotFound("Organization")

    existing = (
        db.query(Framework)
        .filter(
            Framework.organization_id == organization_id,
            Framework.name == framework_data.name,
        )
        .first()
    )

    if existing:
        raise DuplicateResource("Framework")

    framework = Framework(
        organization_id=organization_id,
        name=framework_data.name,
        version=framework_data.version,
        description=framework_data.description,
    )

    db.add(framework)

    db.commit()

    db.refresh(framework)

    return framework


def get_all_frameworks(
    db: Session,
    current_user: User,
):
    """
    Return only frameworks belonging to the user's organization.
    """

    return (
        db.query(Framework)
        .filter(
            Framework.organization_id
            == current_user.organization_id
        )
        .order_by(
            Framework.name.asc(),
            Framework.id.asc(),
        )
        .all()
    )


def get_framework_by_id(
    db: Session,
    framework_id: int,
    current_user: User,
):
    """
    Return a framework only if it belongs to the user's organization.
    """

    framework = (
        db.query(Framework)
        .filter(
            Framework.id == framework_id,
            Framework.organization_id
            == current_user.organization_id,
        )
        .first()
    )

    if framework is None:
        raise ResourceNotFound("Framework")

    return framework


def update_framework(
    db: Session,
    framework_id: int,
    framework_data: FrameworkUpdate,
    current_user: User,
):
    """
    Update a framework only inside the authenticated user's organization.
    """

    framework = get_framework_by_id(
        db,
        framework_id,
        current_user,
    )

    if (
        framework_data.name is not None
        and framework_data.name != framework.name
    ):
        existing = (
            db.query(Framework)
            .filter(
                Framework.organization_id
                == current_user.organization_id,
                Framework.name
                == framework_data.name,
                Framework.id != framework.id,
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
    framework_id: int,
    current_user: User,
):
    """
    Delete a framework only inside the authenticated user's organization.
    """

    framework = get_framework_by_id(
        db,
        framework_id,
        current_user,
    )

    db.delete(framework)

    db.commit()

    return True