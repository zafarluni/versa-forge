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
│       ├── category_router.py
│       ├── agents_router.py
│       ├── __init__.py
│       ├── chat_router.py
│       └── agent_files_router.py
├── app
│   └── api
│       └── routes
│           └── category_router.py
├── llm
│   ├── llm_manager.py
│   ├── vector_store.py
│   ├── llm_config.py
│   ├── __init__.py
│   ├── llm.py
│   └── providers
│       ├── deepseek.py
│       ├── groq.py
│       ├── vllm.py
│       ├── llama.py
│       └── openai.py
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
    ├── chat_service.py
    ├── vector_store_service.py
    ├── agent_file_service.py
    ├── agent_service.py
    ├── categories_service.py
    └── __init__.py
</pre>

# 📄 Files

## ./main.py

```python
from typing import Dict
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
def health_check() -> Dict[str, str]:
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
from app.db.database import get_db
from app.core.auth import get_current_user

__all__ = ["get_db", "get_current_user"]

```


## ./api/__init__.py

```python

```


## ./api/routes/category_router.py

```python
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse
from app.services.categories_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category_data: CategoryCreate, db: Session=Depends(get_db)) -> CategoryResponse:
    return CategoryService.create_category(db, category_data)


@router.get("/", response_model=List[CategoryResponse])
def get_all_categories(db: Session=Depends(get_db)) -> List[CategoryResponse]:
    return CategoryService.get_all_categories(db)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session=Depends(get_db)) -> CategoryResponse:
    return CategoryService.get_category_by_id(db, category_id)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session=Depends(get_db), strict: bool = False) -> Response:
    deleted = CategoryService.delete_category(db, category_id)
    if strict and not deleted:
        raise HTTPException(status_code=404, detail="Category not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

```


## ./api/routes/agents_router.py

```python
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query

from app.db.database import get_db
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse
from app.db.schemas.agent_file_schema import AgentFileResponse
from app.services.agent_service import AgentService
from app.core.auth import get_current_user
from app.db.schemas.user_schemas import UserBase as User

router = APIRouter(prefix="/agents", tags=["Agents"])

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/", response_model=AgentResponse)
def create_agent(
    agent_data: AgentCreate,
    db=Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentResponse:
    if agent_data.is_public and not agent_data.categories:
        raise HTTPException(status_code=400, detail="Public agents must have categories")
    new_agent = AgentService.create_agent(db, agent_data, owner_id=user.id)
    if agent_data.is_public and agent_data.categories:
        AgentService.assign_categories(db, new_agent.id, agent_data.categories)
    return new_agent


@router.get("/public", response_model=List[AgentResponse])
def get_public_agents(
    category_id: Optional[int] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
    db=Depends(get_db),
) -> List[AgentResponse]:
    return AgentService.get_public_agents(db, category_id, limit, offset)


@router.get("/private", response_model=List[AgentResponse])
def get_private_agents(
    db=Depends(get_db), user: User = Depends(get_current_user)
) -> List[AgentResponse]:
    return AgentService.get_private_agents(db, owner_id=user.id)


@router.put("/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    agent_data: AgentUpdate,
    db=Depends(get_db),
    user: User = Depends(get_current_user),
) -> AgentResponse:
    agent = AgentService.update_agent(db, agent_id, agent_data, owner_id=user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")
    if agent.is_public and agent_data.categories:
        AgentService.delete_agent_categories(db, agent.id)
        AgentService.assign_categories(db, agent.id, agent_data.categories)
    return agent


@router.delete("/{agent_id}")
def delete_agent(
    agent_id: int, db=Depends(get_db), user: User = Depends(get_current_user)
) -> dict:
    deleted = AgentService.delete_agent(db, agent_id, owner_id=user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found or unauthorized")
    return {"message": "Agent deleted successfully"}


@router.post("/{agent_id}/upload", response_model=dict)
def upload_file(
    agent_id: int,
    file: UploadFile = File(...),
    db=Depends(get_db),
    user: User = Depends(get_current_user),
) -> dict:
    # Check ownership before uploading
    agent = AgentService.get_agent_by_id_and_owner(db, agent_id, owner_id=user.id)
    if not agent:
        raise HTTPException(status_code=403, detail="Not allowed to upload files to this agent.")
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    safe_filename = f"{agent_id}_{file.filename.replace('/', '_')}"
    file_path = UPLOAD_DIR / safe_filename
    try:
        with file_path.open("wb") as f:
            f.write(file.file.read())
    except OSError as e:
        raise HTTPException(status_code=500, detail="File upload failed") from e
    doc = AgentService.upload_document(db, agent_id, file.filename, file.content_type)
    if not doc:
        raise HTTPException(status_code=500, detail="Failed to save file metadata")
    return {"message": "File uploaded successfully", "file_id": doc.id}


@router.get("/{agent_id}/files", response_model=List[AgentFileResponse])
def get_agent_files(
    agent_id: int, db=Depends(get_db), user: User = Depends(get_current_user)
) -> List[AgentFileResponse]:
    agent = AgentService.get_agent_by_id_and_owner(db, agent_id, owner_id=user.id)
    if not agent:
        raise HTTPException(status_code=403, detail="Not allowed to access these files.")
    files = AgentService.get_agent_files(db, agent_id)
    # Assuming AgentFileResponse.model_validate is available
    return [AgentFileResponse.model_validate(file) for file in files]

```


