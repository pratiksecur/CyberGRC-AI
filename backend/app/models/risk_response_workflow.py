"""
Governed Risk Response Workflow Model

Phase 60
--------

Represents the controlled workflow created after an approved
risk-response execution.

The workflow record is deliberately separate from:
- the governance decision;
- the execution audit record;
- the underlying GRC resource.

Phase 60.4 adds governed workflow lifecycle tracking.
"""

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class RiskResponseWorkflowRecord(Base):
    __tablename__ = "risk_response_workflows"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    execution_id = Column(
        Integer,
        ForeignKey("risk_response_executions.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    decision_id = Column(
        Integer,
        ForeignKey("risk_response_decisions.id"),
        nullable=False,
        index=True,
    )

    risk_id = Column(
        Integer,
        ForeignKey("risks.id"),
        nullable=False,
        index=True,
    )

    workflow_type = Column(
        String(50),
        nullable=False,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="OPEN",
        index=True,
    )

    target_type = Column(
        String(50),
        nullable=False,
    )

    target_id = Column(
        Integer,
        nullable=True,
        index=True,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=False,
    )

    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    # ------------------------------------------------------
    # Phase 60.4 lifecycle governance
    # ------------------------------------------------------

    updated_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    resolution_reason = Column(
        Text,
        nullable=True,
    )

    started_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------
    # Relationships
    # ------------------------------------------------------

    execution = relationship(
        "RiskResponseExecutionRecord",
        back_populates="workflow",
    )

    decision = relationship(
        "RiskResponseDecisionRecord",
        back_populates="workflows",
    )

    risk = relationship(
        "Risk",
        back_populates="response_workflows",
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="response_workflows",
    )

    updated_by = relationship(
        "User",
        foreign_keys=[updated_by_id],
    )