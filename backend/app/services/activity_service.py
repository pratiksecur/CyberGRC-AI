from sqlalchemy.orm import Session

from app.models.risk import Risk


def get_recent_activity(
    db: Session,
    visible_user_ids: list[int],
):
    """
    Get the latest risk activity within the
    authorized organizational scope.
    """

    risks = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(
                visible_user_ids
            )
        )
        .order_by(
            Risk.created_at.desc()
        )
        .limit(10)
        .all()
    )

    return [
        {
            "type": "risk",
            "title": "Risk Created",
            "description": risk.title,
            "time": risk.created_at,
        }
        for risk in risks
    ]