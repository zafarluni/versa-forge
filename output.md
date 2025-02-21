# 📂 Directory Structure

<pre>
.
├── main.py
├── __init__.py
├── notebooks
│   ├── api_testing.ipynb
│   ├── vector_store_tests.ipynb
│   ├── llm_experiments.ipynb
│   └── db_queries.ipynb
├── api
│   ├── dependencies.py
│   ├── __init__.py
│   └── routes
│       ├── files_router.py
│       ├── category_router.py
│       ├── agents_router.py
│       ├── __init__.py
│       └── chat_router.py
├── app
│   └── api
│       └── routes
│           └── category_router.py
├── llm
│   ├── vector_store.py
│   ├── llm_config.py
│   ├── __init__.py
│   └── llm.py
├── utils
│   └── __init__.py
├── db
│   ├── database.py
│   ├── __init__.py
│   ├── migrations
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── schemas
│   │   ├── category_schemas.py
│   │   ├── user_schemas.py
│   │   ├── agent_schemas.py
│   │   ├── group_schemas.py
│   │   └── agent_file_schema.py
│   └── models
│       ├── __init__.py
│       └── database_models.py
├── core
│   ├── auth.py
│   ├── security.py
│   ├── debugger.py
│   ├── __init__.py
│   └── config.py
└── services
    ├── file_service.py
    ├── chat_service.py
    ├── agent_service.py
    ├── categories_service.py
    └── __init__.py
</pre>

# 📄 Files

## ./main.py

```python
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents_router, category_router
from app.core.debugger import start_debugger
from app.core.config import settings

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start debugger if enabled
start_debugger()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
)

# Enable CORS - restrict origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(agents_router.router)
app.include_router(category_router.router)


# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    logger.info("Health check endpoint accessed.")
    return {"status": "OK", "message": "Versa-Forge API is running"}

```


## ./__init__.py

```python

```


## ./notebooks/api_testing.ipynb

```

```


## ./notebooks/vector_store_tests.ipynb

```

```


## ./notebooks/llm_experiments.ipynb

```

```


## ./notebooks/db_queries.ipynb

```

```


## ./api/dependencies.py

```python

```


## ./api/__init__.py

```python

```


## ./api/routes/files_router.py

```python

```


## ./api/routes/category_router.py

```python
from typing import List
from fastapi import HTTPException
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse
from app.services.categories_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate, db: Session = Depends(get_db)) -> CategoryResponse:
    return CategoryService.create_category(db, category_data)

@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)) -> List[CategoryResponse]:
    return CategoryService.get_all_categories(db)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryResponse:
    return CategoryService.get_category_by_id(db, category_id)

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), strict: bool = Query(False)) -> Response:
    deleted = CategoryService.delete_category(db, category_id)
    if strict:
        if deleted:
            return Response(status_code=204)
        raise HTTPException(status_code=404, detail="Category not found")  
    return Response(status_code=204)

```


## ./api/routes/agents_router.py

```python
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.db.schemas.user_schemas import UserBase as User
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse
from app.db.database import get_db
from app.services.agent_service import AgentService
from app.core.auth import get_current_user

router = APIRouter(prefix="/agents", tags=["Agents"])

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Create a New Agent
@router.post("/", response_model=AgentResponse)
def create_agent(
    agent_data: AgentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentResponse:
    if agent_data.is_public and not agent_data.categories:
        raise HTTPException(status_code=400, detail="Public agents must have categories")

    new_agent = AgentService.create_agent(db, agent_data, user.id)

    if agent_data.is_public and agent_data.categories:
        AgentService.assign_categories(db, new_agent.id, agent_data.categories)

    return new_agent


# Get Public Agents
@router.get("/public", response_model=List[AgentResponse])
def get_public_agents(
    category_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> List[AgentResponse]:
    return AgentService.get_public_agents(db, category_id, limit, offset)


# Get Private Agents
@router.get("/private", response_model=List[AgentResponse])
def get_private_agents(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> List[AgentResponse]:
    return AgentService.get_private_agents(db, user.id)


# Update Agent
@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentResponse:
    agent = AgentService.update_agent(db, agent_id, agent_data, user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")

    if agent.is_public and agent_data.categories:
        AgentService.delete_agent_categories(db, agent.id)
        AgentService.assign_categories(db, agent.id, agent_data.categories)

    return agent


# Delete Agent
@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> dict:
    deleted = AgentService.delete_agent(db, agent_id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")
    return {"message": "Agent deleted successfully"}


# Upload RAG Files
@router.post("/{agent_id}/upload")
def upload_file(
    agent_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    # Ensure user owns the agent before uploading a file
    agent = AgentService.get_agent_by_id_and_owner(db, agent_id, user.id)
    if not agent:
        raise HTTPException(status_code=403, detail="You are not allowed to upload files to this agent.")

    # Validate file type
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Save file securely
    safe_filename = f"{agent_id}_{file.filename.replace('/', '_')}"
    file_path = UPLOAD_DIR / safe_filename

    try:
        with file_path.open("wb") as f:
            f.write(file.file.read())
    except OSError as e:
        raise HTTPException(status_code=500, detail="File upload failed") from e

    # Save file metadata to DB
    doc = AgentService.upload_document(db, agent_id, file.filename, file.content_type)
    if not doc:
        raise HTTPException(status_code=500, detail="Failed to save file metadata")

    return {"message": "File uploaded successfully", "file_id": doc.id}


# Get Agent Files
@router.get("/{agent_id}/files")
def get_agent_files(
    agent_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)
) -> List[AgentFile]:
    # Ensure user owns the agent before accessing files
    agent = AgentService.get_agent_by_id_and_owner(db, agent_id, user.id)
    if not agent:
        raise HTTPException(status_code=403, detail="You are not allowed to access these files.")

    return AgentService.get_agent_files(db, agent_id)

```


