"""
Governed Risk Response Execution Model

Phase 59.3 / Phase 60
----------------------

Records the execution of an approved governed risk response
decision.

Phase 60 adds the relationship to the resulting governed
workflow record.
"""

from sqlalchemy import (
    Boolean,
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


class RiskResponseExecutionRecord(Base):
    __tablename__ = "risk_response_executions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    decision_id = Column(
        Integer,
        ForeignKey("risk_response_decisions.id"),
        nullable=False,
        unique=True,
        index=True,
    )

    risk_id = Column(
        Integer,
        ForeignKey("risks.id"),
        nullable=False,
        index=True,
    )

    decision = Column(
        String(50),
        nullable=False,
    )

    response_event_key = Column(
        String(255),
        nullable=False,
        index=True,
    )

    status = Column(
        String(30),
        nullable=False,
        default="EXECUTED",
        index=True,
    )

    execution_action = Column(
        String(50),
        nullable=False,
    )

    human_approval_verified = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    response_event_verified = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    executed_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    execution_reason = Column(
        Text,
        nullable=False,
    )

    result_message = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    executed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ------------------------------------------------------
    # Relationships
    # ------------------------------------------------------

    decision_record = relationship(
        "RiskResponseDecisionRecord",
        back_populates="execution",
    )

    risk = relationship(
        "Risk",
        back_populates="response_executions",
    )

    executed_by = relationship(
        "User",
        foreign_keys=[executed_by_id],
        back_populates="response_executions",
    )

    workflow = relationship(
        "RiskResponseWorkflowRecord",
        back_populates="execution",
        uselist=False,
    )