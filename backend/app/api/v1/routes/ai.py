from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.auth.ai_access import (
    get_authorized_audit,
    get_authorized_risk,
)
from app.auth.visibility import get_visible_user_ids
from app.database.database import get_db
from app.models.user import User

from app.schemas.ai import (
    RiskAnalysisResponse,
    ControlRecommendationResponse,
    AuditSummaryResponse,
    ExecutiveDashboardResponse,
    RiskStateExplanationResponse,
    WorkflowIntelligenceExplanationResponse,
)

from app.schemas.ai_grc_analyst import (
    AIGRCAnalystRequest,
    AIGRCAnalystResponse,
)

from app.services.ai.risk_ai_service import analyze_risk
from app.services.ai.control_ai_service import recommend_controls
from app.services.ai.executive_dashboard_ai_service import (
    generate_executive_dashboard,
)

from app.services.ai.continuous_risk_state_ai_service import (
    explain_continuous_risk_state,
)

from app.services.ai.risk_response_workflow_ai_service import (
    explain_risk_response_workflow,
)

from app.services.ai.audit_ai_service import summarize_audit

from app.services.ai_grc_analyst_ai_service import (
    analyze_with_ai,
)


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
# CONTINUOUS RISK STATE EXPLANATION
# ==========================================================

@router.post(
    "/risk/{risk_id}/state-explanation",
    response_model=RiskStateExplanationResponse,
)
def explain_risk_state(
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
    Explain the deterministic continuous risk state
    using governed AI.

    The deterministic state is calculated by the GRC
    intelligence layer. AI is used only to explain
    the state and identify human review areas.
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

    return explain_continuous_risk_state(
        db=db,
        risk_id=risk_id,
        current_user=current_user,
    )


# ==========================================================
# PHASE 61.9 - WORKFLOW INTELLIGENCE EXPLANATION
# ==========================================================

@router.post(
    "/risk/{risk_id}/response-workflows/{workflow_id}/explanation",
    response_model=WorkflowIntelligenceExplanationResponse,
)
def explain_response_workflow(
    risk_id: int,
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "ai",
            "use",
        )
    ),
):
    """
    Explain deterministic workflow intelligence using governed AI.

    AI only explains the workflow intelligence. It does not
    modify or execute the workflow.
    """

    return explain_risk_response_workflow(
        db=db,
        risk_id=risk_id,
        workflow_id=workflow_id,
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


# ==========================================================
# PHASE 65 — AI GRC ANALYST
# ==========================================================

@router.post(
    "/grc-analyst",
    response_model=AIGRCAnalystResponse,
)
def analyze_grc_question(
    request: AIGRCAnalystRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_permission(
            "ai",
            "use",
        )
    ),
):
    """
    Analyze an enterprise GRC question using governed AI.

    The analyst receives only visibility-filtered GRC
    intelligence.

    AI is advisory only. It does not modify, execute,
    approve, or remediate GRC resources.
    """

    visible_user_ids = get_visible_user_ids(
        db,
        current_user,
        "risks",
    )

    return analyze_with_ai(
        db=db,
        question=request.question,
        visible_user_ids=visible_user_ids,
    )