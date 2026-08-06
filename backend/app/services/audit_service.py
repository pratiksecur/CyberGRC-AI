from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.framework import Framework
from app.models.user import User

from app.schemas.audit import (
    AuditCreate,
    AuditUpdate,
)


def create_audit(
    db: Session,
    audit_data: AuditCreate
):
    """
    Create a new audit.
    """

    framework = (
        db.query(Framework)
        .filter(
            Framework.id == audit_data.framework_id
        )
        .first()
    )

    if framework is None:
        return "FRAMEWORK_NOT_FOUND"

    auditor = (
        db.query(User)
        .filter(
            User.id == audit_data.auditor_id
        )
        .first()
    )

    if auditor is None:
        return "AUDITOR_NOT_FOUND"

    # Business validation
    if audit_data.end_date < audit_data.start_date:
        return "INVALID_DATES"

    audit = Audit(
        name=audit_data.name,
        framework_id=audit_data.framework_id,
        auditor_id=audit_data.auditor_id,
        scope=audit_data.scope,
        status=audit_data.status,
        start_date=audit_data.start_date,
        end_date=audit_data.end_date,
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    return audit


def get_all_audits(db: Session):
    """
    Get all audits.
    """

    return (
        db.query(Audit)
        .all()
    )


def get_audit_by_id(
    db: Session,
    audit_id: int
):
    """
    Get audit by ID.
    """

    return (
        db.query(Audit)
        .filter(
            Audit.id == audit_id
        )
        .first()
    )


def update_audit(
    db: Session,
    audit_id: int,
    audit_data: AuditUpdate
):
    """
    Update an existing audit.
    """

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == audit_id
        )
        .first()
    )

    if audit is None:
        return None

    if audit_data.name is not None:
        audit.name = audit_data.name

    if audit_data.scope is not None:
        audit.scope = audit_data.scope

    if audit_data.status is not None:
        audit.status = audit_data.status

    if audit_data.start_date is not None:
        audit.start_date = audit_data.start_date

    if audit_data.end_date is not None:
        audit.end_date = audit_data.end_date

    # Validate dates if both are available
    if audit.end_date < audit.start_date:
        return "INVALID_DATES"

    db.commit()
    db.refresh(audit)

    return audit


def delete_audit(
    db: Session,
    audit_id: int
):
    """
    Delete an audit.
    """

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == audit_id
        )
        .first()
    )

    if audit is None:
        return None

    db.delete(audit)
    db.commit()

    return True

def get_total_audits(db: Session):
    """
    Get the total number of audits.
    """

    return (
        db.query(Audit)
        .count()
    )