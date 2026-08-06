from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.database.database import get_db
from app.models.user import User

from app.schemas.ai import (
    RiskAnalysisResponse,
    ControlRecommendationResponse,
    AuditSummaryResponse,
    ExecutiveDashboardResponse,
)

from app.services.ai.risk_ai_service import analyze_risk
from app.services.ai.control_ai_service import recommend_controls
from app.services.ai.executive_dashboard_ai_service import (
    generate_executive_dashboard,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post(
    "/risk/{risk_id}/analyze",
    response_model=RiskAnalysisResponse,
)
def analyze_existing_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    ),
):
    """
    Analyze an existing risk stored in the database using AI.
    """

    return analyze_risk(
        db=db,
        risk_id=risk_id,
    )


@router.post(
    "/risk/{risk_id}/recommend-controls",
    response_model=ControlRecommendationResponse,
)
def recommend_controls_for_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    ),
):
    """
    Recommend additional cybersecurity controls
    for an existing risk.
    """

    return recommend_controls(
        db=db,
        risk_id=risk_id,
    )

@router.post(
    "/audit/{audit_id}/summarize",
    response_model=AuditSummaryResponse,
)
def summarize_existing_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    ),
):
    """
    Generate an AI executive summary
    for an existing audit.
    """

    return summarize_audit(
        db=db,
        audit_id=audit_id,
    )

@router.get(
    "/dashboard/executive-summary",
    response_model=ExecutiveDashboardResponse,
)
def executive_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(
            UserRole.ADMIN,
            UserRole.GRC_MANAGER,
            UserRole.AUDITOR,
        )
    ),
):
    """
    Generate an AI-powered executive dashboard summary.
    """

    return generate_executive_dashboard(
        db=db,
    )