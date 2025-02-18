from sqlalchemy import (
    Column, Integer, String, Boolean, Text, DateTime, ForeignKey, UniqueConstraint, func
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
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    agents = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    groups = relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"

# ========================
# Groups Table
# ========================
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    users = relationship("UserGroup", back_populates="group", cascade="all, delete-orphan")
    agents = relationship("AgentGroup", back_populates="group", cascade="all, delete-orphan")

    def __repr__(self):
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

    def __repr__(self):
        return f"<UserGroup(user_id={self.user_id}, group_id={self.group_id})>"

# ========================
# Categories Table
# ========================
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    agents = relationship("AgentCategory", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
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
    is_public = Column(Boolean, server_default="false", nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    owner = relationship("User", back_populates="agents")
    categories = relationship("AgentCategory", back_populates="agent", cascade="all, delete-orphan")
    agent_files = relationship("AgentFile", back_populates="agent", cascade="all, delete-orphan")
    agent_groups = relationship("AgentGroup", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
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

    def __repr__(self):
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

    def __repr__(self):
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
    created_at = Column(DateTime, server_default=func.current_timestamp(), nullable=False)

    # Relationships
    agent = relationship("Agent", back_populates="agent_files")

    # Constraints
    __table_args__ = (UniqueConstraint("agent_id", "filename", name="uix_agent_file"),)

    def __repr__(self):
        return f"<AgentFile(filename={self.filename}, agent_id={self.agent_id})>"
