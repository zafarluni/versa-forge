from typing import List, Optional
from sqlalchemy import String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


# ========================
# Users Table
# ========================
class User(Base):
    """
    Represents a user in the system.
    - Each user can own multiple agents and belong to multiple groups.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    agents: Mapped[List["Agent"]] = relationship("Agent", back_populates="owner", cascade="all, delete-orphan")
    groups: Mapped[List["UserGroup"]] = relationship("UserGroup", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(username={self.username}, email={self.email})>"


# ========================
# Groups Table
# ========================
class Group(Base):
    """
    Represents a group in the system.
    - Groups are used to organize users and control agent visibility.
    """

    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    users: Mapped[List["UserGroup"]] = relationship("UserGroup", back_populates="group", cascade="all, delete-orphan")
    agents: Mapped[List["AgentGroup"]] = relationship(
        "AgentGroup", back_populates="group", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Group(name={self.name})>"


# ========================
# User-Groups Junction Table
# ========================
class UserGroup(Base):
    """
    Junction table for many-to-many relationship between Users and Groups.
    """

    __tablename__ = "user_groups"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True, index=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="groups")
    group: Mapped["Group"] = relationship("Group", back_populates="users")

    def __repr__(self) -> str:
        return f"<UserGroup(user_id={self.user_id}, group_id={self.group_id})>"


# ========================
# Categories Table
# ========================
class Category(Base):
    """
    Represents a category for organizing agents.
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    agents: Mapped[List["AgentCategory"]] = relationship(
        "AgentCategory", back_populates="category", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Category(name={self.name})>"


# ========================
# Agents Table
# ========================
class Agent(Base):
    """
    Represents an agent in the system.
    - Agents are owned by users and can be categorized or assigned to groups.
    """

    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="agents")
    categories: Mapped[List["AgentCategory"]] = relationship(
        "AgentCategory", back_populates="agent", cascade="all, delete-orphan"
    )
    agent_files: Mapped[List["AgentFile"]] = relationship(
        "AgentFile", back_populates="agent", cascade="all, delete-orphan"
    )
    agent_groups: Mapped[List["AgentGroup"]] = relationship(
        "AgentGroup", back_populates="agent", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Agent(name={self.name}, owner_id={self.owner_id})>"


# ========================
# Agent-Categories Junction Table
# ========================
class AgentCategory(Base):
    """
    Junction table for many-to-many relationship between Agents and Categories.
    """

    __tablename__ = "agent_categories"

    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True, index=True
    )

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="categories")
    category: Mapped["Category"] = relationship("Category", back_populates="agents")

    def __repr__(self) -> str:
        return f"<AgentCategory(agent_id={self.agent_id}, category_id={self.category_id})>"


# ========================
# Agent-Groups Junction Table (Visibility Control)
# ========================
class AgentGroup(Base):
    """
    Junction table for many-to-many relationship between Agents and Groups.
    - Controls which groups can access specific agents.
    """

    __tablename__ = "agent_groups"

    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True, index=True)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="agent_groups")
    group: Mapped["Group"] = relationship("Group", back_populates="agents")

    def __repr__(self) -> str:
        return f"<AgentGroup(agent_id={self.agent_id}, group_id={self.group_id})>"


# ========================
# Agent-Files Table (RAG Files)
# ========================
class AgentFile(Base):
    """
    Represents files associated with an agent for RAG (Retrieval-Augmented Generation).
    """

    __tablename__ = "agent_files"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    agent: Mapped["Agent"] = relationship("Agent", back_populates="agent_files")

    # Constraints
    __table_args__ = (UniqueConstraint("agent_id", "filename", name="uix_agent_file"),)

    def __repr__(self) -> str:
        return f"<AgentFile(filename={self.filename}, agent_id={self.agent_id})>"
