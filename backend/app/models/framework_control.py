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


class FrameworkControl(Base):
    __tablename__ = "framework_controls"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    framework_id = Column(
        Integer,
        ForeignKey("frameworks.id"),
        nullable=False
    )

    control_code = Column(
        String(50),
        nullable=False
    )

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
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

    framework = relationship(
        "Framework",
        back_populates="framework_controls"
    )