## ./api/routes/__init__.py

```python

```


## ./api/routes/chat_router.py

```python

```


## ./app/api/routes/category_router.py

```python

```


## ./llm/vector_store.py

```python

```


## ./llm/llm_config.py

```python

```


## ./llm/__init__.py

```python

```


## ./llm/llm.py

```python

```


## ./utils/__init__.py

```python

```


## ./db/database.py

```python
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

```


## ./db/__init__.py

```python

```


## ./db/migrations/env.py

```python

```


## ./db/migrations/script.py.mako

```

```


## ./db/schemas/category_schemas.py

```python
# schemas/category_schemas.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

# Shared properties
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=5, max_length=100)
    description: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Reject names that contain only spaces and enforce allowed characters."""
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("Category name cannot be empty or contain only spaces.")
        if not all(c.isalnum() or c.isspace() or c in "-'" for c in stripped_value):
            raise ValueError("Category name must contain only letters, numbers, spaces, hyphens, or apostrophes.")
        return stripped_value  # Trim spaces before saving


# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    pass

# Properties to receive via API on update
class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Properties to return via API
class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

```


## ./db/schemas/user_schemas.py

```python
# schemas/user_schemas.py

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

# Shared properties
class UserBase(BaseModel):
    id: int
    username: str
    email: EmailStr

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to receive via API on update
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

# Properties to return via API
class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

```


## ./db/schemas/agent_schemas.py

```python
# schemas/agent_schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Shared properties
class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    is_public: bool

# Properties to receive via API on creation
class AgentCreate(AgentBase):
    categories: Optional[List[int]] = []

# Properties to receive via API on update
class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    is_public: Optional[bool] = None
    categories: Optional[List[int]] = None

# Properties to return via API
class AgentResponse(AgentBase):
    id: int
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

```


## ./db/schemas/group_schemas.py

```python
# schemas/group_schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Shared properties
class GroupBase(BaseModel):
    name: str
    description: Optional[str] = None

# Properties to receive via API on creation
class GroupCreate(GroupBase):
    pass

# Properties to receive via API on update
class GroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Properties to return via API
class GroupResponse(GroupBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Schema for assigning a user to a group
class UserGroupAssign(BaseModel):
    user_id: int
    group_id: int

```


## ./db/schemas/agent_file_schema.py

```python
# schemas/agent_file_schemas.py

from pydantic import BaseModel
from datetime import datetime

# Shared properties
class AgentFileBase(BaseModel):
    filename: str
    content_type: str

# Properties to receive via API on file upload
class AgentFileUpload(AgentFileBase):
    pass

# Properties to return via API
class AgentFileResponse(AgentFileBase):
    id: int
    agent_id: int
    created_at: datetime

    class Config:
        from_attributes = True

```


## ./db/models/__init__.py

```python

```


## ./db/models/database_models.py

