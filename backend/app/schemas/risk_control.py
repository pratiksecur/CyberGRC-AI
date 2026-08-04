from datetime import datetime

from pydantic import BaseModel


class RiskControlCreate(BaseModel):
    risk_id: int
    control_id: int


class RiskControlResponse(BaseModel):
    id: int
    risk_id: int
    control_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }