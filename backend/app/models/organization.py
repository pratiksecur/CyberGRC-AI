from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
        unique=True,
    )

    slug = Column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        index=True,
    )

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

    users = relationship(
        "User",
        back_populates="organization",
    )

    business_units = relationship(
        "BusinessUnit",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    departments = relationship(
        "Department",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    grc_teams = relationship(
        "GrcTeam",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    enterprise_configuration = relationship(
        "EnterpriseConfiguration",
        back_populates="organization",
        uselist=False,
        cascade="all, delete-orphan",
    )

    frameworks = relationship(
        "Framework",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    policies = relationship(
        "Policy",
        back_populates="organization",
        cascade="all, delete-orphan",
    )