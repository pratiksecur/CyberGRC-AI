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


class Control(Base):
    __tablename__ = "controls"

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

    control_type = Column(
        String(50),
        nullable=False
    )

    status = Column(
        String(50),
        default="Active"
    )

    effectiveness = Column(
        Integer,
        default=0,
        nullable=False
    )

    # ======================================================
    # Tenant Ownership
    # ======================================================

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id"),
        nullable=True,
        index=True,
    )

    owner_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
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

    # ======================================================
    # Relationships
    # ======================================================

    organization = relationship(
        "Organization",
        foreign_keys=[organization_id],
    )

    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="controls"
    )

    created_by = relationship(
        "User",
        foreign_keys=[created_by_id],
        back_populates="created_controls"
    )

    risk_controls = relationship(
        "RiskControl",
        back_populates="control",
        cascade="all, delete-orphan"
    )

    framework_control_mappings = relationship(
        "ControlFrameworkControl",
        back_populates="control",
        cascade="all, delete-orphan"
    )

    evidence = relationship(
        "Evidence",
        back_populates="control",
        cascade="all, delete-orphan"
    )