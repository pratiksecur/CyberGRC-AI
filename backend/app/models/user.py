from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
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

    hashed_password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(50),
        default=UserRole.EMPLOYEE.value
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