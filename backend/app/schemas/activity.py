from datetime import datetime

from pydantic import BaseModel


class ActivityResponse(BaseModel):
    type: str

    title: str

    description: str

    time: datetime