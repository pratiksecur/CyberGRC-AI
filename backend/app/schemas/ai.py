from typing import List

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)


class _AIBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )


class RiskAnalysisRequest(_AIBaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=255,
    )

    description: str = Field(
        ...,
        min_length=10,
        max_length=4000,
    )


class RiskAnalysisResponse(_AIBaseModel):
    likelihood: str = Field(
        ...,
        pattern=r"^(Low|Medium|High|Critical)$",
    )

    impact: str = Field(
        ...,
        pattern=r"^(Low|Medium|High|Critical)$",
    )

    risk_score: int = Field(
        ...,
        ge=1,
        le=25,
    )

    summary: str = Field(
        ...,
        min_length=30,
        max_length=2000,
    )

    recommended_controls: List[str] = Field(
        ...,
        min_length=3,
        max_length=6,
    )

    @field_validator("recommended_controls")
    @classmethod
    def validate_controls(cls, values):
        if any(
            not item.strip()
            or len(item) > 500
            for item in values
        ):
            raise ValueError(
                "Invalid recommended control text."
            )

        return values


class AIControlRecommendation(_AIBaseModel):
    control_id: int | None = Field(
        default=None,
        ge=1,
    )

    control_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
    )

    already_exists: bool = False

    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
    )

    priority: str = Field(
        ...,
        pattern=r"^(Low|Medium|High|Critical)$",
    )

    reason: str = Field(
        ...,
        min_length=10,
        max_length=2000,
    )


class ControlRecommendationResponse(_AIBaseModel):
    overall_assessment: str = Field(
        ...,
        min_length=10,
        max_length=3000,
    )

    existing_controls_assessment: str = Field(
        ...,
        min_length=10,
        max_length=3000,
    )

    recommended_existing_controls: List[
        AIControlRecommendation
    ] = Field(
        default_factory=list,
        max_length=20,
    )

    recommended_new_controls: List[
        AIControlRecommendation
    ] = Field(
        default_factory=list,
        max_length=20,
    )


class AuditSummaryResponse(_AIBaseModel):
    overall_assessment: str = Field(
        ...,
        min_length=10,
        max_length=3000,
    )

    critical_findings: int = Field(
        ...,
        ge=0,
    )

    open_findings: int = Field(
        ...,
        ge=0,
    )

    completed_actions: int = Field(
        ...,
        ge=0,
    )

    pending_actions: int = Field(
        ...,
        ge=0,
    )

    executive_summary: str = Field(
        ...,
        min_length=20,
        max_length=4000,
    )

    priority_recommendations: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
    )


class ExecutiveDashboardResponse(_AIBaseModel):
    organization_risk_level: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )

    executive_summary: str = Field(
        ...,
        min_length=20,
        max_length=4000,
    )

    top_priorities: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
    )

    recommended_next_steps: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
    )

    # ==========================================================
# CONTINUOUS RISK STATE AI EXPLANATION
# ==========================================================


class AIContinuousRiskStateExplanation(_AIBaseModel):
    explanation: str = Field(
        ...,
        min_length=30,
        max_length=3000,
    )

    key_drivers: List[str] = Field(
        ...,
        min_length=1,
        max_length=8,
    )

    review_areas: List[str] = Field(
        ...,
        min_length=1,
        max_length=8,
    )

    @field_validator(
        "key_drivers",
        "review_areas",
    )
    @classmethod
    def validate_items(cls, values):
        if any(
            not item.strip()
            or len(item) > 500
            for item in values
        ):
            raise ValueError(
                "Invalid explanation item."
            )

        return values


class RiskStateExplanationResponse(_AIBaseModel):
    risk_state: str = Field(
        ...,
        pattern=r"^(CURRENT|DEGRADED|REASSESSMENT_REQUIRED)$",
    )

    treatment_state: str = Field(
        ...,
        pattern=r"^(CURRENT|STALE|DEGRADED|REQUIRES_REASSESSMENT)$",
    )

    reassessment_required: bool

    explanation: str = Field(
        ...,
        min_length=30,
        max_length=3000,
    )

    key_drivers: List[str] = Field(
        ...,
        min_length=1,
        max_length=8,
    )

    review_areas: List[str] = Field(
        ...,
        min_length=1,
        max_length=8,
    )