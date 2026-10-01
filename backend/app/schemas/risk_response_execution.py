from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RiskResponseExecutionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    decision_id: int
    risk_id: int
    decision: str
    response_event_key: str
    status: str
    execution_action: str
    human_approval_verified: bool
    response_event_verified: bool
    executed_by_id: int
    execution_reason: str
    result_message: str
    created_at: datetime
    executed_at: datetime