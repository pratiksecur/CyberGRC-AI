from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
    event,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.models.tenant import inherit_organization


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ======================================================
    # Tenant Ownership
    # ======================================================

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    finding_id = Column(
        Integer,
        ForeignKey("audit_findings.id"),
        nullable=False
    )

    assigned_to = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    priority = Column(
        String(50),
        nullable=False
    )

    status = Column(
        String(50),
        default="Open"
    )

    due_date = Column(
        Date,
        nullable=False
    )

    completed_at = Column(
        Date,
        nullable=True
    )

    comments = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # ======================================================
    # Relationships
    # ======================================================

    organization = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    finding = relationship(
        "AuditFinding"
    )

    assignee = relationship(
        "User"
    )


@event.listens_for(CorrectiveAction, "before_insert")
def _default_corrective_action_organization(mapper, connection, target):
    """
    A corrective action belongs to its finding's organization (or its assignee's).

    Used only when no organization is given. If nothing resolves, the
    database rejects the insert (NOT NULL).
    """

    inherit_organization(
        connection,
        target,
        ("audit_findings", target.finding_id),
        ("users", target.assigned_to),
    )