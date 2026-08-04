from sqlalchemy.orm import Session

from app.models.control import Control
from app.models.user import User
from app.models.evidence import Evidence

from app.schemas.evidence import (
    EvidenceCreate,
    EvidenceUpdate,
)


def create_evidence(
    db: Session,
    evidence_data: EvidenceCreate
):
    """
    Create new evidence.
    """

    control = (
        db.query(Control)
        .filter(Control.id == evidence_data.control_id)
        .first()
    )

    if control is None:
        return "CONTROL_NOT_FOUND"

    user = (
        db.query(User)
        .filter(User.id == evidence_data.uploaded_by)
        .first()
    )

    if user is None:
        return "USER_NOT_FOUND"

    evidence = Evidence(
        control_id=evidence_data.control_id,
        title=evidence_data.title,
        description=evidence_data.description,
        file_name=evidence_data.file_name,
        file_path=evidence_data.file_path,
        uploaded_by=evidence_data.uploaded_by,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


def get_all_evidence(db: Session):
    """
    Get all evidence.
    """

    return (
        db.query(Evidence)
        .all()
    )


def get_evidence_by_id(
    db: Session,
    evidence_id: int
):
    """
    Get evidence by ID.
    """

    return (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )


def update_evidence(
    db: Session,
    evidence_id: int,
    evidence_data: EvidenceUpdate
):
    """
    Update evidence.
    """

    evidence = (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )

    if evidence is None:
        return None

    if evidence_data.title is not None:
        evidence.title = evidence_data.title

    if evidence_data.description is not None:
        evidence.description = evidence_data.description

    if evidence_data.file_name is not None:
        evidence.file_name = evidence_data.file_name

    if evidence_data.file_path is not None:
        evidence.file_path = evidence_data.file_path

    db.commit()
    db.refresh(evidence)

    return evidence


def delete_evidence(
    db: Session,
    evidence_id: int
):
    """
    Delete evidence.
    """

    evidence = (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )

    if evidence is None:
        return None

    db.delete(evidence)
    db.commit()

    return True