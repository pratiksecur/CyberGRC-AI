from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.database.database import Base


class AuditLog(Base):
    """
    Append-only record of who changed what, and when.

    Rows are written automatically whenever an audited record is created,
    changed or deleted (see app/audit/listeners.py), in the same database
    transaction as the change itself. The application only ever adds rows;
    there is no route that edits or removes them.

    The actor's email is stored as well as the id, so the entry stays
    readable after the account is deleted.
    """

    __tablename__ = "audit_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
    )

    # Deliberately not a foreign key: the log keeps its meaning (and can never
    # block or be broken by) deleting an account. actor_email names the person.
    actor_id = Column(
        Integer,
        nullable=True,
    )

    actor_email = Column(
        String(255),
        nullable=True,
    )

    # created, updated, deleted, password_changed, deactivated, ...
    action = Column(
        String(64),
        nullable=False,
    )

    # The table of the record that changed, for example "risks".
    entity_type = Column(
        String(64),
        nullable=False,
    )

    entity_id = Column(
        String(64),
        nullable=True,
    )

    summary = Column(
        String(500),
        nullable=False,
    )

    # {"changes": {field: {"from": old, "to": new}}} or {"values": {...}}
    details = Column(
        JSON,
        nullable=True,
    )

    ip_address = Column(
        String(64),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_audit_logs_org_created",
            "organization_id",
            "created_at",
        ),
        Index(
            "ix_audit_logs_entity",
            "entity_type",
            "entity_id",
        ),
    )