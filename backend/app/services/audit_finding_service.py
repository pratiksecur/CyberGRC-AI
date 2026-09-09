from sqlalchemy.orm import Session

from app.models.audit import Audit
from app.models.control import Control
from app.models.audit_finding import AuditFinding

from app.schemas.audit_finding import (
    AuditFindingCreate,
    AuditFindingUpdate,
)


def finding_response(
    finding: AuditFinding,
    audit_name: str,
    control_name: str,
):
    """
    Convert an AuditFinding database object
    into the API response structure.
    """

    return {
        "id": finding.id,
        "audit_id": finding.audit_id,
        "audit_name": audit_name,
        "control_id": finding.control_id,
        "control_name": control_name,
        "title": finding.title,
        "description": finding.description,
        "severity": finding.severity,
        "recommendation": finding.recommendation,
        "status": finding.status,
        "created_at": finding.created_at,
        "updated_at": finding.updated_at,
    }


def create_audit_finding(
    db: Session,
    finding_data: AuditFindingCreate,
):
    """
    Create a new audit finding.

    Organizational authorization is handled by the route.
    """

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == finding_data.audit_id
        )
        .first()
    )

    if audit is None:
        return "AUDIT_NOT_FOUND"

    control = (
        db.query(Control)
        .filter(
            Control.id == finding_data.control_id
        )
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

    return finding_response(
        finding,
        audit.name,
        control.title,
    )


def get_all_audit_findings(db: Session):
    """
    Get all audit findings with
    audit and control names.
    """

    results = (
        db.query(
            AuditFinding,
            Audit.name,
            Control.title,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id
        )
        .join(
            Control,
            AuditFinding.control_id == Control.id
        )
        .all()
    )

    return [
        finding_response(
            finding,
            audit_name,
            control_name,
        )
        for finding, audit_name, control_name in results
    ]


def get_audit_finding_by_id(
    db: Session,
    finding_id: int
):
    """
    Get a single audit finding with
    audit and control names.
    """

    result = (
        db.query(
            AuditFinding,
            Audit.name,
            Control.title,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id
        )
        .join(
            Control,
            AuditFinding.control_id == Control.id
        )
        .filter(
            AuditFinding.id == finding_id
        )
        .first()
    )

    if result is None:
        return None

    finding, audit_name, control_name = result

    return finding_response(
        finding,
        audit_name,
        control_name,
    )


def get_findings_for_audit(
    db: Session,
    audit_id: int
):
    """
    Get all findings for an audit.
    """

    results = (
        db.query(
            AuditFinding,
            Audit.name,
            Control.title,
        )
        .join(
            Audit,
            AuditFinding.audit_id == Audit.id
        )
        .join(
            Control,
            AuditFinding.control_id == Control.id
        )
        .filter(
            AuditFinding.audit_id == audit_id
        )
        .all()
    )

    return [
        finding_response(
            finding,
            audit_name,
            control_name,
        )
        for finding, audit_name, control_name in results
    ]


def update_audit_finding(
    db: Session,
    finding_id: int,
    finding_data: AuditFindingUpdate
):
    """
    Update an audit finding.

    Relationship authorization is handled by the route.
    """

    finding = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.id == finding_id
        )
        .first()
    )

    if finding is None:
        return None

    # Update Audit
    if finding_data.audit_id is not None:

        audit = (
            db.query(Audit)
            .filter(
                Audit.id == finding_data.audit_id
            )
            .first()
        )

        if audit is None:
            return "AUDIT_NOT_FOUND"

        finding.audit_id = finding_data.audit_id

    # Update Control
    if finding_data.control_id is not None:

        control = (
            db.query(Control)
            .filter(
                Control.id == finding_data.control_id
            )
            .first()
        )

        if control is None:
            return "CONTROL_NOT_FOUND"

        finding.control_id = finding_data.control_id

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

    audit = (
        db.query(Audit)
        .filter(
            Audit.id == finding.audit_id
        )
        .first()
    )

    control = (
        db.query(Control)
        .filter(
            Control.id == finding.control_id
        )
        .first()
    )

    return finding_response(
        finding,
        audit.name,
        control.title,
    )


def delete_audit_finding(
    db: Session,
    finding_id: int
):
    """
    Delete an audit finding.
    """

    finding = (
        db.query(AuditFinding)
        .filter(
            AuditFinding.id == finding_id
        )
        .first()
    )

    if finding is None:
        return None

    db.delete(finding)
    db.commit()

    return True