## ./api/routes/__init__.py

```python

```


## ./api/routes/chat_router.py

```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.chat_service import ChatService
from app.api.dependencies import get_current_user
from app.db.schemas.user_schemas import UserBase as User

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    agent_id: int
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("/", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest, user: User = Depends(get_current_user)):
    result = ChatService.process_chat(request.agent_id, request.message, user.id)
    if not result:
        raise HTTPException(status_code=500, detail="Chat processing failed")
    return ChatResponse(response=result)

```


## ./api/routes/agent_files_router.py

```python
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from typing import List, Optional
from app.db.database import get_db
from app.db.schemas.agent_file_schema import AgentFileResponse
from app.services.agent_file_service import AgentFileService
from app.api.dependencies import get_current_user
from app.db.schemas.user_schemas import UserBase as User

router = APIRouter(prefix="/files", tags=["Files"])


@router.post("/upload", response_model=dict)
def upload_file(
    agent_id: int,
    file: UploadFile = File(...),
    db=Depends(get_db),
    user: User = Depends(get_current_user),
):
    result = AgentFileService.save_file(db, agent_id, file, user.id)
    if not result:
        raise HTTPException(status_code=500, detail="File upload failed")
    return result


@router.get("/", response_model=List[AgentFileResponse])
def list_files(
    agent_id: int,
    db=Depends(get_db),
    user: User = Depends(get_current_user),
) -> List[AgentFileResponse]:
    files = AgentFileService.get_files(db, agent_id, user.id)
    if files is None:
        raise HTTPException(status_code=404, detail="No files found")
    return files

```


## ./app/api/routes/category_router.py

```python

```


## ./llm/llm_manager.py

```python
from typing import Dict, Any
from app.llm.providers.openai import OpenAIProvider
from app.llm.providers.llama import LlamaProvider
from app.llm.providers.vllm import VLLMProvider
from app.llm.providers.deepseek import DeepSeekProvider
from app.llm.providers.groq import GroqProvider
from app.core.llm_provider import BaseLLMProvider

class LLMManager:
    providers: Dict[str, BaseLLMProvider] = {
        "openai": OpenAIProvider(),
        "llama": LlamaProvider(),
        "vllm": VLLMProvider(),
        "deepseek": DeepSeekProvider(),
        "groq": GroqProvider(),
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> BaseLLMProvider:
        provider = cls.providers.get(provider_name.lower())
        if not provider:
            raise ValueError(f"LLM provider '{provider_name}' is not supported.")
        return provider

    @classmethod
    def configure_provider(cls, provider_name: str, config: Dict[str, Any]) -> None:
        provider = cls.get_provider(provider_name)
        provider.configure(config)

```


