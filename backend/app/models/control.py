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

    owner_id = Column(
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

    owner = relationship(
        "User",
        back_populates="controls"
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