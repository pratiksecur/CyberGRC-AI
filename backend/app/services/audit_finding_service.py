from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.control import Control
from app.models.audit_finding import AuditFinding

from app.schemas.audit_finding import (
    AuditFindingCreate,
    AuditFindingUpdate,
)


def create_audit_finding(
    db: Session,
    finding_data: AuditFindingCreate
):
    """
    Create a new audit finding.
    """

    audit = (
        db.query(Audit)
        .filter(Audit.id == finding_data.audit_id)
        .first()
    )

    if audit is None:
        return "AUDIT_NOT_FOUND"

    control = (
        db.query(Control)
        .filter(Control.id == finding_data.control_id)
        .first()
    )

    if control is None:
        return "CONTROL_NOT_FOUND"

    finding = AuditFinding(
        audit_id=finding_data.audit_id,
        control_id=finding_data.control_id,
        title=finding_data.title,
        description=finding_data.description,
        severity=finding_data.severity.value,
        recommendation=finding_data.recommendation,
        status=finding_data.status.value,
    )

    db.add(finding)
    db.commit()
    db.refresh(finding)

    return finding


def get_all_audit_findings(db: Session):
    """
    Get all audit findings.
    """

    return db.query(AuditFinding).all()


def get_audit_finding_by_id(
    db: Session,
    finding_id: int
):
    """
    Get audit finding by ID.
    """

    return (
        db.query(AuditFinding)
        .filter(AuditFinding.id == finding_id)
        .first()
    )


def update_audit_finding(
    db: Session,
    finding_id: int,
    finding_data: AuditFindingUpdate
):
    """
    Update an audit finding.
    """

    finding = (
        db.query(AuditFinding)
        .filter(AuditFinding.id == finding_id)
        .first()
    )

    if finding is None:
        return None

    if finding_data.title is not None:
        finding.title = finding_data.title

    if finding_data.description is not None:
        finding.description = finding_data.description

    if finding_data.severity is not None:
        finding.severity = finding_data.severity.value

    if finding_data.recommendation is not None:
        finding.recommendation = finding_data.recommendation

    if finding_data.status is not None:
        finding.status = finding_data.status.value

    db.commit()
    db.refresh(finding)

    return finding


def delete_audit_finding(
    db: Session,
    finding_id: int
):
    """
    Delete an audit finding.
    """

    finding = (
        db.query(AuditFinding)
        .filter(AuditFinding.id == finding_id)
        .first()
    )

    if finding is None:
        return None

    db.delete(finding)
    db.commit()

    return True