## ./llm/vector_store.py

```python
# This file provides abstractions for interacting with vector stores.

from app.services.vector_store_service import BaseVectorStore, DummyVectorStore

# For now, we can instantiate a dummy vector store.
vector_store = DummyVectorStore()

def add_document_to_store(document: dict) -> None:
    vector_store.add_document(document)

def query_vector_store(query: str, top_k: int = 5):
    return vector_store.query(query, top_k)

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


## ./llm/providers/deepseek.py

```python
from app.core.llm_provider import BaseLLMProvider
from typing import Any, Dict

class DeepSeekProvider(BaseLLMProvider):
    def __init__(self):
        self.config = {}

    def configure(self, config: Dict[str, Any]) -> None:
        self.config = config

    def generate(self, prompt: str, **kwargs) -> str:
        # Placeholder for DeepSeek generation
        return f"[DeepSeek] Response to: {prompt}"

```


## ./llm/providers/groq.py

```python
from app.core.llm_provider import BaseLLMProvider
from typing import Any, Dict

class DeepSeekProvider(BaseLLMProvider):
    def __init__(self):
        self.config = {}

    def configure(self, config: Dict[str, Any]) -> None:
        self.config = config

    def generate(self, prompt: str, **kwargs) -> str:
        # Placeholder for DeepSeek generation
        return f"[DeepSeek] Response to: {prompt}"

```


## ./llm/providers/vllm.py

```python
from app.core.llm_provider import BaseLLMProvider
from typing import Any, Dict

class VLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.config = {}

    def configure(self, config: Dict[str, Any]) -> None:
        self.config = config

    def generate(self, prompt: str, **kwargs) -> str:
        # Placeholder for vLLM generation
        return f"[vLLM] Response to: {prompt}"

```


## ./llm/providers/llama.py

```python
from app.core.llm_provider import BaseLLMProvider
from typing import Any, Dict

class LlamaProvider(BaseLLMProvider):
    def __init__(self):
        self.config = {}

    def configure(self, config: Dict[str, Any]) -> None:
        self.config = config

    def generate(self, prompt: str, **kwargs) -> str:
        # Placeholder for Llama generation
        return f"[Llama] Response to: {prompt}"

```


## ./llm/providers/openai.py

```python
from app.core.llm_provider import BaseLLMProvider
from typing import Any, Dict

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.config = {}

    def configure(self, config: Dict[str, Any]) -> None:
        self.config = config

    def generate(self, prompt: str, **kwargs) -> str:
        # Placeholder: Implement actual OpenAI API call
        return f"[OpenAI] Response to: {prompt}"

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

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class AgentBase(BaseModel):
    name: str
    description: Optional[str] = None
    prompt: str
    is_public: bool

class AgentCreate(AgentBase):
    categories: Optional[List[int]] = []

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt: Optional[str] = None
    is_public: Optional[bool] = None
    categories: Optional[List[int]] = None

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
    is_public = Column(Boolean, server_default=text("false"), nullable=False)  
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

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
from app.db.schemas.user_schemas import UserBase as User

def get_current_user() -> User:
    # Placeholder for real authentication logic.
    # Replace with JWT or OAuth2 as needed.
    return User(id=1, username="admin", email="admin@example.com")

```


## ./core/security.py

```python
# from passlib.context import CryptContext

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)

# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

```


## ./core/debugger.py

```python
import logging
import debugpy
from app.core.config import settings

logger = logging.getLogger(__name__)

