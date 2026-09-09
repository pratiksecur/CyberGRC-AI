from sqlalchemy.orm import Session

from app.auth.visibility import get_visible_user_ids
from app.models.audit import Audit
from app.models.control import Control
from app.models.risk import Risk
from app.models.user import User


def get_authorized_risk(
    db: Session,
    current_user: User,
    risk_id: int,
):
    """
    Return a risk only when it is within the authenticated
    user's resource-level visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    return (
        db.query(Risk)
        .filter(
            Risk.id == risk_id,
            Risk.owner_id.in_(visible_user_ids),
        )
        .first()
    )


def get_authorized_audit(
    db: Session,
    current_user: User,
    audit_id: int,
):
    """
    Return an audit only when its assigned auditor is within
    the authenticated user's resource-level visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "audits",
    )

    return (
        db.query(Audit)
        .filter(
            Audit.id == audit_id,
            Audit.auditor_id.in_(visible_user_ids),
        )
        .first()
    )


def get_authorized_controls(
    db: Session,
    current_user: User,
):
    """
    Return only controls that the authenticated user is
    authorized to use as AI context.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "controls",
    )

    return (
        db.query(Control)
        .filter(
            Control.owner_id.in_(visible_user_ids),
        )
        .all()
    )