import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.utils.config import get_settings

logger = logging.getLogger(__name__)


# ───── Base model ──────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """
    Base class for all ORM models.
    MappedAsDataclass gives you auto-generated __init__ and __repr__.
    """

    pass


# ───── Engine & Session Factory ────────────────────────────────────────────────
settings = get_settings()
DATABASE_URL = settings.database.url

async_engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set True if you want to see raw SQL logs
    pool_pre_ping=True,  # Avoid “stale connection” errors
    future=True,  # Opt into SQLAlchemy 2.0 behavior
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,  # Produce AsyncSession objects
    expire_on_commit=False,
    autoflush=False,
)


# ───── Dependency ─────────────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that yields an AsyncSession.
    Commits on success, rolls back on error, and always closes the session.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # commit if no exceptions
        except Exception as e:
            await session.rollback()  # rollback on error
            logger.error(f"Database session error: {e}", exc_info=True)
            raise
        finally:
            await session.close()
