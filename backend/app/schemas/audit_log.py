from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogEntry(BaseModel):
    id: int
    actor_id: int | None = None
    actor_email: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    summary: str
    details: dict[str, Any] | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogPage(BaseModel):
    items: list[AuditLogEntry]
    total: int
    limit: int
    offset: int


class AuditLogFilters(BaseModel):
    entity_types: list[str]
    actions: list[str]