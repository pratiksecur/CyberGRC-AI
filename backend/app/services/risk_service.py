from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.models.user import User
from app.schemas.risk import RiskCreate, RiskUpdate


def create_risk(db: Session, risk_data: RiskCreate):
    """
    Create a new risk.
    """

    owner = (
        db.query(User)
        .filter(User.id == risk_data.owner_id)
        .first()
    )

    if owner is None:
        return None

    risk_score = (
        risk_data.likelihood *
        risk_data.impact
    )

    risk = Risk(
        title=risk_data.title,
        description=risk_data.description,
        likelihood=risk_data.likelihood,
        impact=risk_data.impact,
        risk_score=risk_score,
        owner_id=risk_data.owner_id
    )

    db.add(risk)

    db.commit()

    db.refresh(risk)

    return risk


def get_all_risks(db: Session):
    """
    Get all risks.
    """

    return (
        db.query(Risk)
        .all()
    )

def get_risk_by_id(db: Session, risk_id: int):
    """
    Get a risk by its ID.
    """

    return (
        db.query(Risk)
        .filter(Risk.id == risk_id)
        .first()
    )

def update_risk(
    db: Session,
    risk_id: int,
    risk_data: RiskUpdate
):
    """
    Update an existing risk.
    """

    risk = (
        db.query(Risk)
        .filter(Risk.id == risk_id)
        .first()
    )

    if risk is None:
        return None

    # Validate owner if changed
    if risk_data.owner_id is not None:

        owner = (
            db.query(User)
            .filter(User.id == risk_data.owner_id)
            .first()
        )

        if owner is None:
            return "OWNER_NOT_FOUND"

        risk.owner_id = risk_data.owner_id

    # Update simple fields
    if risk_data.title is not None:
        risk.title = risk_data.title

    if risk_data.description is not None:
        risk.description = risk_data.description

    if risk_data.likelihood is not None:
        risk.likelihood = risk_data.likelihood

    if risk_data.impact is not None:
        risk.impact = risk_data.impact

    if risk_data.status is not None:
        risk.status = risk_data.status

    # Recalculate risk score
    risk.risk_score = (
        risk.likelihood *
        risk.impact
    )

    db.commit()

    db.refresh(risk)

    return risk

def delete_risk(
    db: Session,
    risk_id: int
):
    """
    Delete a risk.
    """

    risk = (
        db.query(Risk)
        .filter(Risk.id == risk_id)
        .first()
    )

    if risk is None:
        return None

    db.delete(risk)

    db.commit()

    return True