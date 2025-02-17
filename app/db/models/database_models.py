from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    TIMESTAMP,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.database import Base


# ========================
# Users Table
# ========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    # Relationships
    agents = relationship("Agent", back_populates="owner")
    groups = relationship("UserGroup", back_populates="user")


# ========================
# Groups Table
# ========================
class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    # Relationships
    users = relationship("UserGroup", back_populates="group")
    agents = relationship("AgentGroup", back_populates="group")


# ========================
# User-Groups Junction Table
# ========================
class UserGroup(Base):
    __tablename__ = "user_groups"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    user = relationship("User", back_populates="groups")
    group = relationship("Group", back_populates="users")


# ========================
# Categories Table
# ========================
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")


# ========================
# Agents Table
# ========================
class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    prompt = Column(Text, nullable=False)
    is_public = Column(Boolean, default=False)
    owner_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    # Relationships
    owner = relationship("User", back_populates="agents")
    categories = relationship("AgentCategory", back_populates="agent")
    agent_files = relationship("AgentFile", back_populates="agent")
    agent_groups = relationship("AgentGroup", back_populates="agent")


# ========================
# Agent-Categories Junction Table
# ========================
class AgentCategory(Base):
    __tablename__ = "agent_categories"

    agent_id = Column(
        Integer, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True
    )
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    agent = relationship("Agent", back_populates="categories")


# ========================
# Agent-Groups Junction Table (Visibility Control)
# ========================
class AgentGroup(Base):
    __tablename__ = "agent_groups"

    agent_id = Column(
        Integer, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True
    )
    group_id = Column(
        Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
    )

    # Relationships
    agent = relationship("Agent", back_populates="agent_groups")  # 🔍 Corrected
    group = relationship("Group", back_populates="agents")


# ========================
# Agent-Files Table (RAG Files)
# ========================
class AgentFile(Base):
    __tablename__ = "agent_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(
        Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False
    )
    filename = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default="CURRENT_TIMESTAMP")

    # Relationships
    agent = relationship("Agent", back_populates="agent_files")

    # Constraints
    __table_args__ = (UniqueConstraint("agent_id", "filename", name="uix_agent_file"),)
