from datetime import date, datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class PriorityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class ActionStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class CorrectiveActionCreate(BaseModel):
    finding_id: int

    assigned_to: int

    title: str = Field(..., min_length=5, max_length=255)

    description: str = Field(..., min_length=10)

    priority: PriorityLevel

    status: ActionStatus = ActionStatus.OPEN

    due_date: date

    completed_at: Optional[date] = None

    comments: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.completed_at is not None
            and self.completed_at < self.due_date
        ):
            raise ValueError(
                "completed_at cannot be before due_date"
            )
        return self


class CorrectiveActionUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255
    )

    description: Optional[str] = Field(
        None,
        min_length=10
    )

    priority: Optional[PriorityLevel] = None

    status: Optional[ActionStatus] = None

    due_date: Optional[date] = None

    completed_at: Optional[date] = None

    comments: Optional[str] = None

    @model_validator(mode="after")
    def validate_dates(self):
        if (
            self.completed_at is not None
            and self.due_date is not None
            and self.completed_at < self.due_date
        ):
            raise ValueError(
                "completed_at cannot be before due_date"
            )
        return self


class CorrectiveActionResponse(BaseModel):
    id: int

    finding_id: int

    assigned_to: int

    title: str

    description: str

    priority: PriorityLevel

    status: ActionStatus

    due_date: date

    completed_at: Optional[date]

    comments: Optional[str]

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }