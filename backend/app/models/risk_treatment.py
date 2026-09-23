from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class RiskTreatment(Base):
    __tablename__ = "risk_treatments"

    __table_args__ = (
        CheckConstraint(
            "strategy IN "
            "('Mitigate', 'Avoid', 'Transfer', 'Accept')",
            name="ck_risk_treatments_strategy",
        ),
        CheckConstraint(
            "status IN "
            "('Planned', 'In Progress', 'Completed', 'Cancelled')",
            name="ck_risk_treatments_status",
        ),
        CheckConstraint(
            "acceptance_status IN "
            "('Not Required', 'Pending', 'Approved', 'Rejected')",
            name="ck_risk_treatments_acceptance_status",
        ),
        CheckConstraint(
            "residual_likelihood IS NULL OR "
            "(residual_likelihood BETWEEN 1 AND 5)",
            name="ck_risk_treatments_residual_likelihood",
        ),
        CheckConstraint(
            "residual_impact IS NULL OR "
            "(residual_impact BETWEEN 1 AND 5)",
            name="ck_risk_treatments_residual_impact",
        ),
        CheckConstraint(
            "residual_risk_score IS NULL OR "
            "(residual_risk_score BETWEEN 1 AND 25)",
            name="ck_risk_treatments_residual_risk_score",
        ),
    )

    # ======================================================
    # Identity
    # ======================================================

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    # ======================================================
    # Risk Relationship
    # ======================================================

    risk_id = Column(
        Integer,
        ForeignKey("risks.id"),
        nullable=False,
        index=True,
    )

    # ======================================================
    # Treatment Strategy / Status
    # ======================================================

    strategy = Column(
        String(50),
        nullable=False,
    )

    status = Column(
        String(50),
        nullable=False,
        default="Planned",
    )

    treatment_plan = Column(
        Text,
        nullable=False,
    )

    # ======================================================
    # Treatment Ownership / Target
    # ======================================================

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    target_date = Column(
        Date,
        nullable=True,
    )

    # ======================================================
    # Residual Risk Assessment
    # ======================================================

    residual_likelihood = Column(
        Integer,
        nullable=True,
    )

    residual_impact = Column(
        Integer,
        nullable=True,
    )

    residual_risk_score = Column(
        Integer,
        nullable=True,
    )

    # ======================================================
    # Risk Acceptance
    # ======================================================

    acceptance_status = Column(
        String(50),
        nullable=False,
        default="Not Required",
    )

    acceptance_reason = Column(
        Text,
        nullable=True,
    )

    accepted_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True,
    )

    accepted_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ======================================================
    # Timestamps
    # ======================================================

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ======================================================
    # Relationships
    # ======================================================

    risk = relationship(
        "Risk",
        back_populates="risk_treatments",
    )

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="risk_treatments",
    )

    accepted_by = relationship(
        "User",
        foreign_keys=[accepted_by_id],
        back_populates="accepted_risk_treatments",
    )