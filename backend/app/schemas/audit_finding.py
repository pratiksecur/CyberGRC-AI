from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class FindingStatus(str, Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    CLOSED = "Closed"


class AuditFindingCreate(BaseModel):
    audit_id: int

    control_id: int

    title: str = Field(
        ...,
        min_length=5,
        max_length=255
    )

    description: str = Field(
        ...,
        min_length=10
    )

    severity: SeverityLevel

    recommendation: str = Field(
        ...,
        min_length=10
    )

    status: FindingStatus = FindingStatus.OPEN


class AuditFindingUpdate(BaseModel):
    audit_id: Optional[int] = None

    control_id: Optional[int] = None

    title: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255
    )

    description: Optional[str] = Field(
        None,
        min_length=10
    )

    severity: Optional[SeverityLevel] = None

    recommendation: Optional[str] = Field(
        None,
        min_length=10
    )

    status: Optional[FindingStatus] = None


class AuditFindingResponse(BaseModel):
    id: int

    audit_id: int
    audit_name: str

    control_id: int
    control_name: str

    title: str

    description: str

    severity: SeverityLevel

    recommendation: str

    status: FindingStatus

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }