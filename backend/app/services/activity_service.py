from sqlalchemy.orm import Session

from app.models.risk import Risk


def get_recent_activity(db: Session):
    """
    Get the latest risk activities.
    """

    risks = (
        db.query(Risk)
        .order_by(Risk.created_at.desc())
        .limit(10)
        .all()
    )

    activities = []

    for risk in risks:
        activities.append(
            {
                "type": "risk",
                "title": "Risk Created",
                "description": risk.title,
                "time": risk.created_at,
            }
        )

    return activities