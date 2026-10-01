"""
Governed Risk Response Decision Model

Phase 59.1
-----------

Persists a human-governed decision request derived from the
Phase 57 continuous risk response.

This model records the response posture that was reviewed. It does
not execute the proposed response.
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class RiskResponseDecisionRecord(Base):
    __tablename__ = "risk_response_decisions"

    id = Column(
        Integer,
        primary_key=True,
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

    priority = Column(
        String(20),
        nullable=False,
    )

    governance_level = Column(
        String(50),
        nullable=False,
    )

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
        index=True,
    )

    human_approval_required = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    response_event_key = Column(
        String(255),
        nullable=False,
        index=True,
    )

    reason_codes = Column(
        JSON,
        nullable=False,
        default=list,
    )

    # ------------------------------------------------------
    # Response-state snapshot
    # ------------------------------------------------------

    risk_state = Column(
        String(50),
        nullable=False,
    )

    treatment_state = Column(
        String(50),
        nullable=False,
    )

    reassessment_required = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    response_required = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    # ------------------------------------------------------
    # Governance attribution
    # ------------------------------------------------------

    requested_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    assigned_to_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    # ------------------------------------------------------
    # Resolution
    # ------------------------------------------------------

    resolution_reason = Column(
        Text,
        nullable=True,
    )

    deferred_until = Column(
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

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ------------------------------------------------------
    # Relationships
    # ------------------------------------------------------

    risk = relationship(
        "Risk",
        back_populates="response_decisions",
    )

    requested_by = relationship(
        "User",
        foreign_keys=[requested_by_id],
        back_populates="requested_response_decisions",
    )

    assigned_to = relationship(
        "User",
        foreign_keys=[assigned_to_id],
        back_populates="assigned_response_decisions",
    )

    execution = relationship(
        "RiskResponseExecutionRecord",
        back_populates="decision_record",
        uselist=False,
    )