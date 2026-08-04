from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Audit(Base):
    __tablename__ = "audits"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(255),
        nullable=False
    )

    framework_id = Column(
        Integer,
        ForeignKey("frameworks.id"),
        nullable=False
    )

    auditor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    scope = Column(
        Text,
        nullable=False
    )

    status = Column(
        String(50),
        default="Planned"
    )

    start_date = Column(
        Date,
        nullable=False
    )

    end_date = Column(
        Date,
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
        "Framework"
    )

    auditor = relationship(
        "User"
    )