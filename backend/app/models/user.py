from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.core.roles import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String(100), nullable=False)

    email = Column(String(255), unique=True, nullable=False)

    hashed_password = Column(String(255), nullable=False)

    role = Column(String(50), default=UserRole.EMPLOYEE.value)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    risks = relationship(
        "Risk",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    controls = relationship(
        "Control",
        back_populates="owner",
        cascade="all, delete-orphan"
    )

    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
    )