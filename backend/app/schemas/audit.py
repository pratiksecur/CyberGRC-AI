from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class AuditCreate(BaseModel):
    name: str = Field(..., min_length=5, max_length=255)

    framework_id: int

    auditor_id: int

    scope: str = Field(..., min_length=10)

    status: str = "Planned"

    start_date: date

    end_date: date

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date cannot be before start_date")
        return self


class AuditUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255
    )

    scope: Optional[str] = Field(
        None,
        min_length=10
    )

    status: Optional[str] = None

    start_date: Optional[date] = None

    end_date: Optional[date] = None

    auditor_id: Optional[int] = None


class AuditResponse(BaseModel):
    id: int

    name: str

    framework_id: int

    auditor_id: int

    created_by_id: int

    scope: str

    status: str

    start_date: date

    end_date: date

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }