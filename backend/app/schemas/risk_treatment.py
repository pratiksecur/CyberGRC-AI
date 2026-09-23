from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


class TreatmentStrategy(str, Enum):
    MITIGATE = "Mitigate"
    AVOID = "Avoid"
    TRANSFER = "Transfer"
    ACCEPT = "Accept"


class TreatmentStatus(str, Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class AcceptanceStatus(str, Enum):
    NOT_REQUIRED = "Not Required"
    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class RiskTreatmentCreate(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    risk_id: int = Field(
        ...,
        ge=1,
    )

    strategy: TreatmentStrategy

    status: TreatmentStatus = (
        TreatmentStatus.PLANNED
    )

    treatment_plan: str = Field(
        ...,
        min_length=10,
        max_length=10000,
    )

    owner_id: int = Field(
        ...,
        ge=1,
    )

    target_date: Optional[date] = None

    residual_likelihood: Optional[int] = Field(
        None,
        ge=1,
        le=5,
    )

    residual_impact: Optional[int] = Field(
        None,
        ge=1,
        le=5,
    )

    residual_risk_score: Optional[int] = Field(
        None,
        ge=1,
        le=25,
    )

    acceptance_status: AcceptanceStatus = (
        AcceptanceStatus.NOT_REQUIRED
    )

    acceptance_reason: Optional[str] = Field(
        None,
        max_length=10000,
    )

    accepted_by_id: Optional[int] = Field(
        None,
        ge=1,
    )

    accepted_at: Optional[datetime] = None

    @model_validator(mode="after")
    def validate_treatment(self):
        residual_values = (
            self.residual_likelihood,
            self.residual_impact,
            self.residual_risk_score,
        )

        provided_residual_values = sum(
            value is not None
            for value in residual_values
        )

        if (
            provided_residual_values != 0
            and provided_residual_values != 3
        ):
            raise ValueError(
                "Residual risk assessment must include "
                "residual_likelihood, residual_impact, "
                "and residual_risk_score together."
            )

        if (
            self.residual_likelihood is not None
            and self.residual_impact is not None
            and self.residual_risk_score is not None
        ):
            expected_score = (
                self.residual_likelihood
                * self.residual_impact
            )

            if (
                self.residual_risk_score
                != expected_score
            ):
                raise ValueError(
                    "residual_risk_score must equal "
                    "residual_likelihood multiplied "
                    "by residual_impact."
                )

        if (
            self.strategy
            != TreatmentStrategy.ACCEPT
        ):
            if (
                self.acceptance_status
                != AcceptanceStatus.NOT_REQUIRED
            ):
                raise ValueError(
                    "Acceptance status is only applicable "
                    "to the Accept treatment strategy."
                )

            if self.acceptance_reason is not None:
                raise ValueError(
                    "Acceptance reason is only applicable "
                    "to the Accept treatment strategy."
                )

            if self.accepted_by_id is not None:
                raise ValueError(
                    "accepted_by_id is only applicable "
                    "to the Accept treatment strategy."
                )

            if self.accepted_at is not None:
                raise ValueError(
                    "accepted_at is only applicable "
                    "to the Accept treatment strategy."
                )

        if (
            self.acceptance_status
            == AcceptanceStatus.NOT_REQUIRED
        ):
            if (
                self.acceptance_reason is not None
                or self.accepted_by_id is not None
                or self.accepted_at is not None
            ):
                raise ValueError(
                    "Acceptance details require an "
                    "active acceptance status."
                )

        if (
            self.acceptance_status
            == AcceptanceStatus.PENDING
        ):
            if (
                self.accepted_by_id is not None
                or self.accepted_at is not None
            ):
                raise ValueError(
                    "Pending acceptance cannot have "
                    "accepted_by_id or accepted_at."
                )

        if self.acceptance_status in {
            AcceptanceStatus.APPROVED,
            AcceptanceStatus.REJECTED,
        }:
            if self.accepted_by_id is None:
                raise ValueError(
                    "Approved or rejected acceptance "
                    "requires accepted_by_id."
                )

            if self.accepted_at is None:
                raise ValueError(
                    "Approved or rejected acceptance "
                    "requires accepted_at."
                )

            if (
                self.acceptance_reason is None
                or not self.acceptance_reason.strip()
            ):
                raise ValueError(
                    "Approved or rejected acceptance "
                    "requires an acceptance_reason."
                )

        return self


class RiskTreatmentUpdate(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    strategy: Optional[TreatmentStrategy] = None

    status: Optional[TreatmentStatus] = None

    treatment_plan: Optional[str] = Field(
        None,
        min_length=10,
        max_length=10000,
    )

    owner_id: Optional[int] = Field(
        None,
        ge=1,
    )

    target_date: Optional[date] = None

    residual_likelihood: Optional[int] = Field(
        None,
        ge=1,
        le=5,
    )

    residual_impact: Optional[int] = Field(
        None,
        ge=1,
        le=5,
    )

    residual_risk_score: Optional[int] = Field(
        None,
        ge=1,
        le=25,
    )

    acceptance_status: Optional[
        AcceptanceStatus
    ] = None

    acceptance_reason: Optional[str] = Field(
        None,
        max_length=10000,
    )

    accepted_by_id: Optional[int] = Field(
        None,
        ge=1,
    )

    accepted_at: Optional[datetime] = None


class RiskTreatmentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True
    )

    id: int

    risk_id: int

    strategy: TreatmentStrategy

    status: TreatmentStatus

    treatment_plan: str

    owner_id: int

    target_date: Optional[date]

    residual_likelihood: Optional[int]

    residual_impact: Optional[int]

    residual_risk_score: Optional[int]

    acceptance_status: AcceptanceStatus

    acceptance_reason: Optional[str]

    accepted_by_id: Optional[int]

    accepted_at: Optional[datetime]

    created_at: datetime

    updated_at: datetime