from sqlalchemy.orm import Session

from app.models.risk import Risk


def get_risk_trend(db: Session):
    """
    Return risk trend data.

    Currently returns the total number of risks for
    each month as placeholder data.

    This will later be replaced with a grouped SQL query.
    """

    total_risks = (
        db.query(Risk)
        .count()
    )

    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
    ]

    return [
        {
            "month": month,
            "risks": total_risks,
        }
        for month in months
    ]