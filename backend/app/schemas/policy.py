from datetime import date, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


PolicyStatus = Literal[
    "Draft",
    "Active",
    "Retired",
]


class PolicyCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    owner_id: int

    name: str = Field(
        min_length=2,
        max_length=255,
    )

    version: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str = Field(
        min_length=10,
    )

    status: PolicyStatus = "Draft"

    effective_date: date | None = None

    review_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.effective_date is not None
            and self.review_date is not None
            and self.review_date < self.effective_date
        ):
            raise ValueError(
                "review_date cannot be earlier than effective_date."
            )

        return self


class PolicyUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    owner_id: int | None = None

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
    )

    version: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    description: str | None = Field(
        default=None,
        min_length=10,
    )

    status: PolicyStatus | None = None

    effective_date: date | None = None

    review_date: date | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.effective_date is not None
            and self.review_date is not None
            and self.review_date < self.effective_date
        ):
            raise ValueError(
                "review_date cannot be earlier than effective_date."
            )

        return self


class PolicyResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    organization_id: int
    owner_id: int
    name: str
    version: str
    description: str
    status: PolicyStatus
    effective_date: date | None
    review_date: date | None
    created_at: datetime
    updated_at: datetime