```python
from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint, func, text
)
from sqlalchemy.orm import relationship
from app.db.database import Base

# ========================
# Users Table
# ========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    groups = relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"

# ========================
# Groups Table
# ========================
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    users = relationship("UserGroup", back_populates="group", cascade="all, delete-orphan")
    agents = relationship("AgentGroup", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Group(name={self.name})>"

# ========================
# User-Groups Junction Table
# ========================
class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True, index=True)

    # Relationships
    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="users")

    def __repr__(self) -> str:
        return f"<UserGroup(user_id={self.user_id}, group_id={self.group_id})>"

# ========================
# Categories Table
# ========================
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  

    # Relationships
    agents = relationship("AgentCategory", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Category(name={self.name})>"

# ========================
# Agents Table
# ========================
class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    is_public = Column(Boolean, server_default=text("false"), nullable=False)  # ✅ Fix: Used `text("false")`
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  # ✅ Fix

    # Relationships
    owner = relationship("User", back_populates="agents")
    categories = relationship("AgentCategory", back_populates="agent", cascade="all, delete-orphan")
    agent_files = relationship("AgentFile", back_populates="agent", cascade="all, delete-orphan")
    agent_groups = relationship("AgentGroup", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Agent(name={self.name}, owner_id={self.owner_id})>"

# ========================
# Agent-Categories Junction Table
# ========================
class AgentCategory(Base):
    __tablename__ = "agent_categories"

    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True, index=True)

    # Relationships
    agent = relationship("Agent", back_populates="categories")
    category = relationship("Category", back_populates="agents")

    def __repr__(self) -> str:
        return f"<AgentCategory(agent_id={self.agent_id}, category_id={self.category_id})>"

# ========================
# Agent-Groups Junction Table (Visibility Control)
# ========================
class AgentGroup(Base):
    __tablename__ = "agent_groups"

    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True, index=True)

    # Relationships
    agent = relationship("Agent", back_populates="agent_groups")
    group = relationship("Group", back_populates="agents")

    def __repr__(self) -> str:
        return f"<AgentGroup(agent_id={self.agent_id}, group_id={self.group_id})>"

# ========================
# Agent-Files Table (RAG Files)
# ========================
class AgentFile(Base):
    __tablename__ = "agent_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)  

    # Relationships
    agent = relationship("Agent", back_populates="agent_files")

    # Constraints
    __table_args__ = (UniqueConstraint("agent_id", "filename", name="uix_agent_file"),)

    def __repr__(self) -> str:
        return f"<AgentFile(filename={self.filename}, agent_id={self.agent_id})>"

```


## ./core/auth.py

```python
# app/auth/mock_auth.py
from app.db.schemas.user_schemas import UserBase as User


def get_current_user() -> User:
    """Returns a mock user for testing."""
    return User(
        username="admin",
        email="admin@example.com"
    )

```


## ./core/security.py

```python

```


## ./core/debugger.py

```python
import logging
import debugpy
from app.core.config import settings

logger = logging.getLogger(__name__)


def start_debugger() -> None:
    """Start the debugger if RUN_MAIN is set."""
    if settings.RUN_MAIN == True:
        debug_port = settings.DEBUG_PORT
        try:
            debugpy.listen(("0.0.0.0", debug_port))
            logger.info("🔍 Debugger is listening on port: %s", debug_port)
        except Exception as e: # pylint: disable=broad-exception-caught
            logger.error("⚠️ Failed to start debugger: %s", e)
```


## ./core/__init__.py

```python

```


## ./core/config.py

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Project Information (Static & Non-Sensitive)
    PROJECT_NAME: str = "Versa-Forge API"
    DESCRIPTION: str = (
        "VersaForge – A modular platform for building custom GPT agents with multi-LLM support and RAG."
    )
    VERSION: str = "1.0.0"

    # Debugging Settings
    RUN_MAIN: bool = False
    DEBUG_MODE: bool = False
    DEBUG_PORT: int = 5678

    # CORS Settings (Non-Sensitive)
    ALLOWED_ORIGINS: list[str] = ["http://localhost", "https://yourdomain.com"]

    # Database Settings (Sensitive - Must be set via `.env`)
    DATABASE_HOST: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_PORT: str

    # Docker Environment Indicator (Optional)
    RUNNING_IN_DOCKER: bool = False

    @property
    def DATABASE_URL(self) -> str:
        """Constructs the database connection URL dynamically."""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        extra = (
            "ignore"  # Prevents unexpected environment variables from causing errors
        )


# Instantiate settings from environment variables
settings = Settings()

```


## ./services/file_service.py

```python

```


## ./services/chat_service.py

```python

```


## ./services/agent_service.py

```python
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.db.models.database_models import Agent, AgentFile, AgentCategory
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse

