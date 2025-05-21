# app/db/models/database_models.py

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ───── Users ───────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    agents: Mapped[List["Agent"]] = relationship(
        "Agent", back_populates="owner", cascade="all, delete-orphan", passive_deletes=True
    )
    groups: Mapped[List["UserGroup"]] = relationship(
        "UserGroup", back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


# ───── Groups ──────────────────────────────────────────────────────────────────
class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    users: Mapped[List["UserGroup"]] = relationship(
        "UserGroup", back_populates="group", cascade="all, delete-orphan", passive_deletes=True
    )
    agents: Mapped[List["AgentGroup"]] = relationship(
        "AgentGroup", back_populates="group", cascade="all, delete-orphan", passive_deletes=True
    )


# ───── UserGroup ───────────────────────────────────────────────────────────────
class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True, index=True)

    user: Mapped["User"] = relationship("User", back_populates="groups")
    group: Mapped["Group"] = relationship("Group", back_populates="users")


# ───── Categories ─────────────────────────────────────────────────────────────
class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    agents: Mapped[List["AgentCategory"]] = relationship(
        "AgentCategory", back_populates="category", cascade="all, delete-orphan", passive_deletes=True
    )


# ───── Agents ─────────────────────────────────────────────────────────────────
class Agent(Base):
    __tablename__ = "agents"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_agent_owner_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, server_default=text("false"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    owner: Mapped["User"] = relationship("User", back_populates="agents")
    categories: Mapped[List["AgentCategory"]] = relationship(
        "AgentCategory", back_populates="agent", cascade="all, delete-orphan", passive_deletes=True
    )
    agent_files: Mapped[List["AgentFile"]] = relationship(
        "AgentFile", back_populates="agent", cascade="all, delete-orphan", passive_deletes=True
    )
    agent_groups: Mapped[List["AgentGroup"]] = relationship(
        "AgentGroup", back_populates="agent", cascade="all, delete-orphan", passive_deletes=True
    )


# ───── AgentCategory ──────────────────────────────────────────────────────────
class AgentCategory(Base):
    __tablename__ = "agent_categories"

    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True, index=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True, index=True
    )

    agent: Mapped["Agent"] = relationship("Agent", back_populates="categories")
    category: Mapped["Category"] = relationship("Category", back_populates="agents")


# ───── AgentGroup ─────────────────────────────────────────────────────────────
class AgentGroup(Base):
    __tablename__ = "agent_groups"

    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True, index=True)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="agent_groups")
    group: Mapped["Group"] = relationship("Group", back_populates="agents")


# ───── AgentFile ──────────────────────────────────────────────────────────────
class AgentFile(Base):
    __tablename__ = "agent_files"
    __table_args__ = (UniqueConstraint("agent_id", "filename", name="uix_agent_file"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    agent_id: Mapped[int] = mapped_column(ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    agent: Mapped["Agent"] = relationship("Agent", back_populates="agent_files")
