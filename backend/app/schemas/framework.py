from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class FrameworkCreate(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str = Field(
        min_length=2,
        max_length=100,
    )

    version: str = Field(
        min_length=1,
        max_length=50,
    )

    description: str = Field(
        min_length=10,
    )


class FrameworkUpdate(BaseModel):

    model_config = ConfigDict(
        extra="forbid",
    )

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
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


class FrameworkResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
    )

    id: int
    organization_id: int
    name: str
    version: str
    description: str
    created_at: datetime
    updated_at: datetime