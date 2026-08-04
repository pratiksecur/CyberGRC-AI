from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class ControlFrameworkControl(Base):
    __tablename__ = "control_framework_controls"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    control_id = Column(
        Integer,
        ForeignKey("controls.id"),
        nullable=False
    )

    framework_control_id = Column(
        Integer,
        ForeignKey("framework_controls.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    control = relationship(
        "Control",
        back_populates="framework_control_mappings"
    )

    framework_control = relationship(
        "FrameworkControl",
        back_populates="control_mappings"
    )