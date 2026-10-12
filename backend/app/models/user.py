from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index,
    true as sql_true,
)

from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.core.roles import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        nullable=False
    )

    # Emails are unique regardless of capitalisation.
    __table_args__ = (
        Index(
            "uq_users_email_lower",
            func.lower(email),
            unique=True,
        ),
    )

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default=UserRole.EMPLOYEE.value
    )

    # ======================================================
    # Account State
    # ======================================================

    # A deactivated user cannot sign in and existing sessions stop working.
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=sql_true(),
    )

    # Every access token carries this number. Raising it signs the user out
    # everywhere (logout, password change or reset, deactivation).
    token_version = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    password_changed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ======================================================
    # Organization / Tenant
    # ======================================================

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    organization = relationship(
        "Organization",
        back_populates="users",
    )

    # ======================================================
    # Organizational Hierarchy
    # ======================================================

    manager_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True
    )

    department = Column(
        String(100),
        nullable=True
    )

    # ======================================================
    # Enterprise Organizational Structure
    # ======================================================

    business_unit_id = Column(
        Integer,
        ForeignKey(
            "business_units.id"
        ),
        nullable=True,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey(
            "departments.id"
        ),
        nullable=True,
        index=True,
    )

    team_id = Column(
        Integer,
        ForeignKey(
            "grc_teams.id"
        ),
        nullable=True,
        index=True,
    )

    business_unit = relationship(
        "BusinessUnit",
        back_populates="users",
    )

    department_entity = relationship(
        "Department",
        back_populates="users",
    )

    grc_team = relationship(
        "GrcTeam",
        back_populates="users",
    )

    # ======================================================
    # Manager / Subordinate Relationship
    # ======================================================

    manager = relationship(
        "User",
        remote_side=[id],
        back_populates="subordinates"
    )

    subordinates = relationship(
        "User",
        back_populates="manager"
    )

    # ======================================================
    # Resource Relationships
    # ======================================================

    risks = relationship(
        "Risk",
        foreign_keys="Risk.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    created_risks = relationship(
        "Risk",
        foreign_keys="Risk.created_by_id",
        back_populates="created_by"
    )

    risk_treatments = relationship(
        "RiskTreatment",
        foreign_keys="RiskTreatment.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    accepted_risk_treatments = relationship(
        "RiskTreatment",
        foreign_keys="RiskTreatment.accepted_by_id",
        back_populates="accepted_by"
    )

    controls = relationship(
        "Control",
        foreign_keys="Control.owner_id",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    created_controls = relationship(
        "Control",
        foreign_keys="Control.created_by_id",
        back_populates="created_by"
    )

    uploaded_evidence = relationship(
        "Evidence",
        foreign_keys="Evidence.uploaded_by",
        back_populates="uploader"
    )

    audits = relationship(
        "Audit",
        foreign_keys="Audit.auditor_id",
        back_populates="auditor"
    )

    created_audits = relationship(
        "Audit",
        foreign_keys="Audit.created_by_id",
        back_populates="created_by"
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    requested_response_decisions = relationship(
        "RiskResponseDecisionRecord",
        foreign_keys=(
            "RiskResponseDecisionRecord.requested_by_id"
        ),
        back_populates="requested_by",
    )

    assigned_response_decisions = relationship(
        "RiskResponseDecisionRecord",
        foreign_keys=(
            "RiskResponseDecisionRecord.assigned_to_id"
        ),
        back_populates="assigned_to",
    )

    response_executions = relationship(
        "RiskResponseExecutionRecord",
        foreign_keys=(
            "RiskResponseExecutionRecord.executed_by_id"
        ),
        back_populates="executed_by",
    )

    response_workflows = relationship(
        "RiskResponseWorkflowRecord",
        foreign_keys=(
            "RiskResponseWorkflowRecord.created_by_id"
        ),
        back_populates="created_by",
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