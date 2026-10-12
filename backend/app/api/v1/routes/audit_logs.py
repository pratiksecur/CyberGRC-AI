from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.permissions import require_roles
from app.core.roles import UserRole
from app.database.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogFilters, AuditLogPage


router = APIRouter(
    prefix="/audit-logs",
    tags=["Audit Trail"],
)


@router.get(
    "/",
    response_model=AuditLogPage,
)
def list_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    entity_type: str | None = Query(None, max_length=64),
    entity_id: str | None = Query(None, max_length=64),
    action: str | None = Query(None, max_length=64),
    actor_id: int | None = Query(None),
    since: datetime | None = Query(None),
    until: datetime | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.AUDITOR)
    ),
):
    """
    The audit trail of the signed-in user's organization, newest first.

    Administrators and auditors can read it. Nobody can change or delete
    entries through the API.
    """

    query = db.query(AuditLog).filter(
        AuditLog.organization_id == current_user.organization_id
    )

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    if entity_id:
        query = query.filter(AuditLog.entity_id == entity_id)

    if action:
        query = query.filter(AuditLog.action == action)

    if actor_id is not None:
        query = query.filter(AuditLog.actor_id == actor_id)

    if since is not None:
        query = query.filter(AuditLog.created_at >= since)

    if until is not None:
        query = query.filter(AuditLog.created_at <= until)

    total = query.count()

    items = (
        query.order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/filters",
    response_model=AuditLogFilters,
)
def audit_log_filters(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_roles(UserRole.ADMIN, UserRole.AUDITOR)
    ),
):
    """Values that can be used to filter the audit trail."""

    base = db.query(AuditLog).filter(
        AuditLog.organization_id == current_user.organization_id
    )

    entity_types = [
        row[0]
        for row in base.with_entities(AuditLog.entity_type)
        .distinct()
        .order_by(AuditLog.entity_type)
        .all()
    ]

    actions = [
        row[0]
        for row in base.with_entities(AuditLog.action)
        .distinct()
        .order_by(AuditLog.action)
        .all()
    ]

    return {"entity_types": entity_types, "actions": actions}