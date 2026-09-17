from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL


if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured."
    )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_size=10,
    max_overflow=20,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    """
    Create one database session per request.

    The session is always closed after the request,
    including when an exception occurs.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()