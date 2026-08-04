from sqlalchemy.orm import Session

from app.models.risk import Risk
from app.models.control import Control
from app.models.risk_control import RiskControl


def assign_control_to_risk(
    db: Session,
    risk_id: int,
    control_id: int
):
    """
    Assign a control to a risk.
    """

    risk = (
        db.query(Risk)
        .filter(Risk.id == risk_id)
        .first()
    )

    if risk is None:
        return "RISK_NOT_FOUND"

    control = (
        db.query(Control)
        .filter(Control.id == control_id)
        .first()
    )

    if control is None:
        return "CONTROL_NOT_FOUND"

    existing_mapping = (
        db.query(RiskControl)
        .filter(
            RiskControl.risk_id == risk_id,
            RiskControl.control_id == control_id
        )
        .first()
    )

    if existing_mapping:
        return "ALREADY_EXISTS"

    mapping = RiskControl(
        risk_id=risk_id,
        control_id=control_id
    )

    db.add(mapping)

    db.commit()

    db.refresh(mapping)

    return mapping


def get_controls_for_risk(
    db: Session,
    risk_id: int
):
    """
    Get all controls assigned to a risk.
    """

    return (
        db.query(Control)
        .join(
            RiskControl,
            Control.id == RiskControl.control_id
        )
        .filter(
            RiskControl.risk_id == risk_id
        )
        .all()
    )


def get_risks_for_control(
    db: Session,
    control_id: int
):
    """
    Get all risks assigned to a control.
    """

    return (
        db.query(Risk)
        .join(
            RiskControl,
            Risk.id == RiskControl.risk_id
        )
        .filter(
            RiskControl.control_id == control_id
        )
        .all()
    )


def remove_control_from_risk(
    db: Session,
    mapping_id: int
):
    """
    Remove a control-risk mapping.
    """

    mapping = (
        db.query(RiskControl)
        .filter(
            RiskControl.id == mapping_id
        )
        .first()
    )

    if mapping is None:
        return None

    db.delete(mapping)

    db.commit()

    return True