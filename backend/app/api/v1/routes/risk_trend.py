from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.risk_trend import RiskTrendResponse
from app.services.risk_trend_service import get_risk_trend

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/risk-trend",
    response_model=list[RiskTrendResponse],
)
def risk_trend(
    db: Session = Depends(get_db),
):
    """
    Get dashboard risk trend.
    """

    return get_risk_trend(db)