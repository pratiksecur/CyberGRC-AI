from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class RiskControl(Base):
    __tablename__ = "risk_controls"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    risk_id = Column(
        Integer,
        ForeignKey("risks.id"),
        nullable=False
    )

    control_id = Column(
        Integer,
        ForeignKey("controls.id"),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    risk = relationship(
        "Risk",
        back_populates="risk_controls"
    )

    control = relationship(
        "Control",
        back_populates="risk_controls"
    )