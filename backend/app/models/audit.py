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


class Audit(Base):
    __tablename__ = "audits"

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

    name = Column(
        String(255),
        nullable=False
    )

    framework_id = Column(
        Integer,
        ForeignKey("frameworks.id"),
        nullable=False
    )

    auditor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    scope = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="Planned"
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
        nullable=False
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

    framework = relationship(
        "Framework"
    )

    auditor = relationship(
        "User",
        foreign_keys=[auditor_id]
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_id]
    )


@event.listens_for(Audit, "before_insert")
def _default_audit_organization(mapper, connection, target):
    """
    An audit belongs to its auditor's organization (or its creator's).

    Used only when no organization is given. If nothing resolves, the
    database rejects the insert (NOT NULL).
    """

    inherit_organization(
        connection,
        target,
        ("users", target.auditor_id),
        ("users", target.created_by_id),
    )