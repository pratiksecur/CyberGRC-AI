from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
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

    finding = relationship(
        "AuditFinding"
    )

    assignee = relationship(
        "User"
    )