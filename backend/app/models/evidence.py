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


class Evidence(Base):
    __tablename__ = "evidence"

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

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ======================================================
    # Relationships
    # ======================================================

    organization = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    control = relationship(
        "Control",
        back_populates="evidence"
    )

    uploader = relationship(
        "User",
        foreign_keys=[uploaded_by],
        back_populates="uploaded_evidence"
    )


@event.listens_for(Evidence, "before_insert")
def _default_evidence_organization(mapper, connection, target):
    """
    Evidence belongs to its control's organization (or its uploader's).

    Used only when no organization is given. If nothing resolves, the
    database rejects the insert (NOT NULL).
    """

    inherit_organization(
        connection,
        target,
        ("controls", target.control_id),
        ("users", target.uploaded_by),
    )