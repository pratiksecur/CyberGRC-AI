from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    type = Column(
        String(50),
        nullable=False,
    )

    title = Column(
        String(255),
        nullable=False,
    )

    message = Column(
        Text,
        nullable=False,
    )

    source_type = Column(
        String(50),
        nullable=False,
    )

    source_id = Column(
        Integer,
        nullable=False,
    )

    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="notifications",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "type",
            "source_type",
            "source_id",
            name="uq_notification_user_type_source",
        ),
    )