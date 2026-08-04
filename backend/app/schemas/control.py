from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ControlCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)

    description: str = Field(..., min_length=10)

    control_type: str = Field(...)

    owner_id: int


class ControlUpdate(BaseModel):
    title: Optional[str] = Field(
        None,
        min_length=5,
        max_length=255
    )

    description: Optional[str] = Field(
        None,
        min_length=10
    )

    control_type: Optional[str] = None

    status: Optional[str] = None

    owner_id: Optional[int] = None


class ControlResponse(BaseModel):
    id: int

    title: str

    description: str

    control_type: str

    status: str

    owner_id: int

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }