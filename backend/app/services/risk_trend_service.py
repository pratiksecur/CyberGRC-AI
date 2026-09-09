from datetime import datetime

from sqlalchemy.orm import Session

from app.models.risk import Risk


def _add_months(
    value: datetime,
    months: int,
) -> datetime:
    """
    Return the first day of a month offset from value.
    """

    month_index = (
        value.year * 12
        + (value.month - 1)
        + months
    )

    year = month_index // 12

    month = (
        month_index % 12
    ) + 1

    return value.replace(
        year=year,
        month=month,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def get_risk_trend(
    db: Session,
    visible_user_ids: list[int],
):
    """
    Return the number of risks created in each of the
    last six calendar months.

    We intentionally report creation history rather than
    pretending current status values represent historical
    open/closed state.
    """

    current_month = datetime.now().replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    months = [
        _add_months(
            current_month,
            offset,
        )
        for offset in range(-5, 1)
    ]

    start_date = months[0]

    end_date = _add_months(
        current_month,
        1,
    )

    risks = (
        db.query(Risk)
        .filter(
            Risk.owner_id.in_(
                visible_user_ids
            ),
            Risk.created_at >= start_date,
            Risk.created_at < end_date,
        )
        .all()
    )

    counts = {
        month.strftime("%Y-%m"): 0
        for month in months
    }

    for risk in risks:

        if risk.created_at is None:
            continue

        key = risk.created_at.strftime(
            "%Y-%m"
        )

        if key in counts:
            counts[key] += 1

    return [
        {
            "month": month.strftime("%b"),
            "risks": counts[
                month.strftime("%Y-%m")
            ],
        }
        for month in months
    ]