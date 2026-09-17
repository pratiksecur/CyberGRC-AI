from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.database.database import get_db

from app.models.user import User

from app.schemas.monitoring import (
    MonitoringOverviewResponse,
    RiskMonitoringResponse,
)

from app.services.grc_monitoring_service import (
    get_monitoring_overview,
    get_risk_monitoring,
)


router = APIRouter(
    prefix="/monitoring",
    tags=["GRC Monitoring"],
)


# ==========================================================
# MONITORING OVERVIEW
# ==========================================================

@router.get(
    "/overview",
    response_model=MonitoringOverviewResponse,
)
def monitoring_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Return the current scope-aware GRC monitoring state.
    """

    return get_monitoring_overview(
        db,
        current_user,
    )


# ==========================================================
# RISK MONITORING
# ==========================================================

@router.get(
    "/risk/{risk_id}",
    response_model=RiskMonitoringResponse,
)
def monitoring_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Return monitoring alerts associated with one risk.
    """

    result = get_risk_monitoring(
        db,
        risk_id,
        current_user,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    return result