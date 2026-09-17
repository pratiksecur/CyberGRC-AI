from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.auth.ai_access import (
    get_authorized_audit,
    get_authorized_risk,
)
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
from app.services.ai.audit_ai_service import summarize_audit


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# ==========================================================
# RISK ANALYSIS
# ==========================================================

@router.post(
    "/risk/{risk_id}/analyze",
    response_model=RiskAnalysisResponse,
)
def analyze_existing_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "ai",
            "use",
        )
    ),
):
    """
    Analyze an authorized risk using AI.
    """

    risk = get_authorized_risk(
        db,
        current_user,
        risk_id,
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    return analyze_risk(
        db=db,
        risk_id=risk_id,
        current_user=current_user,
    )


# ==========================================================
# CONTROL RECOMMENDATIONS
# ==========================================================

@router.post(
    "/risk/{risk_id}/recommend-controls",
    response_model=ControlRecommendationResponse,
)
def recommend_controls_for_risk(
    risk_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "ai",
            "use",
        )
    ),
):
    """
    Recommend controls using only authorized GRC context.
    """

    risk = get_authorized_risk(
        db,
        current_user,
        risk_id,
    )

    if risk is None:
        raise HTTPException(
            status_code=404,
            detail="Risk not found.",
        )

    return recommend_controls(
        db=db,
        risk_id=risk_id,
        current_user=current_user,
    )


# ==========================================================
# AUDIT SUMMARY
# ==========================================================

@router.post(
    "/audit/{audit_id}/summarize",
    response_model=AuditSummaryResponse,
)
def summarize_existing_audit(
    audit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "ai",
            "use",
        )
    ),
):
    """
    Summarize an audit only when it is within
    the authenticated user's audit scope.

    Authorization is also enforced inside the service
    layer as defense-in-depth.
    """

    audit = get_authorized_audit(
        db,
        current_user,
        audit_id,
    )

    if audit is None:
        raise HTTPException(
            status_code=404,
            detail="Audit not found.",
        )

    return summarize_audit(
        db=db,
        audit_id=audit_id,
        current_user=current_user,
    )


# ==========================================================
# EXECUTIVE AI SUMMARY
# ==========================================================

@router.get(
    "/dashboard/executive-summary",
    response_model=ExecutiveDashboardResponse,
)
def executive_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "ai_executive_summary",
            "use",
        )
    ),
):
    """
    Generate the management-level AI Executive Summary.

    This is intentionally a dedicated permission rather than
    generic AI access.

    According to the CyberGRC-AI RBAC architecture, this
    capability belongs to the GRC Manager dashboard.
    """

    return generate_executive_dashboard(
        db=db,
        current_user=current_user,
    )