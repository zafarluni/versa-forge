from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    """Base model class for SQLAlchemy ORM."""
    pass

# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create Engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# mypy ignore
# Dependency for Database Sessions
def get_db():  # type: ignore
    """Dependency for injecting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
