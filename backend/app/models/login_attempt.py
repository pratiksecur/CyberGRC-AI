from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Index,
    Integer,
    String,
)
from sqlalchemy.sql import func

from app.database.database import Base


class LoginAttempt(Base):
    """
    One row per sign-in attempt, successful or not.

    It is both the security log of who tried to sign in and the data the
    brute-force protection counts. The email is stored as typed (lowercased),
    even if no such account exists, so guessing unknown emails is limited
    too and the response never reveals whether an account exists.
    """

    __tablename__ = "login_attempts"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    email = Column(
        String(255),
        nullable=False,
    )

    ip_address = Column(
        String(64),
        nullable=True,
    )

    success = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        Index(
            "ix_login_attempts_email_created",
            "email",
            "created_at",
        ),
        Index(
            "ix_login_attempts_ip_created",
            "ip_address",
            "created_at",
        ),
    )