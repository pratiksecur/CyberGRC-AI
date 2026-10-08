from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.control import Control
from app.models.user import User
from app.schemas.evidence import EvidenceCreate, EvidenceUpdate


def create_evidence(
    db: Session,
    evidence_data: EvidenceCreate,
    uploaded_by: int,
):
    """
    Create evidence within the organization of its parent control.

    The organization is derived from the control and authenticated
    uploader. It cannot be supplied by the client.
    """

    control = (
        db.query(Control)
        .filter(
            Control.id == evidence_data.control_id
        )
        .first()
    )

    if control is None:
        return None

    user = (
        db.query(User)
        .filter(User.id == uploaded_by)
        .first()
    )

    if user is None:
        return None

    if (
        control.organization_id is None
        or control.organization_id != user.organization_id
    ):
        return None

    evidence = Evidence(
        organization_id=control.organization_id,
        control_id=evidence_data.control_id,
        title=evidence_data.title,
        description=evidence_data.description,
        file_name=evidence_data.file_name,
        file_path=evidence_data.file_path,
        uploaded_by=uploaded_by,
    )

    db.add(evidence)
    db.commit()
    db.refresh(evidence)

    return evidence


def get_all_evidence(db: Session):
    return db.query(Evidence).all()


def get_evidence_by_id(db: Session, evidence_id: int):
    return (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )


def update_evidence(
    db: Session,
    evidence_id: int,
    evidence_data: EvidenceUpdate,
):
    evidence = (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )

    if not evidence:
        return None

    update_data = evidence_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(evidence, field, value)

    db.commit()
    db.refresh(evidence)

    return evidence


def delete_evidence(db: Session, evidence_id: int):
    evidence = (
        db.query(Evidence)
        .filter(Evidence.id == evidence_id)
        .first()
    )

    if not evidence:
        return None

    db.delete(evidence)
    db.commit()

    return True