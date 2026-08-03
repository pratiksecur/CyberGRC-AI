from datetime import datetime

from typing import Optional

from pydantic import BaseModel, Field

class RiskCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)

    likelihood: int = Field(..., ge=1, le=5)

    impact: int = Field(..., ge=1, le=5)

    owner_id: int

class RiskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)

    description: Optional[str] = Field(None, min_length=10)

    likelihood: Optional[int] = Field(None, ge=1, le=5)

    impact: Optional[int] = Field(None, ge=1, le=5)

    status: Optional[str] = Field(None)

    owner_id: Optional[int] = None

class RiskResponse(BaseModel):
    id: int

    title: str

    description: str

    likelihood: int

    impact: int

    risk_score: int

    status: str

    owner_id: int

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }