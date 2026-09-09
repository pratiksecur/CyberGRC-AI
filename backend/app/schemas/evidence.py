from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EvidenceCreate(BaseModel):
    control_id: int

    title: str

    description: str

    file_name: str

    file_path: str


class EvidenceUpdate(BaseModel):
    title: Optional[str] = None

    description: Optional[str] = None

    file_name: Optional[str] = None

    file_path: Optional[str] = None


class EvidenceResponse(BaseModel):
    id: int

    control_id: int

    title: str

    description: str

    file_name: str

    file_path: str

    uploaded_by: int

    uploaded_at: datetime

    model_config = {
        "from_attributes": True
    }