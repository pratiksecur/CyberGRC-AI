from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.config import (
    DATABASE_URL,
    DB_MAX_OVERFLOW,
    DB_POOL_RECYCLE_SECONDS,
    DB_POOL_SIZE,
    DB_POOL_TIMEOUT_SECONDS,
)


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured.")


_ENGINE_KWARGS = {
    "pool_pre_ping": True,
    "pool_recycle": DB_POOL_RECYCLE_SECONDS,
}

if DATABASE_URL.lower().startswith("sqlite://"):
    # SQLite is used by the test suite and local development.
    _ENGINE_KWARGS.update(
        {
            "connect_args": {"check_same_thread": False},
        }
    )
else:
    _ENGINE_KWARGS.update(
        {
            "pool_size": DB_POOL_SIZE,
            "max_overflow": DB_MAX_OVERFLOW,
            "pool_timeout": DB_POOL_TIMEOUT_SECONDS,
        }
    )


engine = create_engine(
    DATABASE_URL,
    **_ENGINE_KWARGS,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    """Create one database session per request and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
