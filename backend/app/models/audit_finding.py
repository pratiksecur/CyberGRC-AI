from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id = Column(
        Integer,
        primary_key=True,
        index=True
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

    audit = relationship(
        "Audit"
    )

    control = relationship(
        "Control"
    )