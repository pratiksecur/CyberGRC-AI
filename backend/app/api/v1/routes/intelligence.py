from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db

from app.auth.permissions import require_permission

from app.models.user import User

from app.schemas.intelligence import (
    GRCIntelligenceOverviewResponse,
    RiskIntelligenceResponse,
)

from app.services.grc_intelligence_service import (
    get_grc_intelligence_overview,
    get_risk_intelligence,
)


router = APIRouter(
    prefix="/intelligence",
    tags=["GRC Intelligence"],
)


# ==========================================================
# RISK INTELLIGENCE
# ==========================================================

@router.get(
    "/risk/{risk_id}",
    response_model=RiskIntelligenceResponse,
)
def get_risk_intelligence_endpoint(
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
    Return scope-aware GRC intelligence for a single risk.

    The risk itself is checked against the user's risk scope.
    Downstream controls, evidence, audits and corrective
    actions are independently filtered using their own
    resource scopes.
    """

    intelligence = get_risk_intelligence(
        db,
        risk_id,
        current_user,
    )

    if intelligence is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    return intelligence


# ==========================================================
# GRC INTELLIGENCE OVERVIEW
# ==========================================================

@router.get(
    "/overview",
    response_model=GRCIntelligenceOverviewResponse,
)
def get_grc_intelligence_overview_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "risks",
            "view",
        )
    ),
):
    """
    Return an aggregated GRC intelligence overview
    limited to the current user's visibility.
    """

    return get_grc_intelligence_overview(
        db,
        current_user,
    )