def start_debugger() -> None:
    if settings.RUN_MAIN:
        try:
            debugpy.listen(("0.0.0.0", settings.DEBUG_PORT))
            logger.info("Debugger is listening on port %s", settings.DEBUG_PORT)
        except Exception as e: # pylint: disable=PylintW0718:broad-exception-caught
            logger.error("Failed to start debugger: %s", e)

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
    def DATABASE_URL(self) -> str:  # pylint: disable=C0103:invalid-name
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
settings = Settings() # type: ignore

```


## ./services/chat_service.py

```python
# from app.llm.llm_manager import LLMManager

# class ChatService:
#     @staticmethod
#     def process_chat(agent_id: int, message: str, user_id: int) -> str:
#         # For demonstration, retrieve provider configuration based on agent_id (placeholder logic)
#         provider_config = {"provider": "openai"}  # This should be retrieved from the agent configuration
#         provider = LLMManager.get_provider(provider_config["provider"])
#         response = provider.generate(prompt=message)
#         return response

```


## ./services/vector_store_service.py

```python
from abc import ABC, abstractmethod
from typing import List, Any

class BaseVectorStore(ABC):
    @abstractmethod
    def add_document(self, document: Any) -> None:
        pass

    @abstractmethod
    def query(self, query_text: str, top_k: int) -> List[Any]:
        pass

# Example implementation for a vector store backend (e.g., Milvus, Qdrant)
class DummyVectorStore(BaseVectorStore):
    def __init__(self):
        self.documents = []

    def add_document(self, document: Any) -> None:
        self.documents.append(document)

    def query(self, query_text: str, top_k: int) -> List[Any]:
        # Dummy implementation that returns first top_k documents
        return self.documents[:top_k]

