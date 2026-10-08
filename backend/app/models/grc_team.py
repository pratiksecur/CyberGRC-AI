from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class GrcTeam(Base):
    __tablename__ = "grc_teams"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_grc_teams_organization_name",
        ),
        UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_grc_teams_organization_slug",
        ),
    )

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
        index=True,
    )

    business_unit_id = Column(
        Integer,
        ForeignKey(
            "business_units.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    department_id = Column(
        Integer,
        ForeignKey(
            "departments.id",
            ondelete="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    name = Column(
        String(255),
        nullable=False,
    )

    slug = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
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

    organization = relationship(
        "Organization",
        back_populates="grc_teams",
    )

    business_unit = relationship(
        "BusinessUnit",
        back_populates="teams",
    )

    department = relationship(
        "Department",
        back_populates="teams",
    )

    users = relationship(
        "User",
        back_populates="grc_team",
    )