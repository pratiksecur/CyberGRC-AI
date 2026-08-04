from datetime import datetime

from pydantic import BaseModel


class ControlFrameworkControlCreate(BaseModel):
    control_id: int
    framework_control_id: int


class ControlFrameworkControlResponse(BaseModel):
    id: int

    control_id: int

    framework_control_id: int

    created_at: datetime

    model_config = {
        "from_attributes": True
    }