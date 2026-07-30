from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import DATABASE_URL

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all SQLAlchemy models
Base = declarative_base()


# Dependency to get a database session
def get_db():
    """
    Create a database session for each request.
    """
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()