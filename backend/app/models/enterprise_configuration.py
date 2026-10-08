from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class EnterpriseConfiguration(Base):
    """
    Organization-level enterprise configuration.

    Every configuration belongs to exactly one organization.
    The organization relationship is immutable from the API layer.
    """

    __tablename__ = "enterprise_configurations"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    organization_id = Column(
        Integer,
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # ======================================================
    # GENERAL
    # ======================================================

    timezone = Column(
        String(100),
        nullable=False,
        default="UTC",
        server_default="UTC",
    )

    # ======================================================
    # RISK THRESHOLDS
    # ======================================================

    default_risk_threshold = Column(
        Integer,
        nullable=False,
        default=15,
        server_default="15",
    )

    critical_risk_threshold = Column(
        Integer,
        nullable=False,
        default=20,
        server_default="20",
    )

    critical_risk_notification_threshold = Column(
        Integer,
        nullable=False,
        default=20,
        server_default="20",
    )

    # ======================================================
    # MONITORING THRESHOLDS
    # ======================================================

    ineffective_control_threshold = Column(
        Integer,
        nullable=False,
        default=50,
        server_default="50",
    )

    stale_evidence_days = Column(
        Integer,
        nullable=False,
        default=90,
        server_default="90",
    )

    treatment_stuck_days = Column(
        Integer,
        nullable=False,
        default=30,
        server_default="30",
    )

    treatment_residual_threshold = Column(
        Integer,
        nullable=False,
        default=15,
        server_default="15",
    )

    # ======================================================
    # GOVERNANCE
    # ======================================================

    continuous_risk_reassessment_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # ======================================================
    # NOTIFICATIONS
    # ======================================================

    notifications_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # ======================================================
    # AI
    # ======================================================

    ai_enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # ======================================================
    # TIMESTAMPS
    # ======================================================

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ======================================================
    # RELATIONSHIP
    # ======================================================

    organization = relationship(
        "Organization",
        back_populates="enterprise_configuration",
    )