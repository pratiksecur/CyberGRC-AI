from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.auth.visibility import get_visible_user_ids
from app.database.database import get_db
from app.models.user import User
from app.schemas.risk_trend import RiskTrendResponse
from app.services.risk_trend_service import get_risk_trend


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get(
    "/risk-trend",
    response_model=list[RiskTrendResponse],
)
def risk_trend(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission("risks", "view")
    ),
):
    """
    Return risk creation history within the
    authenticated user's risk visibility scope.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    return get_risk_trend(
        db,
        visible_user_ids,
    )