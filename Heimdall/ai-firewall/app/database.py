from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Generator

from app.config import settings

# SQLite requires "check_same_thread": False because FastAPI can spawn multiple threads
# that might interact with the same database connection.
engine_kwargs = {}
if settings.DATABASE_URL and settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL, **engine_kwargs
)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base class for all our ORM models to inherit from
Base = declarative_base()

def get_db() -> Generator:
    """
    Dependency function that yields a database session and ensures it is closed
    after the request is completed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
