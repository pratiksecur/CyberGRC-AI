from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RiskResponseWorkflowResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    execution_id: int
    decision_id: int
    risk_id: int
    workflow_type: str
    status: str
    target_type: str
    target_id: int | None
    title: str
    description: str
    created_by_id: int

    updated_by_id: int | None
    resolution_reason: str | None

    started_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None

    created_at: datetime
    updated_at: datetime


class RiskResponseWorkflowTransitionRequest(BaseModel):
    status: Literal[
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED",
    ]

    resolution_reason: str | None = Field(
        default=None,
        max_length=5000,
    )


# ==========================================================
# PHASE 61.7
# WORKFLOW INTELLIGENCE API RESPONSE
# ==========================================================

class RiskResponseWorkflowIntelligenceResponse(BaseModel):
    """
    Read-only intelligence representation for a governed
    risk-response workflow.

    This schema exposes deterministic workflow intelligence
    derived by the Phase 61 intelligence service.

    It does not represent a workflow mutation or execution.
    """

    workflow_id: int
    risk_id: int

    status: str

    health: str

    age_days: float
    age_seconds: float

    attention_required: bool

    reason_codes: list[str]

    started: bool
    terminal: bool

    # ------------------------------------------------------
    # Phase 61.2
    # Lifecycle timing
    # ------------------------------------------------------

    time_to_start_seconds: float | None
    time_in_progress_seconds: float | None
    lifecycle_duration_seconds: float
    terminal_age_seconds: float | None

    # ------------------------------------------------------
    # Phase 61.3
    # Priority intelligence
    # ------------------------------------------------------

    decision_priority: str | None
    priority_rank: int | None
    governance_level: str | None
    priority_requires_attention: bool
    priority_reason_codes: list[str]

    # ------------------------------------------------------
    # Phase 61.4
    # Bottleneck intelligence
    # ------------------------------------------------------

    bottlenecked: bool
    bottleneck_reason_codes: list[str]

    # ------------------------------------------------------
    # Phase 61.5
    # Escalation intelligence
    # ------------------------------------------------------

    escalation_recommendation: str
    escalation_reason_codes: list[str]
    escalation_requires_human_review: bool

    # ------------------------------------------------------
    # Phase 61.6
    # Dependency intelligence
    # ------------------------------------------------------

    dependency_state: str
    dependency_reason_codes: list[str]
    dependency_target_type: str | None
    dependency_target_id: int | None