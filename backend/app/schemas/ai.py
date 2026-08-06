from typing import List

from pydantic import BaseModel, Field


# ==========================================================
# Risk Analysis
# ==========================================================

class RiskAnalysisRequest(BaseModel):
    """
    Request schema for AI risk analysis.
    """

    title: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

    description: str = Field(
        ...,
        min_length=10
    )


class RiskAnalysisResponse(BaseModel):
    """
    Structured AI response for risk analysis.
    """

    likelihood: str

    impact: str

    risk_score: int

    summary: str

    recommended_controls: List[str]


# ==========================================================
# Control Recommendation
# ==========================================================

class AIControlRecommendation(BaseModel):
    """
    A control recommended by the AI.
    """

    control_id: int | None = None

    control_name: str

    already_exists: bool = False

    confidence: float = 0.0

    priority: str

    reason: str


class ControlRecommendationResponse(BaseModel):
    """
    AI response for control recommendations.
    """

    overall_assessment: str

    existing_controls_assessment: str

    recommended_existing_controls: List[
        AIControlRecommendation
    ]

    recommended_new_controls: List[
        AIControlRecommendation
    ]

# ==========================================================
# Audit Summary
# ==========================================================

class AuditSummaryResponse(BaseModel):
    """
    AI-generated executive audit summary.
    """

    overall_assessment: str

    critical_findings: int

    open_findings: int

    completed_actions: int

    pending_actions: int

    executive_summary: str

    priority_recommendations: List[str]

# ==========================================================
# Executive Dashboard
# ==========================================================

class ExecutiveDashboardResponse(BaseModel):

    organization_risk_level: str

    executive_summary: str

    top_priorities: List[str]

    recommended_next_steps: List[str]