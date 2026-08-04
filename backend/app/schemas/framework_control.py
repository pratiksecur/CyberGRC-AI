from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FrameworkControlCreate(BaseModel):
    framework_id: int

    control_code: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    title: str = Field(
        ...,
        min_length=3,
        max_length=255
    )

    description: str = Field(
        ...,
        min_length=10
    )


class FrameworkControlUpdate(BaseModel):
    control_code: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50
    )

    title: Optional[str] = Field(
        None,
        min_length=3,
        max_length=255
    )

    description: Optional[str] = Field(
        None,
        min_length=10
    )


class FrameworkControlResponse(BaseModel):
    id: int

    framework_id: int

    control_code: str

    title: str

    description: str

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }