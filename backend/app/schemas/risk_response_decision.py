from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ==========================================================
# CREATE
# ==========================================================

class RiskResponseDecisionCreate(BaseModel):
    """
    Request a governed decision for the current continuous
    risk response.

    The actual response posture is derived server-side.
    Clients cannot submit or override the decision itself.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    assigned_to_id: int | None = Field(
        default=None,
        gt=0,
    )


# ==========================================================
# HUMAN RESOLUTION
# ==========================================================

class RiskResponseDecisionResolution(BaseModel):
    """
    Human resolution payload used for approval/rejection.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    resolution_reason: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )


class RiskResponseDecisionDefer(BaseModel):
    """
    Human defer payload.

    Deferral always requires:
      - a non-blank reason
      - a future timestamp
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    resolution_reason: str = Field(
        ...,
        min_length=1,
        max_length=4000,
    )

    deferred_until: datetime


# ==========================================================
# RESPONSE
# ==========================================================

class RiskResponseDecisionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int
    risk_id: int

    decision: str
    priority: str
    governance_level: str
    status: str

    human_approval_required: bool
    response_event_key: str

    reason_codes: list[str]

    risk_state: str
    treatment_state: str

    reassessment_required: bool
    response_required: bool

    requested_by_id: int
    assigned_to_id: int | None

    resolution_reason: str | None
    deferred_until: datetime | None

    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None