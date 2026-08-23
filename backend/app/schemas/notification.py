from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):

    id: int

    type: str

    title: str

    message: str

    source_type: str

    source_id: int

    is_read: bool

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class NotificationUnreadCountResponse(BaseModel):

    unread_count: int


class NotificationMessageResponse(BaseModel):

    message: str