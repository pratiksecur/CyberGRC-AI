from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FrameworkCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    version: str = Field(
        ...,
        min_length=1,
        max_length=50
    )

    description: str = Field(
        ...,
        min_length=10
    )


class FrameworkUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100
    )

    version: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50
    )

    description: Optional[str] = Field(
        None,
        min_length=10
    )


class FrameworkResponse(BaseModel):
    id: int

    name: str

    version: str

    description: str

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }