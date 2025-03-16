from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.utils.config import settings


class Base(DeclarativeBase):
    """Base model class for SQLAlchemy ORM."""

    pass


# Database URL from settings
DATABASE_URL = settings.DATABASE_URL

# Create Engine
async_engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)

# Session Factory
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine)

# Async Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,  # Key parameter for async sessions
    autoflush=False,
)


# Dependency for Async Sessions
# mypy: ignore-errors
async def get_db():
    """Yields an async database session."""
    async with AsyncSessionLocal() as db:
        yield db
