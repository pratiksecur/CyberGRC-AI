from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base


class Risk(Base):
    __tablename__ = "risks"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    likelihood = Column(
        Integer,
        nullable=False
    )

    impact = Column(
        Integer,
        nullable=False
    )

    risk_score = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(50),
        default="Open"
    )

    # ======================================================
    # Ownership
    # ======================================================

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ======================================================
    # Creation Attribution
    # ======================================================

    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    # ======================================================
    # Timestamps
    # ======================================================

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

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="risks"
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="created_risks"
    )

    risk_controls = relationship(
        "RiskControl",
        back_populates="risk",
        cascade="all, delete-orphan"
    )

    risk_treatments = relationship(
        "RiskTreatment",
        back_populates="risk",
        cascade="all, delete-orphan",
        order_by="RiskTreatment.created_at",
    )

    response_decisions = relationship(
        "RiskResponseDecisionRecord",
        back_populates="risk",
        cascade="all, delete-orphan",
        order_by="RiskResponseDecisionRecord.created_at",
    )

    response_executions = relationship(
        "RiskResponseExecutionRecord",
        back_populates="risk",
        cascade="all, delete-orphan",
        order_by="RiskResponseExecutionRecord.created_at",
    )

    response_workflows = relationship(
        "RiskResponseWorkflowRecord",
        back_populates="risk",
        cascade="all, delete-orphan",
        order_by="RiskResponseWorkflowRecord.created_at",
    )