class AgentService:
    @staticmethod
    def create_agent(db: Session, agent_data: AgentCreate, owner_id: int) -> AgentResponse:
        """Creates a new agent and commits it to the database."""
        new_agent = Agent(
            name=agent_data.name,
            description=agent_data.description,
            prompt=agent_data.prompt,
            is_public=agent_data.is_public,
            owner_id=owner_id,
            created_at=datetime.now(timezone.utc),
        )
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        return AgentResponse.model_validate(new_agent)

    @staticmethod
    def delete_agent_categories(db: Session, agent_id: int) -> None:
        """Deletes all category associations for a given agent."""
        db.query(AgentCategory).filter(AgentCategory.agent_id == agent_id).delete()
        db.commit()

    @staticmethod
    def assign_categories(db: Session, agent_id: int, category_ids: Optional[List[int]]) -> None:
        """Assigns categories to an agent."""
        if not category_ids:
            return  # Avoid unnecessary operations
        db.bulk_save_objects(
            [AgentCategory(agent_id=agent_id, category_id=cat_id) for cat_id in category_ids]
        )
        db.commit()

    @staticmethod
    def get_public_agents(
        db: Session, category_id: Optional[int] = None, limit: int = 10, offset: int = 0
    ) -> List[AgentResponse]:
        """Retrieves a paginated list of public agents, optionally filtered by category."""
        query = db.query(Agent).filter(Agent.is_public.is_(True))
        if category_id:
            query = query.join(AgentCategory).filter(AgentCategory.category_id == category_id)
        agents = query.offset(offset).limit(limit).all()
        return [AgentResponse.model_validate(agent) for agent in agents]

    @staticmethod
    def get_private_agents(db: Session, owner_id: int) -> List[AgentResponse]:
        """Retrieves a list of private agents belonging to a specific user."""
        agents = db.query(Agent).filter(Agent.owner_id == owner_id, Agent.is_public.is_(False)).all()
        return [AgentResponse.model_validate(agent) for agent in agents]

    @staticmethod
    def update_agent(
        db: Session, agent_id: int, agent_data: AgentUpdate, owner_id: int
    ) -> Optional[AgentResponse]:
        """Updates an existing agent's details."""
        agent = db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == owner_id).first()
        if not agent:
            return None
        # Update only non-null fields
        for field, value in agent_data.model_dump(exclude_unset=True).items():
            setattr(agent, field, value)
        db.commit()
        db.refresh(agent)
        return AgentResponse.model_validate(agent)

    @staticmethod
    def delete_agent(db: Session, agent_id: int, owner_id: int) -> bool:
        """Deletes an agent by ID if it exists and belongs to the user."""
        agent = db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == owner_id).first()
        if agent:
            db.delete(agent)
            db.commit()
            return True
        return False

    @staticmethod
    def upload_document(
        db: Session, agent_id: int, filename: str, content_type: str
    ) -> Optional[AgentFile]:
        """Uploads a document and associates it with an agent."""
        try:
            new_doc = AgentFile(
                agent_id=agent_id, filename=filename, content_type=content_type
            )
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            return new_doc
        except SQLAlchemyError:
            db.rollback()
            return None

    @staticmethod
    def get_agent_files(db: Session, agent_id: int) -> List[AgentFile]:
        """Retrieves all files associated with an agent."""
        return db.query(AgentFile).filter(AgentFile.agent_id == agent_id).all()

    @staticmethod
    def get_agent_by_id_and_owner(
        db: Session, agent_id: int, owner_id: int
    ) -> Optional[Agent]:
        """Retrieves an agent by its ID and owner ID."""
        return db.query(Agent).filter(Agent.id == agent_id, Agent.owner_id == owner_id).first()

```


## ./services/categories_service.py

```python
# ========================
# Category Service (service/categories_service.py)
# ========================
from typing import List
from fastapi import HTTPException
from sqlalchemy.orm import Session, load_only
from app.db.models.database_models import Category
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse


class CategoryService:
    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> CategoryResponse:
        normalized_name = category_data.name.strip().lower()  # Convert input name to lowercase

        existing_category = db.query(Category).filter(Category.name.ilike(normalized_name)).first()
        if existing_category:
            raise HTTPException(status_code=400, detail=f"Category with name '{category_data.name}' already exists.")

        new_category = Category(name=category_data.name.strip(), description=category_data.description)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return new_category




    @staticmethod
    def get_all_categories(db: Session) -> List[CategoryResponse]:
        categories = (
            db.query(Category)
            .options(load_only(getattr(Category, "id"), getattr(Category, "name"), getattr(Category, "description")))
            .all()
        )
        return [CategoryResponse.model_validate(category) for category in categories]

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> CategoryResponse:
        category = db.query(Category).filter_by(id=category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        category = db.query(Category).filter(Category.id == category_id).first()
        if category:
            db.delete(category)
            db.commit()
            return True        
        return False

```


## ./services/__init__.py

```python

```

