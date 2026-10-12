from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    event,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.models.tenant import inherit_organization


class AuditFinding(Base):
    __tablename__ = "audit_findings"

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

    audit_id = Column(
        Integer,
        ForeignKey("audits.id"),
        nullable=False
    )

    control_id = Column(
        Integer,
        ForeignKey("controls.id"),
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

    severity = Column(
        String(50),
        nullable=False
    )

    recommendation = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="Open"
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

    audit = relationship(
        "Audit"
    )

    control = relationship(
        "Control"
    )


@event.listens_for(AuditFinding, "before_insert")
def _default_audit_finding_organization(mapper, connection, target):
    """
    A finding belongs to its audit's organization (or its control's).

    Used only when no organization is given. If nothing resolves, the
    database rejects the insert (NOT NULL).
    """

    inherit_organization(
        connection,
        target,
        ("audits", target.audit_id),
        ("controls", target.control_id),
    )