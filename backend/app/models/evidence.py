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


class Evidence(Base):
    __tablename__ = "evidence"

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

    title = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    file_name = Column(
        String(255),
        nullable=False
    )

    file_path = Column(
        String(500),
        nullable=False
    )

    # User who uploaded the evidence
    uploaded_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # ======================================================
    # Relationships
    # ======================================================

    control = relationship(
        "Control",
        back_populates="evidence"
    )

    uploader = relationship(
        "User",
        foreign_keys=[uploaded_by],
        back_populates="uploaded_evidence"
    )