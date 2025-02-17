from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 1️⃣ Define the SQLAlchemy Base
Base = declarative_base()

# 2️⃣ Create the Database Engine
# Database URL format: postgresql://user:password@host:port/database
DATABASE_URL = settings.DATABASE_URL

# 3️⃣ Create a Thread-Safe Session Factory
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal is the database session that we use in our application
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 4️⃣ Dependency for Database Sessions (FastAPI's dependency injection)
def get_db():
    """Dependency for injecting a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