```


## ./services/agent_file_service.py

```python
from pathlib import Path
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.schemas.agent_file_schema import AgentFileResponse
from app.db.models.database_models import AgentFile, Agent
from app.services.agent_service import AgentService

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class AgentFileService:
    @staticmethod
    def save_file(db: Session, agent_id: int, file, user_id: int) -> dict:
        # Verify ownership using AgentService
        agent = AgentService.get_agent_by_id_and_owner(db, agent_id, owner_id=user_id)
        if not agent:
            raise HTTPException(status_code=403, detail="Not authorized to upload files for this agent.")
        allowed_types = {
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Invalid file type")
        safe_filename = f"{agent_id}_{file.filename.replace('/', '_')}"
        file_path = UPLOAD_DIR / safe_filename
        try:
            with file_path.open("wb") as f:
                f.write(file.file.read())
        except OSError as e:
            raise HTTPException(status_code=500, detail="File upload failed") from e
        doc = AgentService.upload_document(db, agent_id, file.filename, file.content_type)
        if not doc:
            raise HTTPException(status_code=500, detail="Failed to save file metadata")
        return {"message": "File uploaded successfully", "file_id": doc.id}

    @staticmethod
    def get_files(db: Session, agent_id: int, user_id: int):
        agent = AgentService.get_agent_by_id_and_owner(db, agent_id, owner_id=user_id)
        if not agent:
            return None
        stmt = AgentService.get_agent_files(db, agent_id)
        return [AgentFileResponse.model_validate(file) for file in stmt]

```


## ./services/agent_service.py

```python
from typing import Optional, List, Any
from datetime import datetime, timezone
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.database_models import Agent, AgentCategory, AgentFile
from app.db.schemas.agent_schemas import AgentCreate, AgentUpdate, AgentResponse

class AgentService:
    @staticmethod
    def create_agent(db: Session, agent_data: AgentCreate, owner_id: int) -> AgentResponse:
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
        stmt = delete(AgentCategory).where(AgentCategory.agent_id == agent_id)
        db.execute(stmt)
        db.commit()

    @staticmethod
    def assign_categories(db: Session, agent_id: int, category_ids: Optional[List[int]]) -> None:
        if not category_ids:
            return
        objs = [AgentCategory(agent_id=agent_id, category_id=cat_id) for cat_id in category_ids]
        db.bulk_save_objects(objs)
        db.commit()

    @staticmethod
    def get_public_agents(
        db: Session, category_id: Optional[int] = None, limit: int = 10, offset: int = 0
    ) -> List[AgentResponse]:
        stmt = select(Agent).where(Agent.is_public.is_(True))
        if category_id:
            stmt = stmt.join(AgentCategory).where(AgentCategory.category_id == category_id)
        stmt = stmt.offset(offset).limit(limit)
        result = db.execute(stmt).scalars().all()
        return [AgentResponse.model_validate(agent) for agent in result]

    @staticmethod
    def get_private_agents(db: Session, owner_id: int) -> List[AgentResponse]:
        stmt = select(Agent).where(Agent.owner_id == owner_id, Agent.is_public.is_(False))
        result = db.execute(stmt).scalars().all()
        return [AgentResponse.model_validate(agent) for agent in result]

    @staticmethod
    def update_agent(db: Session, agent_id: int, agent_data: AgentUpdate, owner_id: int) -> Optional[AgentResponse]:
        stmt = select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        agent = db.execute(stmt).scalar_one_or_none()
        if not agent:
            return None
        update_data = agent_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        db.commit()
        db.refresh(agent)
        return AgentResponse.model_validate(agent)

    @staticmethod
    def delete_agent(db: Session, agent_id: int, owner_id: int) -> bool:
        stmt = select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        agent = db.execute(stmt).scalar_one_or_none()
        if agent:
            db.delete(agent)
            db.commit()
            return True
        return False

    @staticmethod
    def upload_document(db: Session, agent_id: int, filename: str, content_type: str) -> Optional[AgentFile]:
        try:
            new_doc = AgentFile(agent_id=agent_id, filename=filename, content_type=content_type)
            db.add(new_doc)
            db.commit()
            db.refresh(new_doc)
            return new_doc
        except SQLAlchemyError:
            db.rollback()
            return None

    @staticmethod
    def get_agent_files(db: Session, agent_id: int) -> List[AgentFile]:
        stmt = select(AgentFile).where(AgentFile.agent_id == agent_id)
        result = db.execute(stmt).scalars().all()
        return result

    @staticmethod
    def get_agent_by_id_and_owner(db: Session, agent_id: int, owner_id: int) -> Optional[Agent]:
        stmt = select(Agent).where(Agent.id == agent_id, Agent.owner_id == owner_id)
        return db.execute(stmt).scalar_one_or_none()

```


## ./services/categories_service.py

```python
# ========================
# Category Service (service/categories_service.py)
# ========================
from typing import List
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.database_models import Category
from app.db.schemas.category_schemas import CategoryCreate, CategoryResponse

class CategoryService:
    @staticmethod
    def create_category(db: Session, category_data: CategoryCreate) -> CategoryResponse:
        normalized_name = category_data.name.strip().lower()
        stmt = select(Category).where(Category.name.ilike(normalized_name))
        existing_category = db.execute(stmt).scalar_one_or_none()
        if existing_category:
            raise HTTPException(status_code=400, detail=f"Category '{category_data.name}' already exists.")
        new_category = Category(name=category_data.name.strip(), description=category_data.description)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return CategoryResponse.model_validate(new_category)

    @staticmethod
    def get_all_categories(db: Session) -> List[CategoryResponse]:
        stmt = select(Category)
        categories = db.execute(stmt).scalars().all()
        return [CategoryResponse.model_validate(category) for category in categories]

    @staticmethod
    def get_category_by_id(db: Session, category_id: int) -> CategoryResponse:
        stmt = select(Category).where(Category.id == category_id)
        category = db.execute(stmt).scalar_one_or_none()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return CategoryResponse.model_validate(category)

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        stmt = select(Category).where(Category.id == category_id)
        category = db.execute(stmt).scalar_one_or_none()
        if category:
            db.delete(category)
            db.commit()
            return True
        return False

```


## ./services/__init__.py

```python

```

