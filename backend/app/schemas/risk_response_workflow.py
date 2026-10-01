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